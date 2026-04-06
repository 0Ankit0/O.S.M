from django.views.generic import TemplateView


class AccountsIndexView(TemplateView):
    template_name = "accounts/index.html"
