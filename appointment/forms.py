from django import forms
from django.db.models import Q
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE
from datetime import datetime
from bootstrap_datepicker_plus import DateTimePickerInput, TimePickerInput
from .models import Appointment, MedicalRecord, SiteSetting, DoctorSchedule, Clinic, Status
from users.models import User, DoctorSpeciality


# status_list = (
#     ('1', 'Submitted'),
#     ('2', 'Cancelled'),
#     ('3', 'Pending'),
#     ('4', 'Confirmed'),
#     ('5', 'Reschedule_confirmed'),
#     ('6', 'Completed'),
# )

def all_aptmt_status():
    status = Status.objects.all().order_by('id')
    return status


def all_speciality():
    speciality = DoctorSpeciality.objects.all().order_by('id')
    return speciality


def get_available_status4admin(self):
    if self.status.id == 1:
        status_list = (
            ('1', 'Submitted'),
            ('2', 'Cancelled'),
            ('3', 'Pending'),
            ('4', 'Confirmed'),
        )
    elif self.status.id == 2:
        status_list = (
            ('1', 'Submitted'),
            ('2', 'Cancelled'),
            ('3', 'Pending'),
            ('4', 'Confirmed'),
        )
    elif self.status.id == 3:
        status_list = (
            ('2', 'Cancelled'),
            ('3', 'Pending'),
            ('4', 'Confirmed'),
        )
    elif self.status.id == 4:
        status_list = (
            ('2', 'Cancelled'),
            ('4', 'Confirmed'),
            ('5', 'Reschedule confirmed'),
        )
    elif self.status.id == 5:
        status_list = (
            ('2', 'Cancelled'),
            ('5', 'Reschedule confirmed'),
        )
    elif self.status.id == 6:
        status_list = (
            ('4', 'Confirmed'),
            ('5', 'Reschedule confirmed'),
            ('6', 'Completed'),
        )
    return status_list


def get_doctor_list():
    doc = User.objects.filter(is_doctor=1).exclude(is_staff=1)
    return doc


class AptmtCreateForm(forms.ModelForm):
    preferred_doctor = forms.CharField(required=False, label='Preferred Doctor',
                                       widget=forms.TextInput(attrs={
                                           'placeholder': 'Enter doctor name, or leave it blank if you do not know any doctor'}
                                       ))
    appointment_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                               widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                               initial=datetime.now(), label='Preferred Date&Time')
    speciality = forms.ModelChoiceField(queryset=DoctorSpeciality.objects.all().order_by('name'), label='Speciality')
    # clinic = forms.ModelChoiceField(queryset=Clinic.objects.none(), label='Clinic')
    self_description = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Tell us about how you feel'}
    ), required=False, label='Self Description')

    class Meta:
        model = Appointment
        fields = ['appointment_datetime', 'speciality', 'clinic', 'preferred_doctor', 'self_description', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clinic'].queryset = Clinic.objects.none()

        if 'speciality' in self.data:
            try:
                speciality_id = int(self.data.get('speciality'))
                self.fields['clinic'].queryset = Clinic.objects.filter(
                    Q(doctor_at_clinic__user__is_doctor=True)
                    & Q(doctor_at_clinic__user__is_staff=False)
                    & Q(doctor_at_clinic__speciality__id=speciality_id)
                    | Q(doctor_at_clinic__second_speciality__id=speciality_id)) \
                    .distinct().order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty clinic queryset
                # elif self.instance.pk:
                #     self.fields['clinic'].queryset = self.instance.speciality.city_set.order_by('name')


class AptmtUpdateByUserForm(forms.ModelForm):
    preferred_doctor = forms.CharField(required=False, label='Preferred Doctor')
    appointment_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                               widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                               label='Preferred Date&Time')

    self_description = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Tell us about how you feel'}
    ), required=False, label='Self Description')

    class Meta:
        model = Appointment
        fields = ['appointment_datetime', 'speciality', 'clinic', 'preferred_doctor', 'self_description', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clinic'].queryset = Clinic.objects.none()
        # self.fields['doctor'].queryset = User.objects.none()
        # self.fields['doctor'].required = False

        if 'speciality' in self.data:
            try:
                speciality_id = int(self.data.get('speciality'))
                self.fields['clinic'].queryset = Clinic.objects.filter(
                    Q(doctor_at_clinic__user__is_doctor=True)
                    & Q(doctor_at_clinic__user__is_staff=False)
                    & Q(doctor_at_clinic__speciality__id=speciality_id)
                    | Q(doctor_at_clinic__second_speciality__id=speciality_id)) \
                    .distinct().order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty clinic queryset
        elif self.instance.pk:
            self.fields['clinic'].queryset = \
                Clinic.objects.filter(
                    Q(doctor_at_clinic__speciality=self.instance.speciality)
                    | Q(doctor_at_clinic__second_speciality=self.instance.speciality)
                ).distinct().order_by('name')


class AptmtUpdateByAdminForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=get_doctor_list(), label='Doctor', required=False)
    appointment_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                               widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                               label='Actual Date&Time')

    class Meta:
        model = Appointment
        fields = ['appointment_datetime', 'speciality', 'clinic', 'preferred_doctor', 'doctor', 'status',
                  'self_description', ]

    def __init__(self, *args, **kwargs):
        super(AptmtUpdateByAdminForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = get_available_status4admin(self.instance)
        self.fields['clinic'].queryset = Clinic.objects.none()
        self.fields['preferred_doctor'].widget.attrs['readonly'] = True
        self.fields['preferred_doctor'].required = False
        self.fields['preferred_doctor'].label = 'Preferred doctor filled by patient'
        self.fields['self_description'].widget.attrs['readonly'] = True
        self.fields['self_description'].required = False

        if 'speciality' in self.data:
            try:
                speciality_id = int(self.data.get('speciality'))
                self.fields['clinic'].queryset = Clinic.objects.filter(
                    Q(doctor_at_clinic__user__is_doctor=True)
                    & Q(doctor_at_clinic__user__is_staff=False)
                    & Q(doctor_at_clinic__speciality__id=speciality_id)
                    | Q(doctor_at_clinic__second_speciality__id=speciality_id)) \
                    .distinct().order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty clinic queryset
        elif self.instance.pk:
            self.fields['clinic'].queryset = \
                Clinic.objects.filter(
                    Q(doctor_at_clinic__speciality=self.instance.speciality)
                    | Q(doctor_at_clinic__second_speciality=self.instance.speciality)
                ).distinct().order_by('name')


class AptmtUpdateByDoctorForm(forms.ModelForm):
    problems = forms.CharField(widget=forms.Textarea, required=False)
    medications = forms.CharField(widget=forms.Textarea, required=False)
    directives = forms.CharField(widget=forms.Textarea, required=False)
    allergies_and_adverse_reactions = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = MedicalRecord
        fields = ['problems', 'medications', 'directives', 'allergies_and_adverse_reactions']

        # def __init__(self, *args, **kwargs):
        #     super(AptmtUpdateByDoctorForm, self).__init__(*args, **kwargs)


class SiteSettingForm(forms.ModelForm):
    aptmts_per_page = forms.IntegerField(label='Appointments display per page')
    # doc_schedules_per_page = forms.IntegerField(label='Doctor schedules display per page')
    patient_view_med_records_choices = [('True', 'Yes'),
                                        ('False', 'No'), ]
    patient_view_med_records = forms.ChoiceField(choices=patient_view_med_records_choices,
                                                 widget=forms.RadioSelect,
                                                 initial=SiteSetting.objects.get(scope=0).patient_view_med_records,
                                                 label='Patients can view their own medical records in detail page')

    class Meta:
        model = SiteSetting
        fields = ['aptmts_per_page', 'patient_view_med_records', ]


class DocScheduleCreateByAdminForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=get_doctor_list(), label='Select a Doctor')
    start_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                         widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                         initial=datetime.now(), label='Start Date&Time')
    end_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                       widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                       initial=datetime.now(), label='Preferred Date&Time')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Remarks')

    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'start_datetime', 'end_datetime', 'notes']


class DocScheduleUpdateByAdminForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=get_doctor_list(), label='Select a Doctor')
    start_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                         widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                         label='Start Date&Time')
    end_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                       widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                       label='Preferred Date&Time')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Remarks')

    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'start_datetime', 'end_datetime', 'notes']


class DocScheduleCreateByDoctorForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                         widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                         initial=datetime.now(), label='Start Date&Time')
    end_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                       widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                       initial=datetime.now(), label='Preferred Date&Time')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Remarks')

    class Meta:
        model = DoctorSchedule
        fields = ['start_datetime', 'end_datetime', 'notes']


class DocScheduleUpdateByDoctorForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                         widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                         label='Start Date&Time')
    end_datetime = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                       widget=DateTimePickerInput(format='%d %b %Y, %H:%M'),
                                       label='Preferred Date&Time')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Remarks')

    class Meta:
        model = DoctorSchedule
        fields = ['start_datetime', 'end_datetime', 'notes']


class FlatTextPageUpdateForm(forms.ModelForm):
    # content = forms.CharField(widget=forms.Textarea, required=False)
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 70, 'rows': 20}), required=False)

    class Meta:
        model = FlatPage
        fields = ['content']


class ClinicCreateOrUpdateForm(forms.ModelForm):
    contact_number = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)
    operating_time_from = forms.TimeField(widget=TimePickerInput(format='%H:%M'), label='Operating Time From',
                                          required=False)
    operating_time_to = forms.TimeField(widget=TimePickerInput(format='%H:%M'), label='Operating Time To',
                                        required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    additional_info = forms.CharField(widget=forms.Textarea, required=False, label='Additional Information')

    class Meta:
        model = Clinic
        fields = ['name', 'contact_number', 'email', 'operating_time_from', 'operating_time_to', 'address',
                  'additional_info']


class AptmtSearchFilterForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, required=False)
    status = forms.ModelChoiceField(queryset=all_aptmt_status(), label='Status', required=False)
    speciality = forms.ModelChoiceField(queryset=all_speciality(), label='Speciality', required=False)
    # date_range =
