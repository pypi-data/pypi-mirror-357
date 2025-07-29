from django.apps import AppConfig
from django.conf import settings

class GreenlightConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greenlight'

    def ready(self):
        try:
            from allianceauth.services.hooks import get_extension_urls
            get_extension_urls().register(self.name, "greenlight.urls")
        except ImportError:
            # Not running inside AllianceAuth
            pass
