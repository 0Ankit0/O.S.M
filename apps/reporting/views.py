from django.views.generic import TemplateView

from core.access import DashboardStaffRequiredMixin
from reporting.services import KPIAggregationService


class ReportingIndexView(DashboardStaffRequiredMixin, TemplateView):
    template_name = "reporting/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kpis"] = KPIAggregationService.aggregate(user=self.request.user)
        return context
