from rest_framework import serializers

from delivery.models import DeliveryAssignment, DeliveryEvent


class ServiceabilitySerializer(serializers.Serializer):
    postcode = serializers.CharField(max_length=20)


class AssignmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=DeliveryAssignment.Status.choices)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)


class DeliveryEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)

    class Meta:
        model = DeliveryEvent
        fields = ["id", "from_status", "to_status", "note", "actor_email", "created_at"]


class DeliveryTimelineSerializer(serializers.ModelSerializer):
    events = DeliveryEventSerializer(many=True, read_only=True)

    class Meta:
        model = DeliveryAssignment
        fields = ["id", "order", "assignee", "eta_at", "status", "events", "created_at", "updated_at"]
