from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Category, Product
from orders.services import CartService

User = get_user_model()


class CheckoutAndPaymentEdgeCaseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="edge-user@example.com", username="edge-user@example.com")
        self.user.set_password("password123")
        self.user.save(update_fields=["password"])

        category = Category.objects.create(name="Edge", slug="edge", active=True)
        self.product = Product.objects.create(category=category, name="Edge Product", slug="edge-product", price=Decimal("5.00"))
        self.client.force_authenticate(self.user)

    def test_checkout_requires_return_url_when_gateway_selected(self):
        CartService.add_item(user=self.user, product=self.product, quantity=1)

        response = self.client.post(
            reverse("orders_api:checkout", host="api"),
            {"gateway": "stripe", "idempotency_key": "edge-idem"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("return_url", response.data["detail"])

    @patch("payments.services.payment_flow.GatewayBackedPaymentProviderAdapter")
    def test_create_payment_conflict_when_payment_already_exists(self, adapter_cls):
        adapter = adapter_cls.return_value
        adapter.create_payment_session.return_value = {
            "transaction_id": "txn_edge_1",
            "payment_url": "https://example.test/pay",
            "status": "pending",
        }

        CartService.add_item(user=self.user, product=self.product, quantity=1)
        checkout = self.client.post(
            reverse("orders_api:checkout", host="api"),
            {"gateway": "stripe", "idempotency_key": "edge-idem-2", "return_url": "https://example.test/return"},
            format="json",
        )
        self.assertEqual(checkout.status_code, status.HTTP_201_CREATED)

        order_id = checkout.data["id"]
        response = self.client.post(
            reverse("payments_api:create-intent", host="api"),
            {"order_id": order_id, "provider": "stripe", "return_url": "https://example.test/return"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
