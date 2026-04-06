from django.views.generic import TemplateView


class ReportingIndexView(TemplateView):
    template_name = "reporting/index.html"
