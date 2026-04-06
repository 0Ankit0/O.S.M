from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from accounts.models import AccountAddress
from notifications.models import NotificationPreference

User = get_user_model()


class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="owner@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other@example.com", password="password123")

    def test_endpoints_require_authentication(self):
        profile_url = reverse("accounts_api:profile", host="api")
        address_url = reverse("accounts_api:address-list", host="api")
        pref_url = reverse("accounts_api:notification-preferences", host="api")

        self.assertEqual(self.client.get(profile_url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(address_url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(pref_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_read_and_update(self):
        self.client.force_authenticate(self.user)
        profile_url = reverse("accounts_api:profile", host="api")

        read = self.client.get(profile_url)
        self.assertEqual(read.status_code, status.HTTP_200_OK)

        update = self.client.patch(profile_url, {"first_name": "Jane", "last_name": "Owner"}, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data["first_name"], "Jane")

    def test_address_validation(self):
        self.client.force_authenticate(self.user)
        address_url = reverse("accounts_api:address-list", host="api")

        response = self.client.post(
            address_url,
            {
                "label": "Home",
                "line1": "1 Main St",
                "city": "New York",
                "postal_code": "?",
                "country": "US",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("postal_code", response.data)

    def test_address_ownership_constraints(self):
        address = AccountAddress.objects.create(
            user=self.user,
            label="Home",
            line1="1 Main St",
            city="New York",
            postal_code="10001",
            country="US",
        )
        self.client.force_authenticate(self.other_user)

        detail_url = reverse("accounts_api:address-detail", kwargs={"pk": address.id}, host="api")
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_preferences_upsert_for_authenticated_user(self):
        NotificationPreference.objects.create(
            user=self.other_user,
            notification_type="order_update",
            channel=NotificationPreference.Channels.EMAIL,
            enabled=False,
        )
        self.client.force_authenticate(self.user)
        pref_url = reverse("accounts_api:notification-preferences", host="api")

        response = self.client.put(
            pref_url,
            {
                "preferences": [
                    {"notification_type": "order_update", "channel": "email", "enabled": True},
                    {"notification_type": "promo", "channel": "in_app", "enabled": False},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(NotificationPreference.objects.filter(user=self.user).count(), 2)
        self.assertEqual(NotificationPreference.objects.filter(user=self.other_user).count(), 1)
