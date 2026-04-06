from django.core.exceptions import ValidationError
from django.db import transaction

from delivery.models import DeliveryAssignment, DeliveryEvent, DeliveryZone
from delivery.services.notifications import DeliveryNotificationService


class DeliveryServiceabilityService:
    @staticmethod
    def normalize_postcode(postcode: str) -> str:
        return (postcode or "").replace(" ", "").upper()

    @classmethod
    def get_matching_zone(cls, *, postcode: str):
        normalized = cls.normalize_postcode(postcode)
        for zone in DeliveryZone.objects.filter(is_active=True):
            normalized_zone_postcodes = [cls.normalize_postcode(value) for value in zone.postcodes]
            if normalized in normalized_zone_postcodes:
                return zone
        return None

    @classmethod
    def is_serviceable(cls, *, postcode: str) -> tuple[bool, DeliveryZone | None]:
        zone = cls.get_matching_zone(postcode=postcode)
        return (zone is not None, zone)


class DeliveryAssignmentService:
    @staticmethod
    def create_or_update_assignment(*, order, zone, assignee=None, eta_at=None):
        assignment, _ = DeliveryAssignment.objects.get_or_create(
            order=order,
            defaults={"zone": zone, "assignee": assignee, "eta_at": eta_at},
        )
        changed_fields = []
        if assignment.zone_id != zone.id:
            assignment.zone = zone
            changed_fields.append("zone")
        if assignment.assignee_id != getattr(assignee, "id", None):
            assignment.assignee = assignee
            changed_fields.append("assignee")
        if assignment.eta_at != eta_at:
            assignment.eta_at = eta_at
            changed_fields.append("eta_at")

        if changed_fields:
            changed_fields.append("updated_at")
            assignment.save(update_fields=changed_fields)
        return assignment


class DeliveryTransitionService:
    ALLOWED_TRANSITIONS = {
        DeliveryAssignment.Status.ASSIGNED: {
            DeliveryAssignment.Status.PICKED_UP,
            DeliveryAssignment.Status.CANCELLED,
            DeliveryAssignment.Status.FAILED,
        },
        DeliveryAssignment.Status.PICKED_UP: {
            DeliveryAssignment.Status.OUT_FOR_DELIVERY,
            DeliveryAssignment.Status.CANCELLED,
            DeliveryAssignment.Status.FAILED,
        },
        DeliveryAssignment.Status.OUT_FOR_DELIVERY: {
            DeliveryAssignment.Status.DELIVERED,
            DeliveryAssignment.Status.FAILED,
        },
        DeliveryAssignment.Status.DELIVERED: set(),
        DeliveryAssignment.Status.FAILED: set(),
        DeliveryAssignment.Status.CANCELLED: set(),
    }

    @classmethod
    @transaction.atomic
    def transition(cls, *, assignment: DeliveryAssignment, to_status: str, actor=None, note: str = ""):
        allowed = cls.ALLOWED_TRANSITIONS.get(assignment.status, set())
        if to_status not in allowed:
            raise ValidationError(f"Invalid transition from {assignment.status} to {to_status}.")

        from_status = assignment.status
        assignment.status = to_status
        assignment.save(update_fields=["status", "updated_at"])

        DeliveryEvent.objects.create(
            assignment=assignment,
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            note=note,
        )

        if to_status == DeliveryAssignment.Status.OUT_FOR_DELIVERY:
            DeliveryNotificationService.send_out_for_delivery(assignment=assignment)
        elif to_status == DeliveryAssignment.Status.DELIVERED:
            DeliveryNotificationService.send_delivered(assignment=assignment)

        return assignment
