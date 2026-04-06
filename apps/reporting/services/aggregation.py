from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.utils import timezone

from delivery.models import DeliveryAssignment
from orders.models import Order


class KPIAggregationService:
    @staticmethod
    def aggregate(*, user=None):
        orders = Order.objects.all()
        if user and not user.is_superuser:
            orders = orders.filter(user=user)

        total_orders = orders.exclude(status=Order.Status.DRAFT).count()
        revenue = orders.exclude(status__in=[Order.Status.DRAFT, Order.Status.CANCELLED]).aggregate(
            value=Sum("subtotal")
        )["value"] or Decimal("0.00")

        refundable = orders.filter(payment_status__in=[Order.PaymentStatus.COMPLETED, Order.PaymentStatus.REFUNDED]).count()
        refunded = orders.filter(payment_status=Order.PaymentStatus.REFUNDED).count()
        refund_rate = float(refunded / refundable) if refundable else 0.0

        assignments = DeliveryAssignment.objects.filter(status=DeliveryAssignment.Status.DELIVERED)
        if user and not user.is_superuser:
            assignments = assignments.filter(order__user=user)

        sla_counts = assignments.aggregate(
            total=Count("id"),
            on_time=Count("id", filter=Q(updated_at__lte=F("eta_at"))),
        )
        delivery_sla = float(sla_counts["on_time"] / sla_counts["total"]) if sla_counts["total"] else 0.0

        return {
            "orders": total_orders,
            "revenue": f"{revenue:.2f}",
            "refund_rate": round(refund_rate, 4),
            "delivery_sla": round(delivery_sla, 4),
            "generated_at": timezone.now().isoformat(),
        }
