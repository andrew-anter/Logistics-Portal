import pytest
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.companies.services import create_company
from apps.users.roles import Role, get_role_group
from apps.users.services import create_profile_service

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


@pytest.fixture
def products(company: Company) -> Product:
    for i in range(5):
        initial_data: ProductData = {
            "name": f"Product{i}",
            "stock_quantity": 100 + i * 3,
        }
        create_product_service(company=company, **initial_data)

    return Product.objects.for_tenant(company).all()  # pyright: ignore[reportAttributeAccessIssue]


@pytest.fixture
def company_a() -> Company:
    return Company.objects.create(name="Company A", domain="companya")


@pytest.fixture
def company_b() -> Company:
    return Company.objects.create(name="Company B", domain="companyb")


@pytest.fixture
def user_a(company_a: Company):
    role = get_role_group(role=Role.OPERATOR)
    profile = create_profile_service(
        email="user_a@companya.com",
        password="password123",
        company=company_a,
        role=role,
        first_name="",
        last_name="",
    )
    return profile.user


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
