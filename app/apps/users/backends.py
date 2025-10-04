from core.thread_locals import get_current_tenant
from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token

from .models import User


class TenantBackend(ModelBackend):
    def authenticate(
        self,
        request,
        username=None,
        password=None,
        token_key=None,
        company=None,
        **kwargs,
    ):
        # --- API Token Authentication Flow ---
        if token_key and company:
            try:
                token = Token.objects.select_related("user").get(key=token_key)
                user = token.user
                if (
                    user.profile.company == company
                    and not user.profile.is_blocked
                    and user.is_active
                ):
                    return user  # API login successful
            except Token.DoesNotExist:
                return None

        # --- Django Admin/Session Authentication Flow ---
        elif username and password:
            try:
                # Find the user by email (which is passed as 'username')
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                return None

            # Check the password first
            if not user.check_password(password):
                return None

            # Check if the user is blocked or inactive
            if user.profile.is_blocked or not user.is_active:
                return None

            # If the user is a superuser, they can log in anywhere
            if user.is_superuser:
                return user

            # For regular users, check if they belong to the current tenant
            current_tenant = get_current_tenant()
            if current_tenant and user.profile.company == current_tenant:
                return user

        return None  # Deny access in all other cases
