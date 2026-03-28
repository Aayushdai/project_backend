from django.apps import AppConfig


class KycConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.kyc'          # Important: full path
    verbose_name = "KYC (Know Your Customer)"

    def ready(self):
        # Import signals when app is ready
        import apps.kyc.signals