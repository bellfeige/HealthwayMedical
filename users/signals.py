from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PatientProfile, DoctorProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_patient:
            PatientProfile.objects.create(user=instance)
        elif instance.is_doctor:
            DoctorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.is_patient:
        instance.patient_profile.save()
    elif instance.is_doctor:
        instance.doctor_profile.save()
