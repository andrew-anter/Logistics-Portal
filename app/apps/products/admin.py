from django.contrib import admin
from django.db.models import QuerySet

from apps.products.services import (
    activate_products_service,
    deactivate_products_service,
)

from .forms import ProductAdminForm
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    search_fields = ("name", "sku")

    def get_list_display(self, request):  # noqa: ANN001, ANN201
        base_fields = ("name", "sku", "stock_quantity", "is_active")
        if request.user.is_superuser:
            return (*base_fields, "company")
        return base_fields

    def get_list_filter(self, request):  # noqa: ANN001, ANN201
        if request.user.is_superuser:
            return ("company", "is_active")
        return ("is_active",)

    def get_form(self, request, obj=None, **kwargs):  # noqa: ANN001, ANN003, ANN201  # pyright: ignore[reportIncompatibleMethodOverride]
        """Dynamically hide the company field for non-superusers."""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and "company" in form.base_fields:  # pyright: ignore[reportAttributeAccessIssue]
            form.base_fields.pop("company")  # pyright: ignore[reportAttributeAccessIssue]
        return form

    def activate_products(self, request, queryset: QuerySet[Product]) -> None:  # noqa: ANN001
        activate_products_service(products_qs=queryset)
        self.message_user(request, "Selected products have been activated.")

    def deactivate_products(self, request, queryset: QuerySet[Product]) -> None:  # noqa: ANN001
        deactivate_products_service(products_qs=queryset)
        self.message_user(request, "Selected products have been deactivated.")

    actions = (activate_products, deactivate_products)  # pyright: ignore[reportAssignmentType]
