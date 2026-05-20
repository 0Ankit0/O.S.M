from django.apps import AppConfig


class IamConfig(AppConfig):
    name = 'iam'

    def ready(self):
        pass  # Import signals to connect signal handlers
