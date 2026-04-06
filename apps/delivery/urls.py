from django.urls import path

from .views import DeliveryIndexView

app_name = "delivery"

urlpatterns = [
    path("", DeliveryIndexView.as_view(), name="index"),
]
