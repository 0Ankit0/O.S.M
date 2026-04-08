from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from core.access import DashboardStaffRequiredMixin
from delivery.models import DeliveryAssignment


class ActiveDeliveryListView(DashboardStaffRequiredMixin, ListView):
    template_name = "delivery/active_deliveries.html"
    context_object_name = "assignments"

    def get_queryset(self):
        return (
            DeliveryAssignment.objects.exclude(status=DeliveryAssignment.Status.DELIVERED)
            .exclude(status=DeliveryAssignment.Status.CANCELLED)
            .select_related("order", "assignee", "zone")
        )


class DeliveryDetailView(DashboardStaffRequiredMixin, DetailView):
    template_name = "delivery/detail.html"
    context_object_name = "assignment"
    model = DeliveryAssignment

    def get_object(self, queryset=None):
        queryset = DeliveryAssignment.objects.select_related("order", "assignee", "zone").prefetch_related("events__actor")
        return get_object_or_404(queryset, pk=self.kwargs["pk"])
