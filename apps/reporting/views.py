from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from reporting.services import KPIAggregationService


class ReportingIndexView(LoginRequiredMixin, TemplateView):
    template_name = "reporting/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kpis"] = KPIAggregationService.aggregate(user=self.request.user)
        return context
