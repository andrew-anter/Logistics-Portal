from core.thread_locals import set_current_tenant, set_current_user
from django.http import Http404

from .models import Company


class TenantMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        host_parts = request.get_host().split(".")
        subdomain = host_parts[0]

        set_current_user(request.user)

        if len(host_parts) == 1:
            return self.get_response(request)

        try:
            company = Company.objects.get(domain=subdomain, is_active=True)
        except Company.DoesNotExist:
            raise Http404

        set_current_tenant(company)
        request.company = company

        return self.get_response(request)
