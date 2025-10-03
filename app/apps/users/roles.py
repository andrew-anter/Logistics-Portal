"""
The single source of truth for all role definitions.
To add a new role, you only need to add an entry here.
"""

from enum import Enum

from django.contrib.auth.models import Group

ROLES = {
    "admin": {
        "permissions": [
            "users.add_profile",
            "users.change_profile",
            "users.delete_profile",
            "users.view_profile",
            "orders.add_order",
            "orders.change_order",
            "orders.delete_order",
            "orders.view_order",
            "products.add_product",
            "products.change_product",
            "products.delete_product",
            "products.view_product",
        ],
    },
    "operator": {
        "permissions": [
            "orders.add_order",
            "orders.view_order",
            "products.view_product",
        ],
    },
    "viewer": {
        "permissions": [
            "orders.view_order",
            "products.view_product",
        ],
    },
}


class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


def get_role_group(*, role: str) -> Group:
    return Group.objects.get(name=role)
