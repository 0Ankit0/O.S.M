from django.conf import settings
from django.db import models


class ReportingJobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class ReportingJobType(models.TextChoices):
    KPI_SNAPSHOT = "kpi_snapshot", "KPI Snapshot"
    OPERATIONS = "operations", "Operations"


class BaseReportingJob(models.Model):
    type = models.CharField(max_length=32, choices=ReportingJobType.choices, default=ReportingJobType.KPI_SNAPSHOT)
    status = models.CharField(max_length=16, choices=ReportingJobStatus.choices, default=ReportingJobStatus.PENDING)
    params = models.JSONField(default=dict, blank=True)
    artifact_url = models.URLField(max_length=500, blank=True)
    artifact_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s_requested")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ReportJob(BaseReportingJob):
    class Meta(BaseReportingJob.Meta):
        db_table = "reporting_report_job"


class ExportJob(BaseReportingJob):
    class Format(models.TextChoices):
        CSV = "csv", "CSV"
        JSON = "json", "JSON"

    export_format = models.CharField(max_length=8, choices=Format.choices, default=Format.CSV)

    class Meta(BaseReportingJob.Meta):
        db_table = "reporting_export_job"
