from django.views.generic import TemplateView


class DeliveryIndexView(TemplateView):
    template_name = "delivery/index.html"
