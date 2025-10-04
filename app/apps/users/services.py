from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import QuerySet

from apps.companies.models import Company

from .models import Profile
from .roles import Role, get_role_group


@transaction.atomic
def create_profile_service(
    *,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    company: Company,
    role: Group,
) -> Profile:
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password)
    user.full_clean()
    user.save()
    user.groups.add(role)

    profile = Profile(user=user, company=company, role=role)
    profile.full_clean()
    profile.save()

    return profile


def block_profiles_service(*, qs: QuerySet[Profile]) -> None:
    qs.update(is_blocked=True)


def unblock_profiles_service(*, qs: QuerySet[Profile]) -> None:
    qs.update(is_blocked=False)


@transaction.atomic
def change_user_role(*, user_profile: Profile, new_role: Role) -> None:
    role_group = get_role_group(role=new_role)
    user_profile.role = role_group
    user_profile.full_clean()
    user_profile.save()

    user_profile.user.groups.clear()
    user_profile.user.groups.add(role_group)
