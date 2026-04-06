from django.urls import path

from .views import CatalogIndexView

app_name = "catalog"

urlpatterns = [
    path("", CatalogIndexView.as_view(), name="index"),
]
