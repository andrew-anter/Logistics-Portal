from django.db import transaction
from django.db.models import QuerySet

from .models import Company
from .validators import validate_subdomain_name


@transaction.atomic
def create_company(*, name: str, domain: str, is_active: bool = True) -> Company:
    validate_subdomain_name(domain)
    company = Company(name=name, domain=domain, is_active=is_active)
    company.full_clean()
    company.save()
    return company


def activate_companies(*, qs: QuerySet[Company]) -> None:
    qs.update(is_active=True)


def deactivate_companies(*, qs: QuerySet[Company]) -> None:
    qs.update(is_active=False)
