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
    product = models.ForeignKey(to="products.Product", on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    status = models.IntegerField(choices=Status)  # pyright: ignore
    created_by = models.ForeignKey("users.Profile", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(to="companies.Company", on_delete=models.CASCADE)
    has_been_processed = models.BooleanField(default=False)
    objects = TenantManager()

    def __str__(self) -> str:
        return f"Order {self.reference_code}"


class Export(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    requested_by = models.ForeignKey(
        "users.Profile",
        on_delete=models.SET_NULL,
        null=True,
    )
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    file = models.FileField(upload_to="exports/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = TenantManager()

    def __str__(self) -> str:
        return f"export number {self.pk}"
