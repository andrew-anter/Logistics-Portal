from core.thread_locals import set_current_tenant, set_current_user
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

        set_current_tenant(tenant)

        if request.user.is_authenticated:
            set_current_user(request.user)

        return self.get_response(request)
