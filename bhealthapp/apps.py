from django.apps import AppConfig


class BhealthappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bhealthapp'


class BhealthCaching(AppConfig):
    name = 'bhealth_cache'

    def ready(self):
        import signals