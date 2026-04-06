from django.urls import path

from . import views

app_name = "orders_api"

urlpatterns = [
    path("cart/", views.CartAPIView.as_view(), name="cart"),
    path("cart/items/", views.CartItemCreateAPIView.as_view(), name="cart-item-add"),
    path("cart/items/<str:item_id>/", views.CartItemMutationAPIView.as_view(), name="cart-item-mutation"),
    path("checkout/", views.CheckoutAPIView.as_view(), name="checkout"),
    path("checkout/gateways/", views.PaymentGatewayConfigAPIView.as_view(), name="checkout-gateways"),
    path("orders/", views.OrderListAPIView.as_view(), name="order-list"),
    path("orders/<str:pk>/", views.OrderDetailAPIView.as_view(), name="order-detail"),
]
