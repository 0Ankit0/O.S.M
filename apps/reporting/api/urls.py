from django.urls import path

from reporting.api.views import ExportJobCreateAPIView, ExportJobDownloadAPIView, ExportJobStatusAPIView

app_name = "reporting_api"

urlpatterns = [
    path("exports/", ExportJobCreateAPIView.as_view(), name="export-request"),
    path("exports/<int:job_id>/", ExportJobStatusAPIView.as_view(), name="export-status"),
    path("exports/<int:job_id>/download/", ExportJobDownloadAPIView.as_view(), name="export-download"),
]
