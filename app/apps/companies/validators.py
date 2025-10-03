import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_subdomain_name(value: str) -> None:
    """
    Validates that the value is a valid subdomain name.
    """
    if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", value):
        raise ValidationError(
            _(
                "%(value)s is not a valid subdomain name. It can only contain "
                "lowercase letters, numbers, and hyphens. It cannot start or "
                "end with a hyphen.",
            ),
            params={"value": value},
        )
