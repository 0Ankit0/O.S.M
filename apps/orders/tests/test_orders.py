from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Category, Product
from orders.models import Order
from orders.services import CartService, CheckoutService, OrderStatusTransitionService

User = get_user_model()


class CartServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="cart@example.com", password="password123")
        category = Category.objects.create(name="Food", slug="food")
        self.product = Product.objects.create(category=category, name="Burger", slug="burger", price=Decimal("12.50"))

    def test_cart_math_updates(self):
        CartService.add_item(user=self.user, product=self.product, quantity=2)
        cart = self.user.cart

        self.assertEqual(cart.total_quantity, 2)
        self.assertEqual(cart.subtotal, Decimal("25.00"))

    def test_cart_quantity_validation(self):
        with self.assertRaises(ValidationError):
            CartService.update_item(user=self.user, product=self.product, quantity=-1)


class CheckoutIdempotencyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="checkout@example.com", password="password123")
        category = Category.objects.create(name="Drinks", slug="drinks")
        self.product = Product.objects.create(category=category, name="Cola", slug="cola", price=Decimal("4.00"))

    def test_checkout_idempotency_returns_existing_order(self):
        CartService.add_item(user=self.user, product=self.product, quantity=1)
        first_order, first_created, _ = CheckoutService.checkout(user=self.user, idempotency_key="idem-1")

        CartService.add_item(user=self.user, product=self.product, quantity=1)
        second_order, second_created, _ = CheckoutService.checkout(user=self.user, idempotency_key="idem-1")

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first_order.id, second_order.id)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)


class OrderPermissionsAndTransitionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="owner@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other@example.com", password="password123")
        category = Category.objects.create(name="Dessert", slug="dessert")
        self.product = Product.objects.create(category=category, name="Cake", slug="cake", price=Decimal("8.00"))

        CartService.add_item(user=self.user, product=self.product, quantity=1)
        self.order, _, _ = CheckoutService.checkout(user=self.user, idempotency_key="owner-order")

    def test_order_detail_only_for_owner(self):
        self.client.force_authenticate(self.other_user)

        url = reverse("orders_api:order-detail", kwargs={"pk": self.order.id}, host="api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_state_transition_rules(self):
        self.order.payment_status = Order.PaymentStatus.COMPLETED
        self.order.status = Order.Status.PENDING_PAYMENT
        self.order.save(update_fields=["payment_status", "status"])

        updated = OrderStatusTransitionService.transition(order=self.order, new_status=Order.Status.CONFIRMED)
        self.assertEqual(updated.status, Order.Status.CONFIRMED)

        with self.assertRaises(ValidationError):
            OrderStatusTransitionService.transition(order=self.order, new_status=Order.Status.DRAFT)

    def test_checkout_endpoint_idempotency(self):
        self.client.force_authenticate(self.user)
        CartService.add_item(user=self.user, product=self.product, quantity=2)

        url = reverse("orders_api:checkout", host="api")
        payload = {"idempotency_key": "idem-api"}

        first = self.client.post(url, payload, format="json")
        CartService.add_item(user=self.user, product=self.product, quantity=1)
        second = self.client.post(url, payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])


class CheckoutPaymentIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="payment@example.com", password="password123")
        category = Category.objects.create(name="Snack", slug="snack")
        self.product = Product.objects.create(category=category, name="Chips", slug="chips", price=Decimal("3.50"))

    @patch("orders.services.checkout.PaymentIntegrationService.initiate_order_payment")
    def test_checkout_with_gateway_creates_pending_payment_order(self, mock_initiate):
        CartService.add_item(user=self.user, product=self.product, quantity=3)

        mock_initiate.return_value = (
            None,
            {
                "transaction_id": "pi_test_123",
                "payment_url": "https://checkout.stripe.com/pay/cs_test",
                "status": "pending",
            },
        )

        order, created, meta = CheckoutService.checkout(
            user=self.user,
            tenant=object(),
            idempotency_key="stripe-checkout-1",
            gateway="stripe",
            return_url="https://example.com/payment/return",
            website_url="https://example.com",
        )

        self.assertTrue(created)
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(meta["payment"]["transaction_id"], "pi_test_123")
