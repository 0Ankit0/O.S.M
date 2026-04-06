from django.contrib import admin

from .models import DeliveryAssignment, DeliveryEvent, DeliveryZone, ProofOfDelivery


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "default_eta_minutes")
    search_fields = ("name",)


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "assignee", "zone", "eta_at", "created_at")
    list_filter = ("status", "zone")
    search_fields = ("order__id", "assignee__email")


@admin.register(DeliveryEvent)
class DeliveryEventAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "from_status", "to_status", "actor", "created_at")


@admin.register(ProofOfDelivery)
class ProofOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "assignment", "file_name", "content_type", "file_size", "created_at")
