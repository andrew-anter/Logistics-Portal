import pytest
from django.contrib.auth.models import Group

from ..roles import ROLES
from ..signals import create_roles_and_permissions


@pytest.mark.django_db
def test_create_roles_signal_handler() -> None:
    # Create a dummy sender class that mimics the app config
    class DummySender:
        name = "apps.users"

    # 2. Act: Call the signal handler function directly
    create_roles_and_permissions(sender=DummySender)

    # 3. Assert: Check that the groups and permissions were created
    assert Group.objects.count() == len(ROLES)
    admin_role = Group.objects.get(name="admin")
    expected_admin_perms = len(ROLES["admin"]["permissions"])
    assert admin_role.permissions.count() == expected_admin_perms
