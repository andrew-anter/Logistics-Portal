import uuid

from django.db import models

from apps.companies.managers import TenantManager


class Order(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1
        PROCESSING = 2
        APPROVED = 3
        FAILED = 4

    reference_code = models.UUIDField(default=uuid.uuid4)
    product = models.ForeignKey(to="products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    status = models.IntegerField(choices=Status)  # pyright: ignore
    created_by = models.ForeignKey("users.Profile", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(to="companies.Company", on_delete=models.CASCADE)
    objects = TenantManager()

    def __str__(self) -> str:
        return f"Order {self.reference_code}"

    @property
    def has_been_processed(self) -> bool:
        return (
            self.status == Order.Status.APPROVED or self.status == Order.Status.FAILED
        )
