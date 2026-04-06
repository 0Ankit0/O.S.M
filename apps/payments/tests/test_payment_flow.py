import hashlib
import hmac
import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Category, Product
from orders.models import Order
from orders.services import CheckoutService
from payments.models import PaymentTransaction, RefundRequest
from payments.services import request_refund

User = get_user_model()


@override_settings(PAYMENTS_WEBHOOK_SECRET="test-secret")
class PaymentWebhookIdempotencyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="payment-webhook@example.com", password="password123")
        category = Category.objects.create(name="Fruit", slug="fruit")
        self.product = Product.objects.create(category=category, name="Apple", slug="apple", price=Decimal("2.00"))
        from orders.services import CartService

        CartService.add_item(user=self.user, product=self.product, quantity=1)

        order, _, _ = CheckoutService.checkout(user=self.user, idempotency_key="pay-1")
        self.payment = PaymentTransaction.objects.create(
            order=order,
            provider=PaymentTransaction.Provider.STRIPE,
            status=PaymentTransaction.Status.PENDING,
            amount=order.subtotal,
            currency="NPR",
            provider_transaction_id="txn_123",
        )

    def _signed_headers(self, payload: dict):
        raw = json.dumps(payload).encode("utf-8")
        timestamp = str(int(timezone.now().timestamp()))
        signed_payload = f"{timestamp}.".encode("utf-8") + raw
        signature = hmac.new(settings.PAYMENTS_WEBHOOK_SECRET.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return raw, {"HTTP_X_PAYMENT_SIGNATURE": signature, "HTTP_X_PAYMENT_TIMESTAMP": timestamp}

    def test_duplicate_webhook_event_is_ignored(self):
        payload = {
            "id": "evt_1",
            "type": "payment.succeeded",
            "transaction_id": "txn_123",
            "status": "completed",
        }
        raw, headers = self._signed_headers(payload)

        url = reverse("payments_api:webhook", kwargs={"provider": "stripe"}, host="api")
        first = self.client.post(url, data=raw, content_type="application/json", **headers)
        second = self.client.post(url, data=raw, content_type="application/json", **headers)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertTrue(first.data["processed"])
        self.assertFalse(second.data["processed"])

    def test_stale_webhook_is_rejected(self):
        payload = {"id": "evt_2", "type": "payment.failed", "transaction_id": "txn_123", "status": "failed"}
        raw = json.dumps(payload).encode("utf-8")
        timestamp = str(int((timezone.now() - timedelta(minutes=10)).timestamp()))
        signed_payload = f"{timestamp}.".encode("utf-8") + raw
        signature = hmac.new(settings.PAYMENTS_WEBHOOK_SECRET.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

        url = reverse("payments_api:webhook", kwargs={"provider": "stripe"}, host="api")
        response = self.client.post(
            url,
            data=raw,
            content_type="application/json",
            HTTP_X_PAYMENT_SIGNATURE=signature,
            HTTP_X_PAYMENT_TIMESTAMP=timestamp,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentOutcomePropagationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="payment-outcome@example.com", password="password123")
        category = Category.objects.create(name="Meal", slug="meal")
        self.product = Product.objects.create(category=category, name="Pizza", slug="pizza", price=Decimal("15.00"))

    @patch("payments.services.payment_flow.GatewayBackedPaymentProviderAdapter")
    def test_payment_success_updates_order(self, adapter_cls):
        adapter = adapter_cls.return_value
        adapter.create_payment_session.return_value = {
            "transaction_id": "txn_succ",
            "payment_url": "https://example.com/pay",
            "status": "pending",
        }

        with patch("orders.services.payment.PaymentIntegrationService.available_gateways", return_value=["stripe"]):
            from orders.services import CartService

            CartService.add_item(user=self.user, product=self.product, quantity=1)
            order, _, _ = CheckoutService.checkout(
                user=self.user,
                gateway="stripe",
                return_url="https://example.com/return",
            )

        adapter.confirm_payment.return_value = {"status": "completed", "transaction_id": "txn_succ"}

        url = reverse("payments_api:payment-status", kwargs={"payment_id": order.payment_record.id}, host="api")
        self.client.force_authenticate(self.user)
        response = self.client.get(f"{url}?refresh=true")

        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.payment_status, Order.PaymentStatus.COMPLETED)
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    @patch("payments.services.payment_flow.GatewayBackedPaymentProviderAdapter")
    def test_payment_failure_updates_order(self, adapter_cls):
        adapter = adapter_cls.return_value
        adapter.create_payment_session.return_value = {
            "transaction_id": "txn_fail",
            "payment_url": "https://example.com/pay",
            "status": "pending",
        }

        with patch("orders.services.payment.PaymentIntegrationService.available_gateways", return_value=["stripe"]):
            from orders.services import CartService

            CartService.add_item(user=self.user, product=self.product, quantity=1)
            order, _, _ = CheckoutService.checkout(
                user=self.user,
                gateway="stripe",
                return_url="https://example.com/return",
            )

        adapter.confirm_payment.return_value = {"status": "failed", "transaction_id": "txn_fail"}

        url = reverse("payments_api:payment-status", kwargs={"payment_id": order.payment_record.id}, host="api")
        self.client.force_authenticate(self.user)
        self.client.get(f"{url}?refresh=true")

        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.FAILED)
        self.assertEqual(order.status, Order.Status.FAILED)


class RefundLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="refund@example.com", password="password123")
        category = Category.objects.create(name="Tech", slug="tech")
        product = Product.objects.create(category=category, name="Headphones", slug="headphones", price=Decimal("40.00"))

        from orders.services import CartService

        CartService.add_item(user=self.user, product=product, quantity=1)
        self.order, _, _ = CheckoutService.checkout(user=self.user, idempotency_key="refund-order")
        self.payment = PaymentTransaction.objects.create(
            order=self.order,
            provider=PaymentTransaction.Provider.STRIPE,
            status=PaymentTransaction.Status.COMPLETED,
            amount=self.order.subtotal,
            currency="NPR",
            provider_transaction_id="txn_refund",
        )

    @patch("payments.services.payment_flow.GatewayBackedPaymentProviderAdapter")
    def test_refund_request_lifecycle(self, adapter_cls):
        adapter = adapter_cls.return_value
        adapter.request_refund.return_value = {"refund_id": "rf_123", "status": "completed", "amount": "40.00"}

        refund = request_refund(
            payment=self.payment,
            amount=Decimal("40.00"),
            reason="Customer request",
            requested_by=self.user,
        )

        refund.refresh_from_db()
        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(refund.status, RefundRequest.Status.COMPLETED)
        self.assertEqual(self.payment.status, PaymentTransaction.Status.REFUNDED)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.REFUNDED)
