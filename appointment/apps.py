from django.apps import AppConfig, apps


class AppointmentConfig(AppConfig):
    name = 'appointment'

    def ready(self):
        import appointment.signals
