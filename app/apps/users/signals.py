import logging

from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .roles import ROLES

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    if sender.name != "apps.users":
        return

    # Loop through the roles and their permissions defined in roles.py
    for role_name, config in ROLES.items():
        role, created = Group.objects.get_or_create(name=role_name)

        # Clear existing permissions to ensure a clean slate
        role.permissions.clear()

        # Find and add the new permissions
        for perm_codename in config.get("permissions", []):
            try:
                app_label, codename = perm_codename.split(".")
                permission = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                )
                role.permissions.add(permission)
            except Permission.DoesNotExist:
                logger.info("Warning: Permission '%s' not found.", perm_codename)

        if created:
            logger.info("Created role '%s' with permissions.", role.name)
        else:
            logger.info("Updated permissions for role '%s'.", role.name)
