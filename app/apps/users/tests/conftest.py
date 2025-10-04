import pytest
from django.db.models import QuerySet

from apps.companies.models import Company
from apps.companies.services import create_company

from ..models import Profile
from ..roles import Role, get_role_group
from ..services import create_profile_service


@pytest.fixture
def company() -> Company:
    return create_company(name="test company", domain="test")


@pytest.fixture
def user_profile(company) -> Profile:
    role = get_role_group(role=Role.VIEWER)
    username = f"test"
    email = f"{username}@example.com"
    first_name = username
    last_name = f"{username} last name"
    password = f"{username} password"
    return create_profile_service(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company=company,
        role=role,
        password=password,
    )


@pytest.fixture
def profiles(company) -> QuerySet[Profile]:
    role = get_role_group(role=Role.VIEWER)
    for i in range(5):
        username = f"test{i}"
        email = f"{username}@example.com"
        first_name = username
        last_name = f"{username} last name"
        password = f"{username} password"
        create_profile_service(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company,
            role=role,
            password=password,
        )
    return Profile.objects.for_tenant(company).all()  # pyright: ignore[reportAttributeAccessIssue]
