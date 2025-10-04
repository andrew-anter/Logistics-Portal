from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication

from apps.companies.models import Company


class TenantTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):  # pyright: ignore[reportIncompatibleMethodOverride]  # noqa: ANN001, ANN201
        host = self.get_host(self.request)  # pyright: ignore[reportAttributeAccessIssue]
        subdomain = host.split(".")[0]

        try:
            company = Company.objects.get(domain=subdomain)
        except Company.DoesNotExist:
            # No company found for this subdomain, deny access.
            return None

        # Now, call Django's authenticate, passing the company along
        # This will be received by your custom TenantBackend
        user = authenticate(request=self.request, token_key=key, company=company)  # pyright: ignore[reportAttributeAccessIssue]

        if user:
            return (user, user.auth_token)  # pyright: ignore[reportAttributeAccessIssue]
        return None

    def get_host(self, request):  # noqa: ANN001, ANN201
        """Get the host from the request headers."""
        return request.get_host().split(":")[0].lower()
