import pytest
from django.core.exceptions import ValidationError

from ..models import Company
from ..services import create_company


@pytest.mark.django_db
def test_create_service_with_valid_data() -> None:
    name = "Test Name"
    domain = "mycompany"
    active = True

    company = create_company(name=name, domain=domain, active=active)

    assert Company.objects.all().count() == 1
    assert Company.objects.get(pk=company.pk).name == company.name
    assert Company.objects.get(pk=company.pk).domain == company.domain
    assert Company.objects.get(pk=company.pk).is_active == company.is_active


@pytest.mark.django_db
def test_create_service_with_invalid_data() -> None:
    name = ""
    domain = ""
    active = True

    with pytest.raises(ValidationError):
        create_company(name=name, domain=domain, active=active)

    name = "Test name"
    with pytest.raises(ValidationError):
        create_company(name=name, domain=domain, active=active)

    name = ""
    domain = "mydomain"
    with pytest.raises(ValidationError):
        create_company(name=name, domain=domain, active=active)

    assert Company.objects.all().count() == 0
