from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from delivery.models import DeliveryAssignment, DeliveryZone
from orders.models import Order
from reporting.models import ExportJob, ReportingJobStatus
from reporting.services import KPIAggregationService
from reporting.tasks import generate_export_report

User = get_user_model()


class KPIAggregationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="report-owner@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other-owner@example.com", password="password123")
        zone = DeliveryZone.objects.create(name="Ops", postcodes=["10001"])

        self.order_1 = Order.objects.create(
            user=self.user,
            status=Order.Status.CONFIRMED,
            payment_status=Order.PaymentStatus.COMPLETED,
            subtotal=Decimal("100.00"),
        )
        self.order_2 = Order.objects.create(
            user=self.user,
            status=Order.Status.FULFILLED,
            payment_status=Order.PaymentStatus.REFUNDED,
            subtotal=Decimal("50.00"),
        )
        Order.objects.create(
            user=self.other_user,
            status=Order.Status.CONFIRMED,
            payment_status=Order.PaymentStatus.COMPLETED,
            subtotal=Decimal("25.00"),
        )

        DeliveryAssignment.objects.create(
            order=self.order_1,
            zone=zone,
            status=DeliveryAssignment.Status.DELIVERED,
            eta_at=timezone.now() + timedelta(hours=1),
        )

    def test_aggregate_user_scoped_metrics(self):
        data = KPIAggregationService.aggregate(user=self.user)
        self.assertEqual(data["orders"], 2)
        self.assertEqual(data["revenue"], "150.00")
        self.assertEqual(data["refund_rate"], 0.5)
        self.assertEqual(data["delivery_sla"], 1.0)


class ExportJobLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="exporter@example.com", password="password123")
        self.job = ExportJob.objects.create(requested_by=self.user, export_format=ExportJob.Format.JSON)

    def test_generate_export_report_marks_job_completed(self):
        generate_export_report(self.job.id)
        self.job.refresh_from_db()

        self.assertEqual(self.job.status, ReportingJobStatus.COMPLETED)
        self.assertTrue(self.job.artifact_path)
        self.assertTrue(self.job.artifact_url)

    @patch("reporting.tasks.persist_export_artifact")
    def test_generate_export_report_retries_and_fails(self, mock_persist):
        mock_persist.side_effect = RuntimeError("transient failure")

        with self.assertRaises(RuntimeError):
            generate_export_report(self.job.id, max_attempts=2)

        self.job.refresh_from_db()
        self.assertEqual(self.job.status, ReportingJobStatus.FAILED)
        self.assertEqual(self.job.retry_count, 2)


class ReportingPermissionBoundaryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@example.com", password="password123")
        self.other = User.objects.create_user(email="other@example.com", password="password123")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="password123")
        self.job = ExportJob.objects.create(requested_by=self.owner, export_format=ExportJob.Format.CSV)

    def test_only_owner_or_admin_can_view_job_status(self):
        status_url = reverse("reporting_api:export-status", kwargs={"job_id": self.job.id}, host="api")

        self.client.force_authenticate(self.other)
        forbidden = self.client.get(status_url)
        self.assertEqual(forbidden.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.owner)
        allowed = self.client.get(status_url)
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.admin)
        admin_allowed = self.client.get(status_url)
        self.assertEqual(admin_allowed.status_code, status.HTTP_200_OK)
