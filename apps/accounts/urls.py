from django.urls import path

from .views import (
    AccountAddressPageView,
    AccountPreferencesPageView,
    AccountProfilePageView,
    AccountsIndexView,
)

app_name = "accounts"

urlpatterns = [
    path("", AccountsIndexView.as_view(), name="index"),
    path("profile/", AccountProfilePageView.as_view(), name="profile"),
    path("addresses/", AccountAddressPageView.as_view(), name="addresses"),
    path("preferences/", AccountPreferencesPageView.as_view(), name="preferences"),
]
