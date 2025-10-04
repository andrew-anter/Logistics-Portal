from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from .forms import ProfileAdminForm
from .models import Profile
from .services import block_profile_service, unblock_profile_service


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    search_fields = ("user__email", "user__first_name", "user__last_name")

    def get_list_display(self, request):  # noqa: ANN001, ANN201
        """
        Dynamically sets the columns in the list view based on user type.
        """
        # Start with a base set of fields everyone sees.
        base_fields = ("full_name", "email", "role", "is_blocked")

        # If the user is a superuser, add the 'company' column.
        if request.user.is_superuser:
            return (
                *base_fields,
                "company",
            )

        return base_fields

    def get_list_filter(self, request):  # noqa: ANN001, ANN201
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

    def history_view(self, request, object_id, extra_context=None):  # noqa: ANN001, ANN201
        """Exclude Superuser actions from history view for all non superusers"""
        response = super().history_view(request, object_id, extra_context)

        if not request.user.is_superuser:
            profile_content_type = ContentType.objects.get_for_model(Profile)
            log_entries = LogEntry.objects.filter(
                object_id=object_id,
                content_type=profile_content_type,
            )

            filtered_log_entries = log_entries.exclude(user__is_superuser=True)
            response.context_data["action_list"] = filtered_log_entries  # pyright: ignore[reportAttributeAccessIssue]

        return response

    def get_form(self, request, obj=None, **kwargs):  # noqa: ANN001, ANN003, ANN201  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Dynamically hide the company field for non-superusers.
        """
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields.pop("company", None)  # pyright: ignore[reportAttributeAccessIssue]
        return form

    @admin.display(description="Full Name")
    def full_name(self, obj):  # noqa: ANN001, ANN201
        return obj.user.get_full_name()

    @admin.display(description="Email")
    def email(self, obj):  # noqa: ANN001, ANN201
        return obj.user.email

    # --- Your existing custom actions and methods ---
    def get_actions(self, request):  # noqa: ANN001, ANN201
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def unblock_profiles(self, request, queryset: QuerySet[Profile]) -> None:  # noqa: ANN001
        for profile in queryset:
            unblock_profile_service(profile=profile)
        self.message_user(request, "Selected profiles have been unblocked.")

    def block_profiles(self, request, queryset: QuerySet[Profile]) -> None:  # noqa: ANN001
        for profile in queryset:
            block_profile_service(profile=profile)
        self.message_user(
            request,
            "Selected profiles have been blocked and their sessions invalidated.",
        )

    unblock_profiles.short_description = "Unblock Selected Profiles"  # pyright: ignore[reportFunctionMemberAccess]
    block_profiles.short_description = "Block Selected Profiles"  # pyright: ignore[reportFunctionMemberAccess]
    actions = (unblock_profiles, block_profiles)  # pyright: ignore[reportAssignmentType]
