"""
The single source of truth for all role definitions.
To add a new role, you only need to add an entry here.
"""

from enum import Enum

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

# This dynamically creates an Enum from the keys of the ROLES dictionary.
RoleEnum = Enum("RoleEnum", {role.upper(): role for role in ROLES})
