from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[("kpi_snapshot", "KPI Snapshot"), ("operations", "Operations")],
                        default="kpi_snapshot",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("params", models.JSONField(blank=True, default=dict)),
                ("artifact_url", models.URLField(blank=True, max_length=500)),
                ("artifact_path", models.CharField(blank=True, max_length=500)),
                ("error_message", models.TextField(blank=True)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("failed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportjob_requested",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "reporting_report_job", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ExportJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[("kpi_snapshot", "KPI Snapshot"), ("operations", "Operations")],
                        default="kpi_snapshot",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("params", models.JSONField(blank=True, default=dict)),
                ("artifact_url", models.URLField(blank=True, max_length=500)),
                ("artifact_path", models.CharField(blank=True, max_length=500)),
                ("error_message", models.TextField(blank=True)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("failed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("export_format", models.CharField(choices=[("csv", "CSV"), ("json", "JSON")], default="csv", max_length=8)),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exportjob_requested",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "reporting_export_job", "ordering": ["-created_at"]},
        ),
    ]
