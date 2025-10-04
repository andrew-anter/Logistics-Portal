from typing import NotRequired, TypedDict, Unpack

from django.db import transaction

from apps.companies.models import Company

from .models import Product


class ProductData(TypedDict):
    name: str
    stock_quantity: int
    is_active: NotRequired[bool]


def create_product_service(*, company: Company, **data: Unpack[ProductData]) -> Product:
    """
    Creates a new product for a specific company.
    """
    product = Product(
        name=data["name"],
        stock_quantity=data["stock_quantity"],
        is_active=data.get("is_active", True),
        company=company,
    )
    product.full_clean()
    product.save()
    return product


@transaction.atomic
def update_product_service(*, product: Product, **data: Unpack[ProductData]) -> Product:
    """
    Updates an existing product's details.
    """
    product.name = data.get("name", product.name)  # pyright: ignore[reportAttributeAccessIssue]
    product.stock_quantity = data.get("stock_quantity", product.stock_quantity)  # pyright: ignore[reportAttributeAccessIssue]
    product.is_active = data.get("is_active", product.is_active)  # pyright: ignore[reportAttributeAccessIssue]

    product.full_clean()
    product.save()

    return product
