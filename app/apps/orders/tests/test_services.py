import pytest

from apps.products.models import Product
from apps.users.models import Profile

from ..models import Order
from ..services import approve_order_service


@pytest.mark.django_db
def test_approve_order_success_with_sufficient_stock(
    product: Product,
    user_profile: Profile,
    setup_thread_local,
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
