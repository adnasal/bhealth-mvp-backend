from django.apps import AppConfig


class BHealthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bhealthapp'


class BHealthCaching(AppConfig):
    name = 'bhealth_cache'

    def ready(self):
        import signals