from apps.products.services import adjust_product_stock_service

from .models import Order


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
