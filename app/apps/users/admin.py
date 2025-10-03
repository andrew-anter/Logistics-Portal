from django.contrib import admin
from .models import Profile
from .forms import ProfileAdminForm
from django.db.models import QuerySet
from .services import unblock_profiles_service, block_profiles_service


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    search_fields = ("user__username", "user__first_name", "user__last_name")

    def get_list_display(self, request):
        """
        Dynamically sets the columns in the list view based on user type.
        """
        # Start with a base set of fields everyone sees.
        base_fields = ("username", "full_name", "email", "role", "is_blocked")

        # If the user is a superuser, add the 'company' column.
        if request.user.is_superuser:
            return (
                *base_fields,
                "company",
            )

        return base_fields

    def get_list_filter(self, request):
        """
        Dynamically sets the filters in the sidebar based on user type.
        """
        base_filters = ("role", "is_blocked")

        # If the user is a superuser, add the 'company' filter.
        if request.user.is_superuser:
            return (
                *base_filters,
                "company",
            )

        return base_filters

    @admin.display(description="Username")
    def username(self, obj):
        return obj.user.username

    @admin.display(description="Full Name")
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="Email")
    def email(self, obj):
        return obj.user.email

    # --- Your existing custom actions and methods ---
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def unblock_profiles(self, request, queryset: QuerySet[Profile]) -> None:
        unblock_profiles_service(qs=queryset)
        self.message_user(request, "Selected profiles have been unblocked.")

    def block_profiles(self, request, queryset: QuerySet[Profile]) -> None:
        block_profiles_service(qs=queryset)
        self.message_user(request, "Selected profiles have been blocked.")

    unblock_profiles.short_description = "Unblock Selected Profiles"
    block_profiles.short_description = "Block Selected Profiles"
    actions = (unblock_profiles, block_profiles)
