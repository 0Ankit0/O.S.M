from __future__ import annotations

from datetime import timedelta, timezone as dt_timezone

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderStatusEvent

from payments.models import PaymentTransaction, PaymentWebhookEvent, RefundRequest
from payments.services.providers import GatewayBackedPaymentProviderAdapter


WEBHOOK_REPLAY_TOLERANCE = timedelta(minutes=5)


def _apply_payment_outcome_to_order(*, order: Order, payment_status: str, note: str):
    changed_fields = ["payment_status", "updated_at"]

    if payment_status == PaymentTransaction.Status.COMPLETED:
        order.payment_status = Order.PaymentStatus.COMPLETED
        if order.status == Order.Status.PENDING_PAYMENT:
            old = order.status
            order.status = Order.Status.CONFIRMED
            OrderStatusEvent.objects.create(order=order, from_status=old, to_status=order.status, note=note)
            changed_fields.append("status")
    elif payment_status == PaymentTransaction.Status.FAILED:
        order.payment_status = Order.PaymentStatus.FAILED
        if order.status in {Order.Status.DRAFT, Order.Status.PENDING_PAYMENT}:
            old = order.status
            order.status = Order.Status.FAILED
            OrderStatusEvent.objects.create(order=order, from_status=old, to_status=order.status, note=note)
            changed_fields.append("status")
    elif payment_status == PaymentTransaction.Status.REFUNDED:
        order.payment_status = Order.PaymentStatus.REFUNDED
    else:
        order.payment_status = Order.PaymentStatus.PENDING

    order.save(update_fields=changed_fields)


@transaction.atomic
def create_payment_for_order(*, order: Order, user, provider: str, return_url: str, currency: str = "NPR") -> PaymentTransaction:
    if hasattr(order, "payment_record"):
        raise ValidationError("Payment already exists for this order.")

    adapter = GatewayBackedPaymentProviderAdapter(provider)
    result = adapter.create_payment_session(
        amount=float(order.subtotal),
        currency=currency,
        metadata={
            "purchase_order_id": str(order.id),
            "purchase_order_name": f"Order #{order.id}",
            "return_url": return_url,
            "customer_info": {"customer_email": user.email, "customer_name": user.username},
        },
    )

    payment = PaymentTransaction.objects.create(
        order=order,
        provider=provider,
        status=result.get("status", PaymentTransaction.Status.PENDING),
        amount=order.subtotal,
        currency=currency,
        provider_transaction_id=result["transaction_id"],
        payment_url=result.get("payment_url", ""),
        provider_response=result,
        created_by=user,
    )

    order.payment_status = Order.PaymentStatus.PENDING
    if order.status == Order.Status.DRAFT:
        old = order.status
        order.status = Order.Status.PENDING_PAYMENT
        OrderStatusEvent.objects.create(order=order, from_status=old, to_status=order.status, note="Payment created")
        order.save(update_fields=["payment_status", "status", "updated_at"])
    else:
        order.save(update_fields=["payment_status", "updated_at"])

    return payment


@transaction.atomic
def confirm_payment(*, payment: PaymentTransaction) -> PaymentTransaction:
    adapter = GatewayBackedPaymentProviderAdapter(payment.provider)
    result = adapter.confirm_payment(provider_transaction_id=payment.provider_transaction_id)

    status = result.get("status", PaymentTransaction.Status.PENDING)
    payment.status = status
    payment.provider_response = result
    payment.save(update_fields=["status", "provider_response", "updated_at"])

    _apply_payment_outcome_to_order(order=payment.order, payment_status=status, note="Payment confirmation update")
    return payment


@transaction.atomic
def request_refund(*, payment: PaymentTransaction, amount, reason: str, requested_by) -> RefundRequest:
    if payment.status != PaymentTransaction.Status.COMPLETED:
        raise ValidationError("Only completed payments can be refunded.")

    refund = RefundRequest.objects.create(
        payment_transaction=payment,
        amount=amount,
        reason=reason,
        status=RefundRequest.Status.PROCESSING,
        requested_by=requested_by,
    )

    adapter = GatewayBackedPaymentProviderAdapter(payment.provider)
    result = adapter.request_refund(provider_transaction_id=payment.provider_transaction_id, amount=float(amount))

    refund.status = (
        RefundRequest.Status.COMPLETED
        if result.get("status") in {"completed", "refunded"}
        else RefundRequest.Status.FAILED
    )
    refund.provider_refund_id = result.get("refund_id", "")
    refund.provider_response = result
    refund.save(update_fields=["status", "provider_refund_id", "provider_response", "updated_at"])

    if refund.status == RefundRequest.Status.COMPLETED:
        payment.status = PaymentTransaction.Status.REFUNDED
        payment.save(update_fields=["status", "updated_at"])
        _apply_payment_outcome_to_order(order=payment.order, payment_status=PaymentTransaction.Status.REFUNDED, note="Refund completed")

    return refund


@transaction.atomic
def process_webhook(*, provider: str, payload: dict, raw_payload: bytes, signature: str, timestamp: str) -> tuple[PaymentWebhookEvent, bool]:
    if abs(timezone.now() - timezone.datetime.fromtimestamp(int(timestamp), tz=dt_timezone.utc)) > WEBHOOK_REPLAY_TOLERANCE:
        raise ValidationError("Stale webhook timestamp.")

    adapter = GatewayBackedPaymentProviderAdapter(provider)
    if not adapter.verify_webhook_signature(payload=raw_payload, signature=signature, timestamp=timestamp):
        raise ValidationError("Invalid webhook signature.")

    event_data = adapter.parse_webhook_event(payload=payload)
    event, created = PaymentWebhookEvent.objects.get_or_create(
        provider=provider,
        event_id=event_data["event_id"],
        defaults={
            "event_type": event_data["event_type"],
            "signature": signature,
            "payload": payload,
        },
    )

    if not created:
        return event, False

    event.process_attempts += 1

    provider_txn_id = event_data.get("provider_transaction_id")
    if provider_txn_id:
        payment = PaymentTransaction.objects.filter(provider_transaction_id=provider_txn_id, provider=provider).first()
        if payment:
            payment.status = event_data.get("status", payment.status)
            payment.provider_response = event_data.get("raw", payload)
            payment.save(update_fields=["status", "provider_response", "updated_at"])
            _apply_payment_outcome_to_order(
                order=payment.order,
                payment_status=payment.status,
                note=f"Webhook {event.event_type}",
            )

    event.processed = True
    event.processed_at = timezone.now()
    event.save(update_fields=["process_attempts", "processed", "processed_at"])
    return event, True
