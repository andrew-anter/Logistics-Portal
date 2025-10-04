from apps.companies.models import Company
from apps.products.models import Product
from apps.products.services import adjust_product_stock_service
from apps.users.models import Profile

from .models import Order


def create_order_service(
    *,
    product: Product,
    quantity: int,
    created_by: Profile,
    company: Company,
) -> Order:
    """
    Creates a new Order in a PENDING state and triggers a background
    task to process it.
    """
    from .tasks import process_order_task

    if quantity <= 0:
        msg = "Order quantity must be a positive number."
        raise ValueError(msg)

    order = Order.objects.create(
        product=product,
        quantity=quantity,
        created_by=created_by,
        company=company,
        status=Order.Status.PENDING,
    )

    process_order_task.delay(order.pk)

    return order


def approve_order_service(*, order: Order) -> None:
    """
    Approves an order if stock is available, and deducts the stock quantity.
    """
    if order.status != Order.Status.PENDING:
        return

    product = order.product
    if product.stock_quantity >= order.quantity:
        order.status = Order.Status.APPROVED
        adjust_product_stock_service(
            product=product,
            quantity_change=-order.quantity,
        )

    else:
        order.status = Order.Status.FAILED

    order.has_been_processed = True
    order.save()
