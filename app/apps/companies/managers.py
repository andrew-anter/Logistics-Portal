from typing import Any

from core.thread_locals import get_current_tenant, get_current_user
from django.db import models
from django.db.models import QuerySet

from .models import Company


class TenantManager(models.Manager):
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        company = get_current_tenant()
        user = get_current_user()

        if user and user.is_superuser:
            return queryset

        if company:
            return queryset.filter(company=company)

        # If no tenant is set, return an empty queryset
        # This prevents data leakage if middleware fails
        return queryset.none()

    def for_tenant(self, tenant: Company) -> QuerySet[Any]:
        """
        Returns a queryset filtered for a specific tenant.
        This is a helper for tests and special cases.
        """
        return super().get_queryset().filter(company=tenant)
