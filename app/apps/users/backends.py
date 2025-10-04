from core.thread_locals import get_current_tenant
from django.contrib.auth.backends import ModelBackend

from .models import User


class TenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):  # noqa: ANN001, ANN003, ANN201, ARG002
        current_tenant = get_current_tenant()

        try:
            user = User.objects.get(
                email__iexact=username,
                profile__company=current_tenant,
            )

            if not user:
                return None

        except User.DoesNotExist:
            return None

        # Don't allow login on non-tenant domains for non-superusers
        if not current_tenant and not user.is_superuser:
            return None

        # Check password and return user if valid
        if user.check_password(password):  # pyright: ignore[reportArgumentType]
            return user

        return None
