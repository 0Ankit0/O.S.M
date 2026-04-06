from iam.models import UserProfile
from notifications.models import NotificationPreference
from rest_framework import serializers

from accounts.models import AccountAddress


class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name"]


class AccountAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountAddress
        fields = [
            "id",
            "label",
            "line1",
            "line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ["id", "notification_type", "channel", "enabled"]
        read_only_fields = ["id"]


class NotificationPreferenceBulkUpdateSerializer(serializers.Serializer):
    preferences = NotificationPreferenceSerializer(many=True)
