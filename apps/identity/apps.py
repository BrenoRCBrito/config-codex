"""Django app configuration for the identity module."""

from django.apps import AppConfig


class IdentityConfig(AppConfig):
    """App configuration for the identity bounded context."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.identity"
    verbose_name = "Identity Management"

    def ready(self) -> None:
        """Perform initialization when Django starts."""
        pass


default_app_config = "apps.identity.apps.IdentityConfig"
