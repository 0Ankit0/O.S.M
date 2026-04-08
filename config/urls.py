"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    # App URLs
    path("", include(("core.urls", "core"), namespace="core")),
    path("account/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("catalog/", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("dashboard/payments/", include(("payments.urls", "payments"), namespace="payments")),
    path("dashboard/delivery/", include(("delivery.urls", "delivery"), namespace="delivery")),
    path("dashboard/reporting/", include(("reporting.urls", "reporting"), namespace="reporting")),
    path("", include(("iam.urls", "iam"), namespace="iam")),
    path("", include(("multitenancy.urls", "multitenancy"), namespace="multitenancy")),
    path("", include(("finances.urls", "finances"), namespace="finances")),
    path("", include(("notifications.urls", "notifications"), namespace="notifications")),
    path("", include(("content.urls", "content"), namespace="content")),
    path("", include(("integrations.urls", "integrations"), namespace="integrations")),
    # API URLs
    path("", include("config.urls_api")),
    # i18n
    path("i18n/", include("django.conf.urls.i18n")),
    # Test URLs for error pages
    path("test-400/", core_views.custom_400_view, name="test-400"),
    path("test-403/", core_views.custom_403_view, name="test-403"),
    path("test-404/", core_views.custom_404_view, name="test-404"),
    path("test-500/", core_views.custom_500_view, name="test-500"),
    # Favicon and app icons
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.svg")),
    path("apple-touch-icon.png", RedirectView.as_view(url="/static/images/favicon.svg")),
    path("apple-touch-icon-precomposed.png", RedirectView.as_view(url="/static/images/favicon.svg")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
