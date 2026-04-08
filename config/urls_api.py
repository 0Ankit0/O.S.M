from django.conf import settings
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

api_info = openapi.Info(
    title="Django Template Backend API",
    default_version="v1",
    description="REST API for Django Template Backend with Auth, Payments, Subscriptions, Multi-tenancy, CMS & OpenAI"
)


class HttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    api_info,
    public=True,
    generator_class=HttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r"^doc/", schema_view.with_ui("swagger"), name='schema-swagger-ui'),
    re_path(r"^redoc/", schema_view.with_ui("redoc"), name='schema-redoc'),

    path(
        "api/",
        include(
            [
                # Authentication & User Management
                path("iam/", include(("iam.api.urls", "iam_api"), namespace="iam_api")),

                # Multi-tenancy
                path("multitenancy/", include(("multitenancy.api.urls", "multitenancy_api"), namespace="multitenancy_api")),

                # Notifications
                path("notifications/", include(("notifications.api.urls", "notifications_api"), namespace="notifications_api")),

                # Accounts
                path("accounts/", include(("accounts.api.urls", "accounts_api"), namespace="accounts_api")),

                # Finances & Subscriptions
                path("finances/", include(("finances.api.urls", "finances_api"), namespace="finances_api")),

                # Content Management (Contentful CMS)
                path("content/", include(("content.api.urls", "content_api"), namespace="content_api")),

                # Integrations (OpenAI)
                path("integrations/", include(("integrations.api.urls", "integrations_api"), namespace="integrations_api")),

                # Catalog
                path("catalog/", include(("catalog.api.urls", "catalog_api"), namespace="catalog_api")),

                # Orders
                path("orders/", include(("orders.api.urls", "orders_api"), namespace="orders_api")),

                # Payments
                path("payments/", include(("payments.api.urls", "payments_api"), namespace="payments_api")),

                # Delivery
                path("delivery/", include(("delivery.api.urls", "delivery_api"), namespace="delivery_api")),

                # Reporting
                path("reporting/", include(("reporting.api.urls", "reporting_api"), namespace="reporting_api")),
            ]
        ),
    ),


]

# Browser reload for development
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
