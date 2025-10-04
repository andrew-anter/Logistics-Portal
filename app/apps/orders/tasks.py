import csv
import io

from celery import shared_task
from django.core.files.base import ContentFile
from django.db import transaction

from .models import Export, Order
from .selectors import get_export_for_company, get_orders_for_company
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


@shared_task
@transaction.atomic
def generate_export_file_task(
    export_id: int,
    order_ids: list[int],
    company_id: int,
) -> None:
    export = get_export_for_company(pk=export_id, company_pk=company_id)

    try:
        orders = get_orders_for_company(company_pk=company_id).filter(id__in=order_ids)

        # Use an in-memory text buffer to build the CSV
        string_io = io.StringIO()
        writer = csv.writer(string_io)

        # Write header row
        writer.writerow(
            ["Reference Code", "Product SKU", "Quantity", "Status", "Created At"],
        )

        # Write data rows
        for order in orders:
            writer.writerow(
                [
                    order.reference_code,
                    order.product.sku,
                    order.quantity,
                    order.get_status_display(),  # pyright: ignore[reportAttributeAccessIssue]
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ],
            )

        # Create a Django ContentFile from the buffer's content
        file_content = ContentFile(string_io.getvalue().encode("utf-8"))

        # Save the file to the Export object's FileField
        export.file.save(f"export_{export_id}.csv", file_content)

        # Mark the export as ready
        export.status = Export.Status.READY
        export.save()

    except Exception:
        # If anything goes wrong, mark the export as failed
        if "export" in locals():
            export.status = Export.Status.FAILED
            export.save()
        raise
