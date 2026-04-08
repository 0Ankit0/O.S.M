from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin, UserPassesTestMixin
from rest_framework.permissions import BasePermission, IsAuthenticated


class DashboardStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict dashboard views to staff users."""

    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)


class CustomerAccessRequiredMixin(LoginRequiredMixin, AccessMixin):
    """Restrict customer views to non-staff authenticated users."""

    permission_denied_message = "This section is available to customer accounts only."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IsDashboardStaff(IsAuthenticated):
    """DRF permission class for dashboard/staff APIs."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and bool(request.user and request.user.is_staff)


class IsCustomerUser(BasePermission):
    """DRF permission class for authenticated non-staff users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_staff)
