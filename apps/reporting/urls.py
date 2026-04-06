from django.urls import path

from .views import ReportingIndexView

app_name = "reporting"

urlpatterns = [
    path("", ReportingIndexView.as_view(), name="index"),
]
