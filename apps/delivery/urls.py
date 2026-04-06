from django.urls import path

from .views import ActiveDeliveryListView, DeliveryDetailView

app_name = "delivery"

urlpatterns = [
    path("", ActiveDeliveryListView.as_view(), name="active-list"),
    path("<int:pk>/", DeliveryDetailView.as_view(), name="detail"),
]
