from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=50)
    sku = models.UUIDField()
    stock_quantity = models.IntegerField(default=0)
    company = models.ForeignKey(to="companies.Company", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.sku}"
