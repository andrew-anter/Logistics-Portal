from django.contrib.auth.models import Group, User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    company = models.ForeignKey(
        to="companies.Company",
        on_delete=models.CASCADE,
    )
    role = models.ForeignKey(to=Group, null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return self.user.get_full_name()
