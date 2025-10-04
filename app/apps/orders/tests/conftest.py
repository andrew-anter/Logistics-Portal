import pytest
from core.thread_locals import delete_current_tenant, set_current_tenant
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.companies.services import create_company
from apps.products.models import Product
from apps.products.services import create_product_service
from apps.users.models import Profile
from apps.users.roles import Role, get_role_group
from apps.users.services import create_profile_service
from apps.users.signals import create_roles_and_permissions

from ..models import Export, Order
from ..services import create_order_service


@pytest.fixture
def company() -> Company:
    return create_company(name="test company", domain="test")


@pytest.fixture
def company_b() -> Company:
    return create_company(name="company b", domain="companyb")


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


@pytest.fixture
def setup_current_tenant(company):
    set_current_tenant(company)
    yield
    delete_current_tenant()


@pytest.fixture
def test_data(company, product, user_profile, mocker, setup_current_tenant):
    """Fixture to create a company, user, and some orders."""
    mock_process_task = mocker.patch("apps.orders.tasks.process_order_task.delay")

    # Create a few orders for the export
    for _ in range(5):
        create_order_service(
            created_by=user_profile,
            company=company,
            quantity=30,
            product=product,
        )

    return {
        "company": company,
        "profile": user_profile,
        "order_ids": [order.id for order in Order.objects.for_tenant(company).all()],  # pyright: ignore[reportAttributeAccessIssue]
    }


@pytest.fixture(scope="session", autouse=True)
def setup_roles_and_permissions(django_db_setup, django_db_blocker):
    """
    Fixture to run the role and permission creation logic once for the test session.
    """

    class DummySender:
        name = "apps.users"

    with django_db_blocker.unblock():
        create_roles_and_permissions(sender=DummySender)


@pytest.fixture
def operator_profile(company, setup_roles_and_permissions):
    role = get_role_group(role=Role.OPERATOR)
    profile = create_profile_service(
        email="operation@company.com",
        first_name="",
        last_name="",
        company=company,
        password="TestP@ssw0rd",
        role=role,
    )
    assert profile.user.has_perm("orders.add_order")
    return profile


@pytest.fixture
def admin_profile(company, setup_roles_and_permissions):
    role = get_role_group(role=Role.ADMIN)
    return create_profile_service(
        email="operation@company.com",
        first_name="",
        last_name="",
        company=company,
        password="TestP@ssw0rd",
        role=role,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def ready_export(company, operator_profile, settings, tmp_path, setup_current_tenant):
    settings.MEDIA_ROOT = tmp_path
    export = Export.objects.create(
        company=company,
        requested_by=operator_profile,
        status=Export.Status.READY,
    )
    # Create a dummy CSV file in memory and attach it
    csv_content = "header1,header2\ndata1,data2"
    file_content = ContentFile(csv_content.encode("utf-8"))
    export.file.save("dummy_export.csv", file_content)
    return export
