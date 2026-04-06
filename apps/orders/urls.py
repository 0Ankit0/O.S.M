from django.urls import path

from .views import OrdersIndexView

app_name = "orders"

urlpatterns = [
    path("", OrdersIndexView.as_view(), name="index"),
]
