from notifications.models import Notification


class DeliveryNotificationService:
    @staticmethod
    def send_out_for_delivery(*, assignment):
        Notification.objects.create(
            user=assignment.order.user,
            type="delivery.out_for_delivery",
            data={
                "order_id": str(assignment.order_id),
                "assignment_id": assignment.id,
                "status": assignment.status,
            },
            issuer=assignment.assignee,
        )

    @staticmethod
    def send_delivered(*, assignment):
        Notification.objects.create(
            user=assignment.order.user,
            type="delivery.delivered",
            data={
                "order_id": str(assignment.order_id),
                "assignment_id": assignment.id,
                "status": assignment.status,
            },
            issuer=assignment.assignee,
        )
