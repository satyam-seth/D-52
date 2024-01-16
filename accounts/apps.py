from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration class for the 'accounts' Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from accounts import signals  # pylint: disable=unused-import
