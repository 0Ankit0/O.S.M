from django.urls import path

from .views import AccountsIndexView

app_name = "accounts"

urlpatterns = [
    path("", AccountsIndexView.as_view(), name="index"),
]
