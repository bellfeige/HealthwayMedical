from django.db import models
from datetime import datetime
# import datetime
from django.urls import reverse
from users.models import User, DoctorSpeciality


class Status(models.Model):
    status = models.CharField(max_length=25)
    display = models.CharField(max_length=25, null=True)
    description = models.TextField(null=True)
    colour = models.CharField(max_length=6, null=True)

    def __str__(self):
        return self.display


class Clinic(models.Model):
    name = models.CharField(max_length=50)
    # contact_number = models.PositiveIntegerField(null=True)
    contact_number = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    operating_time_from = models.TimeField(null=True)
    operating_time_to = models.TimeField(null=True)
    address = models.TextField(null=True)
    additional_info = models.TextField(null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('clinic-detail', kwargs={'pk': self.pk})


class Appointment(models.Model):
    appointment_number = models.CharField(max_length=50)
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='appointment_creator')
    status = models.ForeignKey(Status, default=1, on_delete=models.SET('Status Error'), null=True)
    speciality = models.ForeignKey(DoctorSpeciality, on_delete=models.SET_NULL, null=True,
                                   related_name='appointment_speciality')
    self_description = models.TextField(null=True)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='appointment_doctor')
    preferred_doctor = models.CharField(max_length=50, null=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name='appointment_clinic')
    appointment_datetime = models.DateTimeField()
    create_datetime = models.DateTimeField(default=datetime.now)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                        related_name='appointment_update_by')
    last_updated_datetime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f'{self.appointment_number}'

    def get_absolute_url(self):
        return reverse('aptmt-detail', kwargs={'pk': self.pk})

    @property
    def get_html_url(self):
        url = reverse('aptmt-detail', args=(self.id,))
        return f'{url}'


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    problems = models.TextField(null=True)
    medications = models.TextField(null=True)
    directives = models.TextField(null=True)
    allergies_and_adverse_reactions = models.TextField(null=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                        related_name='medical_record_update_by')
    last_updated_datetime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f'{self.appointment.appointment_number}'

    def get_absolute_url(self):
        return reverse('aptmt-detail', kwargs={'pk': self.appointment_id})


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor')
    start_datetime = models.DateTimeField(default=datetime.now)
    end_datetime = models.DateTimeField(default=datetime.now)
    notes = models.TextField(null=True)
    create_datetime = models.DateTimeField(default=datetime.now)
    create_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='create_by')
    last_updated_datetime = models.DateTimeField(default=datetime.now)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='update_by')


class SiteSetting(models.Model):
    aptmts_per_page = models.PositiveSmallIntegerField(default=10)
    patient_view_med_records = models.BooleanField(default=False)
    scope = models.PositiveSmallIntegerField(default=0, unique=True)
    doc_schedules_per_page = models.SmallIntegerField(default=10)

    def get_aptmts_per_page(self):
        return self.aptmts_per_page

    def get_doc_schedules_per_page(self):
        return self.doc_schedules_per_page
