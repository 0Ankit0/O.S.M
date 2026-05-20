from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, TemplateView
from core.mixins import RoleAwareBaseTemplateMixin

from . import constants, forms, models
from .services import membership as membership_service

User = get_user_model()


class TenantListView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, ListView):
    """List user's tenants."""
    template_name = 'tenants/list.html'
    context_object_name = 'memberships'
    login_url = reverse_lazy('iam:login')

    def get_queryset(self):
        return models.TenantMembership.objects.filter(
            user=self.request.user,
            tenant__is_active=True,
        ).select_related('tenant')


class TenantCreateView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    """Create a new tenant."""
    template_name = 'tenants/create.html'
    form_class = forms.TenantForm
    success_url = reverse_lazy('multitenancy:list')
    login_url = reverse_lazy('iam:login')

    def form_valid(self, form):
        tenant = models.Tenant.objects.create(
            name=form.cleaned_data['name'],
            type=constants.TenantType.ORGANIZATION,
            created_by=self.request.user,
        )
        models.TenantMembership.objects.create(
            user=self.request.user,
            tenant=tenant,
            role=constants.TenantUserRole.OWNER,
            is_accepted=True,
            invitee_email_address=self.request.user.email,
            created_by=self.request.user,
        )
        messages.success(self.request, f'Organization "{tenant.name}" created successfully!')
        return super().form_valid(form)


class TenantDetailView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, TemplateView):
    """Tenant detail view."""
    template_name = 'tenants/detail.html'
    login_url = reverse_lazy('iam:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant_id = self.kwargs.get('pk')

        membership = get_object_or_404(
            models.TenantMembership,
            tenant_id=tenant_id,
            user=self.request.user,
            tenant__is_active=True,
        )

        context['tenant'] = membership.tenant
        context['membership'] = membership
        context['members'] = models.TenantMembership.objects.get_all().filter(
            tenant=membership.tenant,
            tenant__is_active=True,
        ).select_related('user')
        context['invitation_form'] = forms.TenantInvitationForm()

        return context


class TenantInviteView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    """Invite a member to a tenant."""
    template_name = 'tenants/invite.html'
    form_class = forms.TenantInvitationForm
    login_url = reverse_lazy('iam:login')

    def get_success_url(self):
        return reverse('multitenancy:detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        tenant_id = self.kwargs.get('pk')
        membership = get_object_or_404(
            models.TenantMembership.objects.get_all(),
            tenant_id=tenant_id,
            user=self.request.user,
            is_accepted=True,
            tenant__is_active=True,
        )
        if membership.role not in {constants.TenantUserRole.OWNER, constants.TenantUserRole.ADMIN}:
            messages.error(self.request, 'You do not have permission to invite members to this organization.')
            return redirect('multitenancy:detail', pk=tenant_id)

        email = form.cleaned_data['email']
        role = form.cleaned_data['role']

        if models.TenantMembership.objects.get_all().filter(
            Q(user__email__iexact=email, tenant=membership.tenant) | Q(invitee_email_address__iexact=email, tenant=membership.tenant)
        ).exists():
            form.add_error('email', 'This user already belongs to the organization or already has a pending invitation.')
            return self.form_invalid(form)

        invited_user = User.objects.filter(email__iexact=email).first()

        membership_service.create_tenant_membership(
            tenant=membership.tenant,
            user=invited_user,
            invitee_email_address='' if invited_user else email,
            created_by=self.request.user,
            role=role,
            is_accepted=False,
        )

        messages.success(self.request, f'Invitation sent to {email}!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenant'] = get_object_or_404(models.Tenant, pk=self.kwargs.get('pk'), is_active=True)
        return context


@login_required
def switch_tenant(request, pk):
    tenant = get_object_or_404(models.Tenant, id=pk, is_active=True)
    if not models.TenantMembership.objects.filter(tenant=tenant, user=request.user, is_accepted=True).exists():
        messages.error(request, 'You are not a member of this tenant.')
        return redirect('core:dashboard')

    request.session['tenant_id'] = str(tenant.id)
    messages.success(request, f'Switched to {tenant.name}')
    return redirect('core:dashboard')


@login_required
def remove_tenant_member(request, pk, membership_id):
    if request.method != 'POST':
        return redirect('multitenancy:detail', pk=pk)

    acting_membership = get_object_or_404(
        models.TenantMembership.objects.get_all(),
        tenant_id=pk,
        user=request.user,
        role=constants.TenantUserRole.OWNER,
        is_accepted=True,
        tenant__is_active=True,
    )
    target_membership = get_object_or_404(
        models.TenantMembership.objects.get_all(),
        tenant_id=pk,
        pk=membership_id,
        tenant__is_active=True,
    )

    if target_membership.user_id == request.user.id:
        messages.error(request, 'Use another owner account before removing yourself from this organization.')
        return redirect('multitenancy:detail', pk=pk)

    membership_service.delete_tenant_membership(target_membership, request.user)
    target_label = target_membership.user.email if target_membership.user else target_membership.invitee_email_address
    messages.success(request, f'Removed {target_label} from {acting_membership.tenant.name}.')
    return redirect('multitenancy:detail', pk=pk)


@login_required
def delete_tenant(request, pk):
    if request.method != 'POST':
        return redirect('multitenancy:detail', pk=pk)

    membership = get_object_or_404(
        models.TenantMembership.objects.get_all(),
        tenant_id=pk,
        user=request.user,
        role=constants.TenantUserRole.OWNER,
        is_accepted=True,
        tenant__is_active=True,
    )
    tenant = membership.tenant

    if tenant.type == constants.TenantType.DEFAULT:
        messages.error(request, 'Your default personal organization cannot be deleted.')
        return redirect('multitenancy:detail', pk=pk)

    tenant_name = tenant.name
    tenant_id = str(tenant.id)
    for tenant_membership in models.TenantMembership.objects.get_all().filter(tenant=tenant):
        tenant_membership.delete(user=request.user)
    tenant.delete(user=request.user)
    if request.session.get('tenant_id') == tenant_id:
        request.session.pop('tenant_id', None)
    messages.success(request, f'Organization "{tenant_name}" deleted successfully.')
    return redirect('multitenancy:list')
