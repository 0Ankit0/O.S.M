from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reporting.api.serializers import ExportJobRequestSerializer, ExportJobSerializer
from reporting.models import ExportJob, ReportingJobStatus
from reporting.tasks import generate_export_report


class ExportJobCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExportJobRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save(requested_by=request.user, status=ReportingJobStatus.PENDING)
        generate_export_report.delay(job.id)
        return Response(ExportJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)


class ExportJobStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        queryset = ExportJob.objects.all()
        if not request.user.is_superuser:
            queryset = queryset.filter(requested_by=request.user)

        job = get_object_or_404(queryset, id=job_id)
        return Response(ExportJobSerializer(job).data, status=status.HTTP_200_OK)


class ExportJobDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        queryset = ExportJob.objects.all()
        if not request.user.is_superuser:
            queryset = queryset.filter(requested_by=request.user)

        job = get_object_or_404(queryset, id=job_id)
        if job.status != ReportingJobStatus.COMPLETED:
            return Response({"detail": "Export is not ready yet."}, status=status.HTTP_409_CONFLICT)

        return Response(
            {
                "job_id": job.id,
                "download_url": job.artifact_url,
                "artifact_path": job.artifact_path,
                "status": job.status,
                "completed_at": job.completed_at,
            },
            status=status.HTTP_200_OK,
        )
