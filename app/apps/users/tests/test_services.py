import pytest

from ..models import Profile
from ..roles import Role, get_role_group
from ..services import (
    block_profiles_service,
    create_profile_service,
    unblock_profiles_service,
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
