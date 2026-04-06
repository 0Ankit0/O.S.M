from django.urls import path

from . import views

app_name = "payments_api"

urlpatterns = [
    path("intents/", views.CreatePaymentIntentAPIView.as_view(), name="create-intent"),
    path("<int:payment_id>/status/", views.PaymentStatusAPIView.as_view(), name="payment-status"),
    path("refunds/", views.RefundCreateAPIView.as_view(), name="refund-create"),
    path("webhooks/<str:provider>/", views.PaymentWebhookReceiverAPIView.as_view(), name="webhook"),
]
