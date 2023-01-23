from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class KernConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kern'
