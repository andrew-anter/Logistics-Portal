from celery import shared_task
from django.db import transaction

from .models import Order
from .services import approve_order_service


@shared_task
def process_order_task(order_id: int) -> None:
    try:
        with transaction.atomic():
            order = Order.objects.get(id=order_id, status=Order.Status.PENDING)
            order.status = Order.Status.PROCESSING
            order.save()
            approve_order_service(order=order)

    except Order.DoesNotExist:
        pass
