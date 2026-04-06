from django.views.generic import TemplateView


class CatalogIndexView(TemplateView):
    template_name = "catalog/index.html"
