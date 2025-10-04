import threading

import pytest
from core.thread_locals import delete_current_tenant, set_current_tenant

from apps.companies.models import Company
from apps.companies.services import create_company
from apps.products.models import Product
from apps.products.services import create_product_service
from apps.users.models import Profile
from apps.users.roles import Role, get_role_group
from apps.users.services import create_profile_service


@pytest.fixture
def company() -> Company:
    return create_company(name="test company", domain="test")


@pytest.fixture
def user_profile(company: Company) -> Profile:
    role = get_role_group(role=Role.OPERATOR)
    return create_profile_service(
        email="user@company.com",
        password="password123",
        company=company,
        role=role,
        first_name="",
        last_name="",
    )


@pytest.fixture
def product(company: Company) -> Product:
    return create_product_service(
        company=company,
        name="Test Product",
        stock_quantity=100,
    )


thread_data = threading.local()


@pytest.fixture
def setup_thread_local(company):
    set_current_tenant(company)
    yield
    delete_current_tenant()
