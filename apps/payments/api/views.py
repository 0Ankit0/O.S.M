from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from payments.models import PaymentTransaction
from payments.services import confirm_payment, create_payment_for_order, process_webhook, request_refund

from .serializers import CreatePaymentSerializer, PaymentStatusSerializer, RefundCreateSerializer, RefundRequestSerializer


class CreatePaymentIntentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create payment intent",
        request_body=CreatePaymentSerializer,
        responses={201: PaymentStatusSerializer},
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data["order_id"], user=request.user)
        if hasattr(order, "payment_record"):
            return Response({"detail": "Payment already exists for this order."}, status=status.HTTP_409_CONFLICT)
        try:
            payment = create_payment_for_order(
                order=order,
                user=request.user,
                provider=serializer.validated_data["provider"],
                return_url=serializer.validated_data["return_url"],
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentStatusSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get payment status", responses={200: PaymentStatusSerializer})
    def get(self, request, payment_id):
        payment = get_object_or_404(PaymentTransaction, id=payment_id, order__user=request.user)
        refresh = request.query_params.get("refresh") == "true"
        if refresh:
            payment = confirm_payment(payment=payment)
        return Response(PaymentStatusSerializer(payment).data)


class RefundCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create refund request",
        request_body=RefundCreateSerializer,
        responses={201: RefundRequestSerializer},
    )
    def post(self, request):
        serializer = RefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(PaymentTransaction, id=serializer.validated_data["payment_id"], order__user=request.user)
        try:
            refund = request_refund(
                payment=payment,
                amount=serializer.validated_data["amount"],
                reason=serializer.validated_data.get("reason", ""),
                requested_by=request.user,
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundRequestSerializer(refund).data, status=status.HTTP_201_CREATED)


class PaymentWebhookReceiverAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(operation_summary="Receive provider webhook", responses={200: "Webhook accepted"})
    def post(self, request, provider):
        signature = request.headers.get("X-Payment-Signature", "")
        timestamp = request.headers.get("X-Payment-Timestamp", "0")
        try:
            event, created = process_webhook(
                provider=provider,
                payload=request.data,
                raw_payload=request.body,
                signature=signature,
                timestamp=timestamp,
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"event_id": event.event_id, "processed": created},
            status=status.HTTP_200_OK,
        )
