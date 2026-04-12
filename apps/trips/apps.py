from django.apps import AppConfig


class TripsConfig(AppConfig):
    name = 'apps.trips'
    
    def ready(self):
        import apps.trips.signals
