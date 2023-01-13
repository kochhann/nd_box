from django.apps import AppConfig


class AgamottoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.agamotto'

    def ready(self):
        from . import skurge
        skurge.start()

