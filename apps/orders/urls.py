from django.urls import path

from .views import CartView, CheckoutView, OrderDetailView, OrderHistoryView, OrdersIndexView

app_name = "orders"

urlpatterns = [
    path("", OrdersIndexView.as_view(), name="index"),
    path("cart/", CartView.as_view(), name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("history/", OrderHistoryView.as_view(), name="history"),
    path("history/<str:pk>/", OrderDetailView.as_view(), name="detail"),
]
