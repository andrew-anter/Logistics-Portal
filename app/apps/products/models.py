import uuid

from django.db import models

from apps.companies.managers import TenantManager


class Product(models.Model):
    name = models.CharField(max_length=50)
    sku = models.UUIDField(default=uuid.uuid4)
    stock_quantity = models.IntegerField(default=0)
    company = models.ForeignKey(to="companies.Company", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    objects = TenantManager()

    def __str__(self) -> str:
        return self.name
