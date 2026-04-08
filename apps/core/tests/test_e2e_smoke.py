from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Category, Product
from delivery.models import DeliveryAssignment, DeliveryZone
from orders.models import Order

User = get_user_model()


class CustomerJourneySmokeTests(TestCase):
    @staticmethod
    def _create_user(email: str, *, is_superuser: bool = False):
        user = User.objects.create(email=email, username=email, is_superuser=is_superuser)
        user.set_password("password123")
        user.save(update_fields=["password"])
        return user

    def setUp(self):
        self.client = APIClient()
        self.customer = self._create_user("customer-smoke@example.com")
        self.category = Category.objects.create(name="Meals", slug="meals", active=True)
        self.product = Product.objects.create(
            category=self.category,
            name="Veg Burger",
            slug="veg-burger",
            price=Decimal("9.50"),
            active=True,
        )

    @patch("payments.services.payment_flow.GatewayBackedPaymentProviderAdapter")
    def test_catalog_to_checkout_to_payment_to_delivery_timeline(self, adapter_cls):
        adapter = adapter_cls.return_value
        adapter.create_payment_session.return_value = {
            "transaction_id": "txn_smoke_1",
            "payment_url": "https://example.test/payment/txn_smoke_1",
            "status": "pending",
        }
        adapter.confirm_payment.return_value = {"status": "completed", "transaction_id": "txn_smoke_1"}

        self.client.force_authenticate(self.customer)

        categories_url = reverse("catalog_api:category-list", host="api")
        categories_response = self.client.get(categories_url)
        self.assertEqual(categories_response.status_code, status.HTTP_200_OK)

        products_url = reverse("catalog_api:product-list", host="api")
        products_response = self.client.get(products_url)
        self.assertEqual(products_response.status_code, status.HTTP_200_OK)

        add_item_url = reverse("orders_api:cart-item-add", host="api")
        add_item_response = self.client.post(
            add_item_url,
            {"product_id": str(self.product.id), "quantity": 2},
            format="json",
        )
        self.assertEqual(add_item_response.status_code, status.HTTP_200_OK)

        checkout_url = reverse("orders_api:checkout", host="api")
        checkout_response = self.client.post(
            checkout_url,
            {
                "idempotency_key": "smoke-idem-1",
                "return_url": "https://example.test/return",
                "website_url": "https://example.test",
            },
            format="json",
        )
        self.assertEqual(checkout_response.status_code, status.HTTP_201_CREATED)
        order_id = checkout_response.data["id"]

        create_payment_url = reverse("payments_api:create-intent", host="api")
        create_payment_response = self.client.post(
            create_payment_url,
            {"order_id": order_id, "provider": "stripe", "return_url": "https://example.test/return"},
            format="json",
        )
        self.assertEqual(create_payment_response.status_code, status.HTTP_201_CREATED)
        payment_id = create_payment_response.data["id"]

        payment_status_url = reverse("payments_api:payment-status", kwargs={"payment_id": payment_id}, host="api")
        payment_response = self.client.get(f"{payment_status_url}?refresh=true")
        self.assertEqual(payment_response.status_code, status.HTTP_200_OK)

        order = Order.objects.get(id=order_id)
        self.assertEqual(order.payment_status, Order.PaymentStatus.COMPLETED)

        zone = DeliveryZone.objects.create(name="Smoke Zone", postcodes=["10101"], is_active=True)
        assignment = DeliveryAssignment.objects.create(
            order=order,
            zone=zone,
            eta_at=timezone.now() + timedelta(minutes=40),
        )

        timeline_url = reverse("delivery_api:order-timeline", kwargs={"order_id": order.id}, host="api")
        timeline_response = self.client.get(timeline_url)
        self.assertEqual(timeline_response.status_code, status.HTTP_200_OK)
        self.assertEqual(timeline_response.data["id"], assignment.id)


class DashboardVisibilitySmokeTests(TestCase):
    @staticmethod
    def _create_user(email: str, *, is_superuser: bool = False):
        user = User.objects.create(email=email, username=email, is_superuser=is_superuser)
        user.set_password("password123")
        user.save(update_fields=["password"])
        return user

    def setUp(self):
        self.client = APIClient()
        self.staff = self._create_user("staff-smoke@example.com", is_superuser=True)

    def test_staff_dashboard_sections_and_openapi_schema(self):
        self.client.force_login(self.staff)
        payments_response = self.client.get(reverse("payments:index", host="api"))
        delivery_response = self.client.get(reverse("delivery:index", host="api"))
        reporting_response = self.client.get(reverse("reporting:index", host="api"))

        self.assertEqual(payments_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delivery_response.status_code, status.HTTP_200_OK)
        self.assertEqual(reporting_response.status_code, status.HTTP_200_OK)

        schema_response = self.client.get(reverse("schema-json", kwargs={"format": ".json"}, host="api"))
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        schema_body = schema_response.content.decode("utf-8")
        self.assertIn("/api/orders/checkout/", schema_body)
        self.assertIn("/api/payments/intents/", schema_body)
        self.assertIn("/api/delivery/orders/{order_id}/timeline/", schema_body)
        self.assertIn("/api/reporting/exports/", schema_body)
