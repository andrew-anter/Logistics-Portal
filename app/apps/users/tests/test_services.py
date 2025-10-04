import pytest
from django.contrib.auth.models import User

from apps.companies.services import create_company

from ..models import Profile
from ..roles import Role, get_role_group
from ..services import (
    block_profiles_service,
    create_profile_service,
    unblock_profiles_service,
    update_profile_service,
)


@pytest.mark.django_db
def test_create_profile(company) -> None:
    username = "test"
    email = "test@example.com"
    first_name = "test"
    last_name = "test last name"
    password = "test password"
    role = get_role_group(role=Role.ADMIN)

    user_profile = create_profile_service(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        company=company,
        role=role,
        password=password,
    )
    assert Profile.objects.for_tenant(company).filter(pk=user_profile.pk).exists()  # pyright: ignore


@pytest.mark.django_db
def test_update_profile_service(user_profile, company):
    admin_role = get_role_group(role=Role.ADMIN)
    new_company = create_company(name="new company", domain="domain")
    update_data = {
        "username": "updated_user",
        "email": "updated@test.com",
        "first_name": "Updated",
        "last_name": "User",
        "password": "a_new_secure_password_456",
        "role": admin_role,
        "is_blocked": True,
        "company": new_company,
    }

    update_profile_service(user_profile, **update_data)

    user = User.objects.get(pk=user_profile.user.pk)
    user_profile.refresh_from_db()

    # Assert that each attribute was updated correctly
    assert user.username == "updated_user"
    assert user.email == "updated@test.com"
    assert user.first_name == "Updated"
    assert user.last_name == "User"
    assert user_profile.role == admin_role
    assert user_profile.is_blocked is True
    assert user_profile.company == new_company

    assert user.check_password("a_new_secure_password_456")
    assert not user.check_password("initial_password_123")


@pytest.mark.django_db
def test_block_profiles(profiles, company):
    block_profiles_service(qs=profiles)
    assert (
        Profile.objects.for_tenant(company).filter(is_blocked=True).count()  # pyright: ignore
        == profiles.count()
    )


@pytest.mark.django_db
def test_unblock_profiles(profiles, company):
    block_profiles_service(qs=profiles)
    unblock_profiles_service(qs=profiles)
    assert (
        Profile.objects.for_tenant(company).filter(is_blocked=False).count()  # pyright: ignore
        == profiles.count()
    )


@pytest.mark.django_db
def test_set_user_role(user_profile):
    assert user_profile.role == get_role_group(role=Role.VIEWER)
