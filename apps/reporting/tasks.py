from celery import shared_task
from django.utils import timezone

from reporting.models import ExportJob, ReportingJobStatus
from reporting.services import ExportMetadataService


@shared_task
def persist_export_artifact(job_id: int) -> dict:
    job = ExportJob.objects.get(id=job_id)
    result = ExportMetadataService.generate_for_job(job)
    job.artifact_path = result["artifact_path"]
    job.artifact_url = result["artifact_url"]
    job.status = ReportingJobStatus.COMPLETED
    job.completed_at = timezone.now()
    job.error_message = ""
    job.save(update_fields=["artifact_path", "artifact_url", "status", "completed_at", "error_message", "updated_at"])
    return {"job_id": job.id, "status": job.status, "artifact_url": job.artifact_url}


@shared_task
def generate_export_report(job_id: int, max_attempts: int = 3) -> dict:
    job = ExportJob.objects.get(id=job_id)
    job.status = ReportingJobStatus.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at", "updated_at"])

    for attempt in range(1, max_attempts + 1):
        try:
            return persist_export_artifact(job.id)
        except Exception as exc:
            job.retry_count = attempt
            job.error_message = str(exc)
            if attempt >= max_attempts:
                job.status = ReportingJobStatus.FAILED
                job.failed_at = timezone.now()
                job.save(update_fields=["retry_count", "error_message", "status", "failed_at", "updated_at"])
                raise
            job.save(update_fields=["retry_count", "error_message", "updated_at"])

    return {"job_id": job.id, "status": job.status}
