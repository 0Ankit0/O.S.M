from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentRefreshStatusView,
    PaymentRefundCreateView,
    PaymentTransactionDetailView,
    PaymentTransactionListView,
    PaymentsIndexView,
)

app_name = "payments"

urlpatterns = [
    path("", PaymentsIndexView.as_view(), name="index"),
    path("transactions/", PaymentTransactionListView.as_view(), name="transactions"),
    path("create/", PaymentCreateView.as_view(), name="create"),
    path("transactions/<int:pk>/", PaymentTransactionDetailView.as_view(), name="detail"),
    path("transactions/<int:pk>/refresh/", PaymentRefreshStatusView.as_view(), name="refresh"),
    path("transactions/<int:pk>/refund/", PaymentRefundCreateView.as_view(), name="refund"),
]
