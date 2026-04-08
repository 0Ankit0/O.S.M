from django.contrib.auth import get_user_model
from django.test import TestCase
from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient

from multitenancy import constants
from multitenancy.models import Tenant, TenantMembership

User = get_user_model()


class TenantInvitationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create(email="owner-invite@example.com", username="owner-invite@example.com")
        self.owner.set_password("password123")
        self.owner.save(update_fields=["password"])

        self.invitee = User.objects.create(email="invitee@example.com", username="invitee@example.com")
        self.invitee.set_password("password123")
        self.invitee.save(update_fields=["password"])
        self.other_user = User.objects.create(email="other@example.com", username="other@example.com")
        self.other_user.set_password("password123")
        self.other_user.save(update_fields=["password"])

        self.tenant = Tenant.objects.create(name="Tenant A", type=constants.TenantType.DEFAULT, created_by=self.owner)
        TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.owner,
            role=constants.TenantUserRole.OWNER,
            is_accepted=True,
            created_by=self.owner,
            invitee_email_address=self.owner.email,
        )
        self.invitation = TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.invitee,
            role=constants.TenantUserRole.MEMBER,
            is_accepted=False,
            created_by=self.owner,
            invitee_email_address=self.invitee.email,
        )

    def test_accept_invitation_endpoint(self):
        self.client.force_authenticate(self.invitee)
        url = reverse("multitenancy_api:invitation-accept", kwargs={"pk": self.invitation.id}, host="api")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.is_accepted)

    def test_other_user_cannot_accept_invitation(self):
        self.client.force_authenticate(self.other_user)
        url = reverse("multitenancy_api:invitation-accept", kwargs={"pk": self.invitation.id}, host="api")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_invitation_endpoint(self):
        self.client.force_authenticate(self.invitee)
        url = reverse("multitenancy_api:invitation-decline", kwargs={"pk": self.invitation.id}, host="api")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TenantMembership.objects.get_all().filter(pk=self.invitation.pk).exists())
