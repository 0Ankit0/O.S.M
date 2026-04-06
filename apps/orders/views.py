from django.views.generic import TemplateView


class OrdersIndexView(TemplateView):
    template_name = "orders/index.html"
