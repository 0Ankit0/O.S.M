from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models import Cart, Order, OrderItem, OrderStatusEvent
from orders.services.payment import PaymentIntegrationService


class CheckoutService:
    @staticmethod
    @transaction.atomic
    def checkout(
        *,
        user,
        tenant=None,
        idempotency_key: str | None = None,
        gateway: str | None = None,
        return_url: str | None = None,
        website_url: str | None = None,
        payment_method_id: str | None = None,
    ):
        if idempotency_key:
            existing = Order.objects.filter(user=user, idempotency_key=idempotency_key).first()
            if existing:
                return existing, False

        cart = Cart.objects.select_for_update().prefetch_related("items__product").filter(user=user).first()
        if not cart or not cart.items.exists():
            raise ValidationError("Cannot checkout an empty cart.")

        subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
        initial_status = Order.Status.PENDING_PAYMENT if gateway else Order.Status.CONFIRMED
        payment_status = Order.PaymentStatus.PENDING if gateway else Order.PaymentStatus.UNPAID

        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            idempotency_key=idempotency_key or None,
            status=initial_status,
            payment_status=payment_status,
            payment_gateway=gateway or "",
        )

        order_items = [
            OrderItem(order=order, product=item.product, quantity=item.quantity, unit_price=item.product.price)
            for item in cart.items.all()
        ]
        OrderItem.objects.bulk_create(order_items)

        OrderStatusEvent.objects.create(order=order, from_status="", to_status=initial_status, note="Checkout")

        if gateway:
            if not return_url:
                raise ValidationError("return_url is required when gateway checkout is requested.")
            transaction_record, gateway_result = PaymentIntegrationService.initiate_order_payment(
                order=order,
                tenant=tenant,
                user=user,
                gateway=gateway,
                return_url=return_url,
                website_url=website_url,
                payment_method_id=payment_method_id,
            )
            order.payment_transaction = transaction_record
            order.payment_status = transaction_record.status
            if transaction_record.status == "completed":
                order.status = Order.Status.CONFIRMED
                OrderStatusEvent.objects.create(
                    order=order,
                    from_status=Order.Status.PENDING_PAYMENT,
                    to_status=Order.Status.CONFIRMED,
                    note="Payment completed",
                )
            order.save(update_fields=["payment_transaction", "payment_status", "status", "updated_at"])
            response_meta = {"payment": gateway_result}
        else:
            response_meta = {"payment": None}

        cart.items.all().delete()
        return (order, True, response_meta)
