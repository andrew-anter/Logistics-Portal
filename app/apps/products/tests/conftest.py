import pytest

from apps.companies.models import Company
from apps.companies.services import create_company

from ..models import Product
from ..services import ProductData, create_product_service


@pytest.fixture
def company() -> Company:
    return create_company(name="test company", domain="test")


@pytest.fixture
def product(company: Company) -> Product:
    initial_data: ProductData = {
        "name": "Initial Product",
        "stock_quantity": 100,
    }
    return create_product_service(company=company, **initial_data)
