from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..constants import TenantUserRole
from ..models import Tenant, TenantMembership
from ..notifications import TenantInvitationEmail, send_tenant_invitation_notification
from ..tokens import tenant_invitation_token

User = get_user_model()


def create_tenant_membership(
    tenant: Tenant,
    user: User = None,
    created_by: User = None,
    invitee_email_address: str = "",
    role: TenantUserRole = TenantUserRole.MEMBER,
    is_accepted: bool = False,
):
    membership = TenantMembership.objects.create(
        user=user,
        tenant=tenant,
        role=role,
        invitee_email_address=invitee_email_address,
        is_accepted=is_accepted,
        created_by=created_by,
    )
    if not is_accepted:
        token = tenant_invitation_token.make_token(
            user_email=invitee_email_address if invitee_email_address else user.email, tenant_membership=membership
        )
        # Use the membership ID directly instead of GraphQL global ID
        tenant_membership_id = str(membership.id)
        TenantInvitationEmail(
            to=user.email if user else invitee_email_address,
            data={"tenant_membership_id": tenant_membership_id, "token": token},
        ).send()

        if user:
            send_tenant_invitation_notification(membership, tenant_membership_id, token)

    return membership


@transaction.atomic
def accept_invitation(invitation: TenantMembership, actor):
    if invitation.user and invitation.user != actor:
        raise PermissionDenied("You do not have permission to accept this invitation.")
    if not invitation.user and invitation.invitee_email_address and invitation.invitee_email_address != actor.email and not actor.is_superuser:
        raise PermissionDenied("You do not have permission to accept this invitation.")
    if invitation.is_accepted:
        return {"detail": "Invitation already accepted."}

    invitation.user = actor
    invitation.is_accepted = True
    invitation.invitation_accepted_at = invitation.invitation_accepted_at or timezone.now()
    invitation.save(update_fields=["user", "is_accepted", "invitation_accepted_at", "updated_at"])
    return {"detail": "Invitation accepted.", "tenant_id": str(invitation.tenant_id)}


@transaction.atomic
def decline_invitation(invitation: TenantMembership, actor):
    can_manage = (
        actor.is_superuser
        or invitation.user_id == actor.id
        or invitation.created_by_id == actor.id
        or invitation.tenant.created_by_id == actor.id
        or invitation.invitee_email_address == actor.email
    )
    if not can_manage:
        raise PermissionDenied("You do not have permission to decline this invitation.")
    invitation.delete()
    return {"detail": "Invitation declined."}


@transaction.atomic
def delete_tenant_membership(membership: TenantMembership, actor):
    if membership.tenant.created_by_id != actor.id and membership.user_id != actor.id and not actor.is_superuser:
        raise PermissionDenied("You do not have permission to remove this membership.")
    if membership.role == TenantUserRole.OWNER:
        owners_count = membership.tenant.user_memberships.filter(role=TenantUserRole.OWNER, is_accepted=True).count()
        if owners_count <= 1:
            raise ValidationError("There must be at least one owner in the tenant.")
    membership.delete()
