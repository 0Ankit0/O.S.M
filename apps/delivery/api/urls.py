from django.urls import path

from . import views

app_name = "delivery_api"

urlpatterns = [
    path("serviceability/", views.ServiceabilityCheckAPIView.as_view(), name="serviceability"),
    path("assignments/<int:assignment_id>/status/", views.AssignmentStatusUpdateAPIView.as_view(), name="assignment-status"),
    path("orders/<str:order_id>/timeline/", views.OrderDeliveryTimelineAPIView.as_view(), name="order-timeline"),
]
