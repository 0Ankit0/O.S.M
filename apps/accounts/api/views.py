from iam.models import UserProfile
from notifications.models import NotificationPreference
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import AccountAddress

from .serializers import (
    AccountAddressSerializer,
    AccountProfileSerializer,
    NotificationPreferenceBulkUpdateSerializer,
    NotificationPreferenceSerializer,
)


class AccountProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = AccountProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = AccountProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = AccountProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountAddressViewSet(viewsets.ModelViewSet):
    serializer_class = AccountAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AccountAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefs = NotificationPreference.objects.filter(user=request.user).order_by("notification_type", "channel")
        serializer = NotificationPreferenceSerializer(prefs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = NotificationPreferenceBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for pref in serializer.validated_data["preferences"]:
            NotificationPreference.objects.update_or_create(
                user=request.user,
                notification_type=pref["notification_type"],
                channel=pref["channel"],
                defaults={"enabled": pref["enabled"]},
            )

        updated = NotificationPreference.objects.filter(user=request.user).order_by("notification_type", "channel")
        return Response(NotificationPreferenceSerializer(updated, many=True).data, status=status.HTTP_200_OK)
