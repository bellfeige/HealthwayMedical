from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, MedicalRecord


@receiver(post_save, sender=Appointment)
def create_profile(sender, instance, created, **kwargs):
    if created:
        MedicalRecord.objects.create(appointment=instance)


@receiver(post_save, sender=Appointment)
def save_profile(sender, instance, **kwargs):
    instance.medical_record.save()
