from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from bootstrap_datepicker_plus import DatePickerInput
from tinymce.widgets import TinyMCE
from .models import User, PatientProfile, DoctorProfile, DoctorSpeciality, Nationality
from appointment.models import Clinic


# today = date.today()
# s = today.replace(year=2018)


def get_speciality_list():
    speciality = DoctorSpeciality.objects.all()
    return speciality


def get_clinic_list():
    speciality = Clinic.objects.all()
    return speciality


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, min_length=2, required=True)
    last_name = forms.CharField(max_length=50, min_length=2, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class PatientProfileForm(forms.ModelForm):
    id_number = forms.CharField(label='ID Number')

    id_type_choices = [('C', 'Citizen / PR'),
                       ('P', 'Passport'), ]
    id_type = forms.ChoiceField(choices=id_type_choices, widget=forms.RadioSelect, label='ID Type')
    nationality = forms.ModelChoiceField(queryset=Nationality.objects.all().order_by('nationality'))
    gender_choices = [('M', 'Male'),
                      ('F', 'Female'),
                      ('O', 'Others'), ]
    gender = forms.ChoiceField(choices=gender_choices, widget=forms.RadioSelect)
    date_of_birth = forms.DateTimeField(input_formats=settings.DATE_INPUT_FORMATS,
                                        widget=DatePickerInput(format='%d %b %Y'))
    height = forms.IntegerField(label='Height (cm)', required=False)
    weight = forms.IntegerField(label='Weight (kg)', required=False)
    contact_number = forms.CharField(max_length=50, required=False)
    contact_address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = PatientProfile
        fields = ['id_number', 'id_type', 'nationality', 'gender', 'date_of_birth', 'height', 'weight',
                  'contact_number', 'contact_address']


class DoctorProfileForm(forms.ModelForm):
    speciality = forms.ModelChoiceField(queryset=get_speciality_list(), required=False)
    second_speciality = forms.ModelChoiceField(queryset=get_speciality_list(), required=False)
    contact_number = forms.CharField(max_length=50, required=False)
    education = forms.CharField(widget=TinyMCE(attrs={'cols': 70, 'rows': 10}), required=False)
    background = forms.CharField(widget=TinyMCE(attrs={'cols': 70, 'rows': 10}), required=False)
    at_clinic = forms.ModelChoiceField(queryset=get_clinic_list(), required=False)

    class Meta:
        model = DoctorProfile
        fields = ['avatar', 'speciality', 'second_speciality', 'at_clinic', 'contact_number', 'education', 'background']


class UserTermAgree(forms.Form):
    label = 'I have read and agree to the Terms of Services and Privacy Policy listed below.'
    check = forms.BooleanField(required=True, initial=False, label=label)
