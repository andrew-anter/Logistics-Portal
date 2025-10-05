from core.thread_locals import get_current_tenant
from django.contrib import admin
from django.utils.html import format_html

from apps.users.roles import Role

from .forms import OrderAdminForm
from .models import Export, Order
from .services import approve_order_service, create_order_service, retry_order_service
from .tasks import generate_export_file_task


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ("reference_code", "product__name", "created_by__user__username")
    readonly_fields = ("reference_code", "created_at", "updated_at")
    form = OrderAdminForm

    def get_list_filter(self, request):
        """
        Dynamically sets the filters, showing 'company' only for superusers.
        """
        if request.user.is_superuser:
            return ("company", "status", "has_been_processed")
        return ("status",)

    def get_list_display(self, request):
        """
        Dynamically sets the columns, showing 'company' only for superusers.
        """
        # Define the base fields that are always visible
        base_display = (
            "reference_code",
            "product",
            "quantity",
            "status",
            "has_been_processed",
            "created_by",
            "created_at",
        )

        # If the user is a superuser, add 'company' to the list
        if request.user.is_superuser:
            return (
                *base_display,
                "company",
            )

        return base_display

    def save_model(self, request, obj, form, change):
        """
        Automatically set created_by, company, and status for new orders.
        """
        if not change:  # Only on creation
            company = get_current_tenant()
            create_order_service(
                product=obj.product,
                quantity=obj.quantity,
                created_by=request.user.profile,
                company=company,
            )

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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
        if profile.role and profile.role.name == "operator":
            return qs.filter(created_by=profile)

        return qs.filter(company=profile.company)

    def approve_selected_orders(self, orderadmin, request, queryset) -> None:  # noqa: ANN001
        """Triggers processing for selected PENDING orders."""
        for order in queryset:
            approve_order_service(order=order)
        self.message_user(
            request,
            f"{queryset.count()} orders have been queued for approval.",
        )

    def retry_failed_orders(self, orderadmin, request, queryset) -> None:  # noqa: ANN001
        """Resets and re-queues selected FAILED orders."""
        failed_orders = queryset.filter(status=Order.Status.FAILED)
        for order in failed_orders:
            retry_order_service(order=order)
        self.message_user(
            request,
            f"{failed_orders.count()} failed orders have been re-queued for processing.",  # noqa: E501
        )

    def export_selected_orders(self, orderadmin, request, queryset) -> None:
        """Exports selected orders to a CSV file via a background task."""
        if not queryset:
            return
        company = get_current_tenant()
        export = Export.objects.create(
            requested_by=request.user.profile,
            company=company,
        )
        order_ids = list(queryset.values_list("id", flat=True))
        generate_export_file_task.delay(
            export_id=export.pk,
            order_ids=order_ids,
            company_id=company.pk,
        )
        self.message_user(request, "Export task has been started.")

    def get_actions(self, request):  # noqa: ANN001, ANN201
        """
        Dynamically determine which actions are available based on user role.
        """
        # Get the default actions
        actions = super().get_actions(request)

        # Always remove the default delete action if it exists
        if "delete_selected" in actions:
            del actions["delete_selected"]

        user = request.user

        # Only allow admins and superusers to approve or export
        if user.is_superuser or (
            user.profile.role and user.profile.role.name == Role.ADMIN
        ):
            actions["approve_selected_orders"] = (
                self.approve_selected_orders,
                "approve_selected_orders",
                "Approve selected orders",
            )
            actions["export_selected_orders"] = (
                self.export_selected_orders,
                "export_selected_orders",
                "Export selected orders",
            )

        # Allow everyone who can see this page to retry their failed orders
        actions["retry_failed_orders"] = (
            self.retry_failed_orders,
            "retry_failed_orders",
            "Retry failed orders",
        )

        return actions


@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "requested_by",
        "status",
        "created_at",
        "download_link",
    )
    list_filter = ("status",)

    def get_queryset(self, request):  # noqa: ANN001, ANN201
        """
        Filter exports to only show entries for the current user's company,
        unless the user is a superuser.
        """
        qs = (
            super()
            .get_queryset(request)
            .select_related("company", "requested_by__user")
        )
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.profile.company)

    def get_list_filter(self, request):
        """Show company filter only for superusers."""
        if request.user.is_superuser:
            return ("company", "status")
        return ("status",)

    @admin.display(description="Download")
    def download_link(self, obj):  # noqa: ANN001, ANN201
        """Create a direct download link if the file is ready."""
        if obj.file and obj.status == Export.Status.READY:
            return format_html('<a href="{}" download>Download</a>', obj.file.url)
        return "Not ready"

    # --- Make the model read-only in the admin ---
    def has_add_permission(self, request) -> bool:  # noqa: ANN001, ARG002
        # Exports are only created via the OrderAdmin action
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # noqa: ANN001, ARG002
        # Exports are immutable once created
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # noqa: ANN001, ARG002
        return True  # Allow superusers to clean up old exports if needed
