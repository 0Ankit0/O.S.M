from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from delivery.models import DeliveryAssignment, DeliveryZone
from delivery.services import DeliveryServiceabilityService, DeliveryTransitionService
from orders.models import Order

User = get_user_model()


class DeliveryServiceabilityTests(TestCase):
    def setUp(self):
        self.zone = DeliveryZone.objects.create(name="Central", postcodes=["10001", "10002"], is_active=True)

    def test_zone_matching_ignores_whitespace_and_case(self):
        serviceable, zone = DeliveryServiceabilityService.is_serviceable(postcode=" 10001 ")

        self.assertTrue(serviceable)
        self.assertEqual(zone.id, self.zone.id)


class DeliveryTransitionTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email="customer@example.com", password="password123")
        self.rider = User.objects.create_user(email="rider@example.com", password="password123")
        self.zone = DeliveryZone.objects.create(name="North", postcodes=["20001"])
        self.order = Order.objects.create(user=self.customer, status=Order.Status.CONFIRMED)
        self.assignment = DeliveryAssignment.objects.create(
            order=self.order,
            zone=self.zone,
            assignee=self.rider,
            eta_at=timezone.now() + timedelta(minutes=45),
        )

    def test_valid_transition(self):
        assignment = DeliveryTransitionService.transition(
            assignment=self.assignment,
            to_status=DeliveryAssignment.Status.PICKED_UP,
            actor=self.rider,
        )
        self.assertEqual(assignment.status, DeliveryAssignment.Status.PICKED_UP)
        self.assertEqual(assignment.events.count(), 1)

    def test_invalid_transition_raises_error(self):
        with self.assertRaises(ValidationError):
            DeliveryTransitionService.transition(
                assignment=self.assignment,
                to_status=DeliveryAssignment.Status.DELIVERED,
                actor=self.rider,
            )


class DeliveryPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email="timeline@example.com", password="password123")
        self.rider = User.objects.create_user(email="rider2@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other@example.com", password="password123")
        self.staff = User.objects.create_user(email="staff@example.com", password="password123", is_staff=True)

        self.zone = DeliveryZone.objects.create(name="South", postcodes=["30001"])
        self.order = Order.objects.create(user=self.customer, status=Order.Status.CONFIRMED)
        self.assignment = DeliveryAssignment.objects.create(order=self.order, zone=self.zone, assignee=self.rider)

    def test_only_staff_or_assignee_can_update_status(self):
        url = reverse("delivery_api:assignment-status", kwargs={"assignment_id": self.assignment.id}, host="api")

        self.client.force_authenticate(self.other_user)
        forbidden_response = self.client.patch(url, {"status": DeliveryAssignment.Status.PICKED_UP}, format="json")
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.rider)
        assignee_response = self.client.patch(url, {"status": DeliveryAssignment.Status.PICKED_UP}, format="json")
        self.assertEqual(assignee_response.status_code, status.HTTP_200_OK)

        self.assignment.status = DeliveryAssignment.Status.ASSIGNED
        self.assignment.save(update_fields=["status"])

        self.client.force_authenticate(self.staff)
        staff_response = self.client.patch(url, {"status": DeliveryAssignment.Status.PICKED_UP}, format="json")
        self.assertEqual(staff_response.status_code, status.HTTP_200_OK)
