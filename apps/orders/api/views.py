from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Product
from orders.models import CartItem, Order
from orders.services import CartService, CheckoutService, PaymentIntegrationService

from .serializers import (
    CartAddItemSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    OrderSerializer,
)


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=serializer.validated_data["product_id"], active=True)
        CartService.add_item(
            user=request.user,
            product=product,
            quantity=serializer.validated_data["quantity"],
        )
        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemMutationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        CartService.update_item(user=request.user, product=item.product, quantity=serializer.validated_data["quantity"])
        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        CartService.remove_item(user=request.user, product=item.product)
        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gateway = serializer.validated_data.get("gateway")
        order, created, meta = CheckoutService.checkout(
            user=request.user,
            tenant=getattr(request, "tenant", None),
            idempotency_key=serializer.validated_data.get("idempotency_key"),
            gateway=gateway,
            return_url=serializer.validated_data.get("return_url"),
            website_url=serializer.validated_data.get("website_url"),
            payment_method_id=serializer.validated_data.get("payment_method_id"),
        )
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        payload = OrderDetailSerializer(order).data
        payload["payment"] = meta.get("payment")
        return Response(payload, status=http_status)


class PaymentGatewayConfigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"gateways": PaymentIntegrationService.available_gateways()}, status=status.HTTP_200_OK)


class OrderListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "status_events")
