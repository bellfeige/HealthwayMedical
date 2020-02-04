from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User, PatientProfile, DoctorProfile, Nationality, DoctorSpeciality


class UserCreateForm(UserCreationForm):
    # email = forms.EmailField(required=True)
    is_patient = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    is_doctor = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'is_patient', 'is_doctor')


class UserAdmin(UserAdmin):
    add_form = UserCreateForm
    # prepopulated_fields = {'username': ('first_name', 'last_name',)}

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'is_patient', 'is_doctor'),
        }),
    )


admin.site.register(User, UserAdmin)
# admin.site.register(User)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(Nationality)
admin.site.register(DoctorSpeciality)
