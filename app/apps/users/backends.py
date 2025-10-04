from core.thread_locals import get_current_tenant
from django.contrib.auth.backends import ModelBackend

from .models import User


class TenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):  # noqa: ANN001, ANN003, ANN201, ARG002
        current_company = get_current_tenant()

        try:
            user = User.objects.select_related(
                "profile__company",
            ).get(
                email__iexact=username,
            )

            if user.is_superuser and user.check_password(password):  # pyright: ignore[reportArgumentType]
                return user

            if user.profile.is_blocked:  # pyright: ignore[reportAttributeAccessIssue]
                return None

            if user.profile.company != current_company:  # pyright: ignore[reportAttributeAccessIssue]
                return None

        except User.DoesNotExist:
            return None

        # Check password and return user if valid
        if user.check_password(password):  # pyright: ignore[reportArgumentType]
            return user

        return None
