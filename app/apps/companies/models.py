from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self) -> str:
        return self.name
