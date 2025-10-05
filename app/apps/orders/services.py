import logging

from django.db import transaction

from apps.companies.models import Company
from apps.products.models import Product
from apps.products.services import adjust_product_stock_service
from apps.users.models import Profile

from .models import Order

logger = logging.getLogger(__name__)


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

    process_order_task.delay(order.pk, company_id=order.company.pk)

    return order


@transaction.atomic
def approve_order_service(*, order: Order) -> None:
    """
    Approves an order if stock is available, and deducts the stock quantity.
    """
    if order.status != Order.Status.PROCESSING or not order.product.is_active:
        return

    product = order.product
    if product.stock_quantity >= order.quantity:
        order.status = Order.Status.APPROVED
        adjust_product_stock_service(
            product=product,
            quantity_change=-order.quantity,
        )
        logger.info("Order %s approved.", order.reference_code)

    else:
        order.status = Order.Status.FAILED
        logger.warning(
            "Order %s failed due to insufficient stock.",
            order.reference_code,
        )

    order.has_been_processed = True
    order.save()


def retry_order_service(*, order: Order) -> Order:
    """
    Resets a FAILED order to PENDING and re-queues it for processing.
    """
    from .tasks import process_order_task

    if order.status != Order.Status.FAILED:
        msg = "Only failed orders can be retried."
        raise ValueError(msg)

    order.status = Order.Status.PENDING
    order.has_been_processed = False
    order.save()

    process_order_task.delay(order.pk, company_id=order.company.pk)

    return order
