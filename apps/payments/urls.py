from django.urls import path

from .views import PaymentsIndexView

app_name = "payments"

urlpatterns = [
    path("", PaymentsIndexView.as_view(), name="index"),
]
