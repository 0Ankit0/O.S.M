from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from delivery.models import DeliveryAssignment


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ActiveDeliveryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = "delivery/active_deliveries.html"
    context_object_name = "assignments"

    def get_queryset(self):
        return (
            DeliveryAssignment.objects.exclude(status=DeliveryAssignment.Status.DELIVERED)
            .exclude(status=DeliveryAssignment.Status.CANCELLED)
            .select_related("order", "assignee", "zone")
        )


class DeliveryDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    template_name = "delivery/detail.html"
    context_object_name = "assignment"
    model = DeliveryAssignment

    def get_object(self, queryset=None):
        queryset = DeliveryAssignment.objects.select_related("order", "assignee", "zone").prefetch_related("events__actor")
        return get_object_or_404(queryset, pk=self.kwargs["pk"])
