from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "accounts_api"

router = DefaultRouter()
router.register(r"addresses", views.AccountAddressViewSet, basename="address")

urlpatterns = [
    path("profile/", views.AccountProfileView.as_view(), name="profile"),
    path("notification-preferences/", views.NotificationPreferenceView.as_view(), name="notification-preferences"),
]

urlpatterns += router.urls
