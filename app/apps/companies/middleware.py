from core.thread_locals import set_current_tenant
from django.http import Http404

from .models import Company


class TenantMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        host_parts = request.get_host().split(".")
        subdomain = host_parts[0]

        if len(host_parts) == 1:
            return self.get_response(request)

        try:
            tenant = Company.objects.get(domain=subdomain, is_active=True)
        except Company.DoesNotExist:
            raise Http404

        # Store the tenant on the request object for easy access in views
        request.tenant = tenant

        # Store it in thread-local storage for access in managers/models
        set_current_tenant(tenant)

        return self.get_response(request)
