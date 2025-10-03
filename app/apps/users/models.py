from django.contrib.auth.models import Group, User
from django.db import models

from apps.companies.managers import TenantManager


class Profile(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.PROTECT,
        related_name="profile",
    )
    company = models.ForeignKey(to="companies.Company", on_delete=models.CASCADE)
    role = models.ForeignKey(
        to=Group,
        on_delete=models.SET_NULL,
        null=True,
    )
    is_blocked = models.BooleanField(default=False)
    objects = TenantManager()

    def __str__(self) -> str:
        return self.user.get_full_name()
