from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AccountsIndexView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/index.html"


class AccountProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class AccountAddressPageView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/addresses.html"


class AccountPreferencesPageView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/preferences.html"
