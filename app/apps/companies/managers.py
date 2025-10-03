from typing import Any

from core.thread_locals import get_current_tenant
from django.db import models
from django.db.models import QuerySet


class TenantManager(models.Manager):
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        company = get_current_tenant()

        if company:
            return queryset.filter(company=company)

        # If no tenant is set, return an empty queryset
        # This prevents data leakage if middleware fails
        return queryset.none()
