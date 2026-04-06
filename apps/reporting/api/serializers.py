from rest_framework import serializers

from reporting.models import ExportJob


class ExportJobRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = ["id", "type", "export_format", "params", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class ExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = [
            "id",
            "type",
            "export_format",
            "status",
            "params",
            "artifact_url",
            "artifact_path",
            "error_message",
            "retry_count",
            "requested_by",
            "started_at",
            "completed_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
