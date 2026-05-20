from base64 import b64decode
from binascii import Error as BinasciiError

from django.utils.functional import SimpleLazyObject

from .models import Tenant, TenantMembership


def get_current_tenant(tenant_id):
    """
    Retrieve the current tenant based on the provided tenant ID.

    Args:
        tenant_id (str): The ID of the tenant.

    Returns:
        Tenant or None: The retrieved tenant or None if not found.
    """
    try:
        return Tenant.objects.get(pk=tenant_id)
    except (Tenant.DoesNotExist, TypeError, ValueError):
        return None


def get_current_user_role(tenant, user):
    """
    Retrieve the user role within the specified tenant.

    Args:
        tenant (Tenant): The current tenant.
        user (User): The user for whom the role is to be retrieved.

    Returns:
        str or None: The user role or None if not found or invalid conditions.
    """
    if user and user.is_authenticated and tenant:
        try:
            membership = TenantMembership.objects.get(user=user, tenant=tenant)
            return membership.role
        except TenantMembership.DoesNotExist:
            return None

    return None


class TenantUserRoleMiddleware:
    """
    Middleware for resolving the current tenant for REST API requests.

    This middleware extracts the tenant ID from request headers or parameters
    and attaches the tenant object to the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _normalize_tenant_id(value):
        if value in (None, ""):
            return None

        if not isinstance(value, str):
            return value

        if ":" in value:
            return None

        try:
            decoded = b64decode(value).decode("utf-8")
        except (BinasciiError, UnicodeDecodeError, ValueError):
            return value

        node_type, separator, tenant_id = decoded.partition(":")
        if not separator:
            return value
        if node_type != "TenantType" or not tenant_id:
            return None
        return tenant_id

    @classmethod
    def _get_tenant_id_from_arguments(cls, args):
        if not isinstance(args, dict):
            return None

        candidate = args.get("tenant_id") or args.get("id")
        input_args = args.get("input")
        if isinstance(input_args, dict):
            candidate = input_args.get("tenant_id", candidate)

        return cls._normalize_tenant_id(candidate)

    def __call__(self, request):
        # Extract tenant ID from header, query params, or session
        tenant_id = self._normalize_tenant_id(
            request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id") or request.session.get("tenant_id")
        )
        request.tenant_id = tenant_id

        if tenant_id:
            request.tenant = SimpleLazyObject(lambda: get_current_tenant(tenant_id))
            request.user_role = SimpleLazyObject(lambda: get_current_user_role(request.tenant, request.user))
        else:
            request.tenant = None
            request.user_role = None

        response = self.get_response(request)
        return response


TenantMiddleware = TenantUserRoleMiddleware
