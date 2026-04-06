from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models import Order, OrderStatusEvent


class OrderStatusTransitionService:
    ALLOWED_TRANSITIONS = {
        Order.Status.DRAFT: {Order.Status.PENDING_PAYMENT, Order.Status.CANCELLED, Order.Status.FAILED},
        Order.Status.PENDING_PAYMENT: {Order.Status.CONFIRMED, Order.Status.CANCELLED, Order.Status.FAILED},
        Order.Status.CONFIRMED: {Order.Status.FULFILLED, Order.Status.CANCELLED},
        Order.Status.FULFILLED: set(),
        Order.Status.CANCELLED: set(),
        Order.Status.FAILED: set(),
    }

    @classmethod
    @transaction.atomic
    def transition(cls, *, order: Order, new_status: str, note: str = ""):
        allowed_next = cls.ALLOWED_TRANSITIONS.get(order.status, set())
        if new_status not in allowed_next:
            raise ValidationError(f"Invalid transition from {order.status} to {new_status}.")

        if new_status == Order.Status.CONFIRMED and order.payment_status != Order.PaymentStatus.COMPLETED:
            raise ValidationError("Order cannot be confirmed until payment is completed.")

        previous = order.status
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

        OrderStatusEvent.objects.create(order=order, from_status=previous, to_status=new_status, note=note)
        return order
