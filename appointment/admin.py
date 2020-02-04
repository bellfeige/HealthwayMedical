from django.contrib import admin
from .models import Clinic, Appointment, MedicalRecord

admin.site.register(Appointment)
admin.site.register(MedicalRecord)
# admin.site.register(SiteSetting)
