"""
Django admin configuration for the identity app.
Provides a comprehensive admin interface for user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):  # type: ignore[type-arg]
    """Custom admin interface for the User model."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "email_verified",
        "created_at",
        "last_login",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "created_at",
        "last_login",
    )

    search_fields = ("email", "username", "first_name", "last_name")

    ordering = ("-created_at",)

    readonly_fields = ("id", "created_at", "updated_at", "last_login", "last_login_ip")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar_url",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "last_login_ip",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            _("Technical"),
            {
                "classes": ("collapse",),
                "fields": ("id",),
            },
        ),
    )

    def get_readonly_fields(
        self, request: HttpRequest, obj: User | None = None
    ) -> list[str]:
        """Make certain fields read-only based on context."""
        readonly = list(self.readonly_fields)

        if obj:
            readonly.append("email")

        return readonly

    def save_model(
        self,
        request: HttpRequest,
        obj: User,
        form: ModelForm,  # type: ignore[type-arg]
        change: bool,
    ) -> None:
        """Custom save logic."""
        if not change:
            if not obj.username:
                obj.username = obj.email

        super().save_model(request, obj, form, change)

    actions = ["verify_emails", "deactivate_users", "activate_users"]

    def verify_emails(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Admin action to verify emails for selected users."""
        updated = queryset.update(email_verified=True)
        self.message_user(
            request, f"{updated} user(s) email addresses were successfully verified."
        )

    verify_emails.short_description = "Verify email addresses"  # type: ignore[attr-defined]

    def deactivate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Admin action to deactivate selected users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) were successfully deactivated.")

    deactivate_users.short_description = "Deactivate selected users"  # type: ignore[attr-defined]

    def activate_users(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        """Admin action to activate selected users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) were successfully activated.")

    activate_users.short_description = "Activate selected users"  # type: ignore[attr-defined]
