import pytest
from django.db.models import QuerySet

from ..models import Company
from ..services import create_company


@pytest.fixture
def companies() -> QuerySet[Company]:
    for i in range(5):
        name = f"company{i}"
        domain = f"company{i}domain"
        create_company(name=name, domain=domain)

    assert Company.objects.count() == 5
    return Company.objects.all()
