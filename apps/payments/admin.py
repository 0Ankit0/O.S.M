from django.contrib import admin

from payments.models import PaymentTransaction, PaymentWebhookEvent, RefundRequest


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "provider", "status", "amount", "currency", "created_at"]
    list_filter = ["provider", "status", "currency", "created_at"]
    search_fields = ["provider_transaction_id", "order__id", "order__user__email"]
    readonly_fields = ["provider_response", "created_at", "updated_at"]


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "payment_transaction", "amount", "status", "requested_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["provider_refund_id", "reason", "payment_transaction__provider_transaction_id"]
    readonly_fields = ["provider_response", "created_at", "updated_at"]


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ["id", "provider", "event_id", "event_type", "processed", "received_at"]
    list_filter = ["provider", "processed", "received_at"]
    search_fields = ["event_id", "event_type"]
    readonly_fields = ["payload", "received_at", "processed_at"]
