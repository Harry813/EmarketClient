from django.apps import AppConfig


class KernConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kern'

    def ready (self):
        from rest_framework_api_key.models import APIKey
        from kern.utils.core import send_request

        if not APIKey.objects.filter(name='ADM_CONTROL').exists():
            response = send_request('/init/api-key/', 'GET', payload={"name": "ADM_CONTROL"})
            if response.status_code == 200:
                APIKey.objects.create(**response.json())

        if not APIKey.objects.filter(name='RMTCTL').exists():
            response = send_request('/init/api-key/', 'GET', payload={"name": "RMTCTL"})
            if response.status_code == 200:
                APIKey.objects.create(**response.json())
