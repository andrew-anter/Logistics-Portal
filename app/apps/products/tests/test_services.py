import pytest

from apps.companies.models import Company

from ..models import Product
from ..services import ProductData, create_product_service, update_product_service


@pytest.mark.django_db
def test_create_product_service(company: Company):
    new_product_data: ProductData = {
        "name": "New Awesome Widget",
        "stock_quantity": 50,
        "is_active": False,
    }

    created_product = create_product_service(company=company, **new_product_data)

    assert Product.objects.for_tenant(company).count() == 1  # pyright: ignore[reportAttributeAccessIssue]
    assert created_product.name == "New Awesome Widget"
    assert created_product.stock_quantity == 50
    assert created_product.is_active is False
    assert created_product.company == company


@pytest.mark.django_db
def test_update_product_service(product: Product):
    update_data: ProductData = {
        "name": "Updated Awesome Widget",
        "stock_quantity": 75,
        "is_active": False,
    }

    updated_product = update_product_service(product=product, **update_data)

    product.refresh_from_db()

    assert product.name == "Updated Awesome Widget"
    assert product.stock_quantity == 75
    assert product.is_active is False
    assert updated_product == product
