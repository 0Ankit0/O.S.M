from django.conf import settings
from django.db import models


class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUND_PENDING = "refund_pending", "Refund Pending"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        KHALTI = "khalti", "Khalti"

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment_record")
    provider = models.CharField(max_length=20, choices=Provider.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NPR")
    provider_transaction_id = models.CharField(max_length=255, unique=True, db_index=True)
    payment_url = models.URLField(blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} - {self.provider} - {self.status}"


class RefundRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    payment_transaction = models.ForeignKey(
        PaymentTransaction, on_delete=models.CASCADE, related_name="refund_requests"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    provider_refund_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentWebhookEvent(models.Model):
    provider = models.CharField(max_length=20, db_index=True)
    event_id = models.CharField(max_length=255, db_index=True)
    event_type = models.CharField(max_length=100, db_index=True)
    signature = models.CharField(max_length=255)
    payload = models.JSONField()
    processed = models.BooleanField(default=False, db_index=True)
    process_attempts = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-received_at"]
        constraints = [
            models.UniqueConstraint(fields=["provider", "event_id"], name="unique_payment_webhook_event_per_provider")
        ]

    def __str__(self):
        return f"{self.provider}:{self.event_id}"
