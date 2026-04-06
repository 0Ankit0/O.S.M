from django.views.generic import TemplateView


class PaymentsIndexView(TemplateView):
    template_name = "payments/index.html"
