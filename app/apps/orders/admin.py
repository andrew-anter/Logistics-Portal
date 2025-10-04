from django.contrib import admin

from .models import Export, Order
from .services import approve_order_service
from .tasks import generate_export_file_task, process_order_task


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "product",
        "quantity",
        "status",
        "created_by",
        "company",
        "created_at",
    )
    search_fields = ("reference_code", "product__name", "created_by__user__username")
    readonly_fields = ("reference_code", "created_at", "updated_at")

    def get_queryset(self, request):  # noqa: ANN001, ANN201
        """
        Filters the queryset based on the user's role.
        - Superusers see everything.
        - Tenant admins see all orders for their company.
        - Operators see only their own orders.
        """
        qs = (
            super()
            .get_queryset(request)
            .select_related("product", "created_by__user", "company")
        )
        if request.user.is_superuser:
            return qs

        profile = request.user.profile  # pyright: ignore[reportAttributeAccessIssue]
        # Check the group name for the role
        if profile.role and profile.role.name == "operator":
            return qs.filter(created_by=profile)

        return qs.filter(company=profile.company)

    def get_list_filter(self, request):  # noqa: ANN001, ANN201
        """Dynamically show the company filter only for superusers."""
        if request.user.is_superuser:
            return ("company", "status")
        return ("status",)

    actions = [  # noqa: RUF012
        "approve_selected_orders",
        "retry_failed_orders",
        "export_selected_orders",
    ]

    def approve_selected_orders(self, request, queryset) -> None:  # noqa: ANN001
        """Triggers processing for selected PENDING orders."""
        pending_orders = queryset.filter(status=Order.Status.PENDING)
        for order in pending_orders:
            approve_order_service(order=order)
        self.message_user(
            request,
            f"{pending_orders.count()} orders have been queued for approval.",
        )

    approve_selected_orders.short_description = "Approve selected orders"  # pyright: ignore[reportFunctionMemberAccess]

    def retry_failed_orders(self, request, queryset) -> None:  # noqa: ANN001
        """Resets and re-queues selected FAILED orders."""
        failed_orders = queryset.filter(status=Order.Status.FAILED)
        for order in failed_orders:
            order.has_been_processed = False
            order.status = Order.Status.PENDING
            order.save()
            process_order_task.delay(order.id)
        self.message_user(
            request,
            f"{failed_orders.count()} failed orders have been re-queued for processing.",  # noqa: E501
        )

    retry_failed_orders.short_description = "Retry failed orders"  # pyright: ignore[reportFunctionMemberAccess]

    def export_selected_orders(self, request, queryset) -> None:  # noqa: ANN001
        """Exports selected orders to a CSV file via a background task."""
        if not queryset:
            return
        company = queryset.first().company
        export = Export.objects.create(
            requested_by=request.user.profile,
            company=company,
        )
        order_ids = list(queryset.values_list("id", flat=True))
        generate_export_file_task.delay(export_id=export.pk, order_ids=order_ids)  # pyright: ignore[reportCallIssue]
        self.message_user(request, "Export task has been started.")

    export_selected_orders.short_description = "Export selected orders"  # pyright: ignore[reportFunctionMemberAccess]
