import pytest
from django.conf import settings

from apps.products.services import create_product_service


@pytest.mark.django_db
def test_list_products_success_for_correct_tenant(api_client, user_a, company_a):
    # Arrange: Create products for a single company
    create_product_service(company=company_a, name="Widget A", stock_quantity=10)

    api_client.force_authenticate(user=user_a)

    # Act: User A tries to access products on Company A's subdomain
    response = api_client.get(
        "/api/products/",
        HTTP_HOST=f"{company_a.domain}.{settings.MAIN_DOMAIN}",
    )

    # Assert: The products shall return to the user
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Widget A"


@pytest.mark.django_db
def test_list_products_fails_for_wrong_tenant(api_client, user_a, company_a, company_b):
    # Arrange: Create products for both companies
    create_product_service(company=company_a, name="Widget A", stock_quantity=10)
    create_product_service(company=company_b, name="Gadget B", stock_quantity=20)

    api_client.force_authenticate(user=user_a)

    # Act: User A tries to access products on Company B's subdomain
    response = api_client.get(
        "/api/products/",
        HTTP_HOST=f"{company_b.domain}.{settings.MAIN_DOMAIN}",
    )

    # Assert: The TenantManager should return an empty queryset
    assert response.status_code == 200
    assert len(response.data) == 0  # User A sees no products


@pytest.mark.django_db
def test_list_products_fails_for_unauthenticated_user(api_client, company_a):
    response = api_client.get(
        "/api/products/",
        HTTP_HOST=f"{company_a.domain}.{settings.MAIN_DOMAIN}",
    )

    # Assert
    assert response.status_code == 401
