import pytest

from apps.products.models import Product
from apps.users.models import Profile

from ..models import Order
from ..services import approve_order_service, create_order_service, retry_order_service


@pytest.mark.django_db
def test_approve_order_success_with_sufficient_stock(
    product: Product,
    user_profile: Profile,
    setup_current_tenant,
):
    # 1. Arrange: Create a pending order with a quantity we know is in stock
    order = Order.objects.create(
        product=product,
        quantity=10,
        created_by=user_profile,
        company=user_profile.company,
        status=Order.Status.PENDING,
    )
    assert product.stock_quantity == 100

    # 2. Act: Call the service to approve the order
    approve_order_service(order=order)

    # 3. Assert: Check that the order and product states are correct
    order.refresh_from_db()
    product.refresh_from_db()

    assert order.status == Order.Status.APPROVED
    assert order.has_been_processed is True
    assert product.stock_quantity == 90  # 100 - 10


@pytest.mark.django_db
def test_create_order_service(
    product,
    user_profile,
    company,
    mocker,
    setup_current_tenant,
):
    # 1. Arrange: Patch the Celery task so we can check if it was called
    mock_process_task = mocker.patch("apps.orders.tasks.process_order_task.delay")

    order_quantity = 5

    # 2. Act: Call the create service
    new_order = create_order_service(
        product=product,
        quantity=order_quantity,
        created_by=user_profile,
        company=company,
    )

    # 3. Assert: Check that the Order object was created correctly
    assert Order.objects.count() == 1
    assert new_order.product == product
    assert new_order.quantity == order_quantity
    assert new_order.created_by == user_profile
    assert new_order.company == company
    assert new_order.status == Order.Status.PENDING
    assert new_order.has_been_processed is False

    # Assert that the background task was called exactly once with the new order's ID
    mock_process_task.assert_called_once_with(new_order.pk)


@pytest.mark.django_db
def test_retry_order_service(product, user_profile, company, mocker):
    # 1. Arrange: Create an order that is already in a FAILED state
    order = create_order_service(
        product=product,
        quantity=20,
        created_by=user_profile,
        company=company,
    )

    mock_process_task = mocker.patch("apps.orders.tasks.process_order_task.delay")

    # 2. Act: Call the retry service
    retried_order = retry_order_service(order=order)

    # 3. Assert: Check that the order's state was correctly reset
    assert retried_order.status == Order.Status.PENDING
    assert retried_order.has_been_processed is False

    # Assert that the background task was re-queued
    mock_process_task.assert_called_once_with(order.pk)
