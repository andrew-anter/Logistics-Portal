from typing import NotRequired, TypedDict, Unpack

from django.db import transaction
from django.db.models import QuerySet

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
def update_product_service(
    *,
    product: Product,
    **data: Unpack[ProductData],
) -> Product:
    """
    Updates an existing product's details.
    """
    product.name = data.get("name", product.name)  # pyright: ignore[reportAttributeAccessIssue]
    product.is_active = data.get("is_active", product.is_active)  # pyright: ignore[reportAttributeAccessIssue]
    product.stock_quantity = data.get("stock_quantity", product.stock_quantity)

    product.full_clean()
    product.save()

    return product


def activate_products_service(*, products_qs: QuerySet[Product]) -> None:
    products_qs.update(is_active=True)


def deactivate_products_service(*, products_qs: QuerySet[Product]) -> None:
    products_qs.update(is_active=False)


@transaction.atomic
def adjust_product_stock_service(*, product: Product, quantity_change: int) -> Product:
    """
    Adjusts a product's stock quantity.
    quantity_change can be positive or negative.
    """
    company = product.company
    # Lock the product row to prevent race conditions
    product_to_update = (
        Product.objects.for_tenant(company).select_for_update().get(pk=product.pk)
    )

    if quantity_change < 0 and product_to_update.stock_quantity < abs(quantity_change):
        raise ValueError(
            f"Cannot remove {abs(quantity_change)} items; only {product_to_update.stock_quantity} are in stock."
        )

    product_to_update.stock_quantity += quantity_change
    product_to_update.save()

    return product_to_update
