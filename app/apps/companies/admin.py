from django.contrib import admin
from django.db.models import QuerySet

from .forms import CompanyAdminForm
from .models import Company
from .services import activate_companies, deactivate_companies


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = ("name", "domain", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "domain")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def make_companies_active(self, request, queryset: QuerySet[Company]) -> None:
        activate_companies(qs=queryset)
        self.message_user(
            request,
            "Selected companies have been activated.",
        )

    def disable_companies(self, request, queryset: QuerySet[Company]) -> None:
        deactivate_companies(qs=queryset)
        self.message_user(
            request,
            "Selected companies have been deactivated.",
        )

    make_companies_active.short_description = "Activate Selected Companies"
    disable_companies.short_description = "Deactivate Selected Companies"

    actions = (make_companies_active, disable_companies)
