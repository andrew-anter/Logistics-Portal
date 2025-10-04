from typing import NotRequired, TypedDict, Unpack

from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.db import transaction

from apps.companies.models import Company

from .models import Profile, User
from .roles import Role, get_role_group


class ProfileData(TypedDict):
    """Data for creating or updating a user profile."""

    email: str
    first_name: str
    last_name: str
    company: Company
    role: Group
    password: NotRequired[str]
    is_blocked: NotRequired[bool]


@transaction.atomic
def create_profile_service(**data: Unpack[ProfileData]) -> Profile:
    user = User(
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        is_staff=True,
    )

    password = data["password"]
    user.set_password(password)
    user.full_clean()
    user.save()

    role = data["role"]
    company = data["company"]
    profile = Profile(user=user, company=company, role=role)
    profile.full_clean()
    profile.save()
    user.groups.add(role)

    return profile


@transaction.atomic
def update_profile_service(profile: Profile, **data: Unpack[ProfileData]) -> Profile:
    """
    Updates a user and their associated profile from a dictionary of data.
    """
    user = profile.user

    # Update User fields
    user.email = data.get("email", user.email)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)

    # Securely handle password change if a new one is provided
    password = data.get("password")
    if password:
        user.set_password(password)

    user.save()

    # Update Profile fields
    profile.role = data.get("role", profile.role)
    profile.company = data.get("company", profile.company)
    if data.get("is_blocked"):
        block_profile_service(profile=profile)

    profile.save()

    return profile


@transaction.atomic
def block_profile_service(*, profile: Profile) -> None:
    """
    Blocks a user's profile and invalidates all their active sessions.
    """
    user = profile.user

    for session in Session.objects.all():
        session_data = session.get_decoded()
        if session_data.get("_auth_user_id") == str(user.pk):
            session.delete()

    profile.is_blocked = True
    profile.save()

    user.is_active = False
    user.save()


@transaction.atomic
def unblock_profile_service(*, profile: Profile) -> None:
    """
    Unblocks a user's profile.
    """
    user = profile.user

    profile.is_blocked = False
    profile.save()

    user.is_active = True
    user.save()


@transaction.atomic
def change_user_role(*, user_profile: Profile, new_role: Role) -> None:
    role_group = get_role_group(role=new_role)
    user_profile.role = role_group
    user_profile.full_clean()
    user_profile.save()

    user_profile.user.groups.clear()
    user_profile.user.groups.add(role_group)
