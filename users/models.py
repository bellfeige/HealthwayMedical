from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from PIL import Image


class User(AbstractUser):
    is_patient = models.BooleanField(default=True)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.username}'


class Nationality(models.Model):
    nationality = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.nationality}'


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    id_number = models.CharField(max_length=50, null=True)
    id_type = models.CharField(max_length=1, null=True)
    gender = models.CharField(max_length=1, null=True)
    date_of_birth = models.DateField(null=True)
    height = models.PositiveSmallIntegerField(null=True)
    weight = models.PositiveSmallIntegerField(null=True)
    # contact_number = models.PositiveIntegerField(null=True)
    contact_number = models.CharField(max_length=50, null=True)
    contact_address = models.TextField(null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True,
                                    related_name='patient_nationality')

    def __str__(self):
        if self.user.first_name or self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name} Profile'
        else:
            return f'{self.user.username} Profile'

    @property
    def completed_percentage(self):
        total = 0
        percentage = {
            'id_number': 20,
            'id_type': 10,
            'gender': 10,
            'date_of_birth': 10,
            'height': 10,
            'weight': 10,
            'contact_number': 10,
            'contact_address': 10,
            'nationality': 10
        }
        if self.id_number:
            total += percentage.get('id_number', 0)
        if self.id_type:
            total += percentage.get('id_type', 0)
        if self.gender:
            total += percentage.get('gender', 0)
        if self.date_of_birth:
            total += percentage.get('date_of_birth', 0)
        if self.height:
            total += percentage.get('height', 0)
        if self.weight:
            total += percentage.get('weight', 0)
        if self.contact_number:
            total += percentage.get('contact_number', 0)
        if self.contact_address:
            total += percentage.get('contact_address', 0)
        if self.nationality:
            total += percentage.get('nationality', 0)
        return total


class DoctorSpeciality(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    avatar = models.ImageField(default='default.png', upload_to='profile_avatars')
    contact_number = models.CharField(max_length=50, null=True)
    education = models.TextField(null=True)
    background = models.TextField(null=True)
    speciality = models.ForeignKey(DoctorSpeciality, on_delete=models.SET_NULL, null=True,
                                   related_name='doctor_speciality')
    second_speciality = models.ForeignKey(DoctorSpeciality, on_delete=models.SET_NULL, null=True,
                                          related_name='doctor_speciality2')

    at_clinic = models.ForeignKey('appointment.Clinic', on_delete=models.SET_NULL, null=True,
                                  related_name='doctor_at_clinic')

    def __str__(self):
        if self.user.first_name or self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name} Profile'
        else:
            return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(DoctorProfile, self).save(*args, **kwargs)

        ava = Image.open(self.avatar.path)
        rgb_ava = ava.convert('RGB')

        if rgb_ava.height > 300 or rgb_ava.width > 300:
            output_size = (300, 300)
            rgb_ava.thumbnail(output_size)
            rgb_ava.save(self.avatar.path)
