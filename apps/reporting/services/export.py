import csv
import io
import json
from hashlib import sha256

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from reporting.models import ExportJob
from reporting.services.aggregation import KPIAggregationService


class ExportMetadataService:
    @staticmethod
    def generate_for_job(job: ExportJob) -> dict:
        data = KPIAggregationService.aggregate(user=job.requested_by)
        if job.export_format == ExportJob.Format.CSV:
            content = ExportMetadataService._to_csv(data)
            extension = "csv"
            content_type = "text/csv"
        else:
            content = json.dumps(data, indent=2)
            extension = "json"
            content_type = "application/json"

        digest = sha256(content.encode("utf-8")).hexdigest()
        artifact_path = f"reporting/exports/job-{job.id}.{extension}"
        saved_path = default_storage.save(artifact_path, ContentFile(content.encode("utf-8")))
        artifact_url = default_storage.url(saved_path)
        return {
            "artifact_path": saved_path,
            "artifact_url": artifact_url,
            "content_type": content_type,
            "checksum": digest,
            "payload": data,
        }

    @staticmethod
    def _to_csv(data: dict) -> str:
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(data.keys()))
        writer.writeheader()
        writer.writerow(data)
        return stream.getvalue()
