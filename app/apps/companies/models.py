from django.db import models

from .validators import validate_subdomain_name


class Company(models.Model):
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=50, validators=[validate_subdomain_name])
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self) -> str:
        return self.name
