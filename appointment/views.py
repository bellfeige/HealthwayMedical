from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.contrib.flatpages.models import FlatPage
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404, redirect
import calendar
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime, timedelta, date
from .models import Appointment, Status, MedicalRecord, SiteSetting, DoctorSchedule, Clinic
from users.models import User
from .forms import (
    AptmtUpdateByAdminForm,
    AptmtCreateForm,
    AptmtUpdateByUserForm,
    AptmtUpdateByDoctorForm,
    SiteSettingForm,
    DocScheduleCreateByAdminForm,
    DocScheduleUpdateByAdminForm,
    DocScheduleCreateByDoctorForm,
    DocScheduleUpdateByDoctorForm,
    FlatTextPageUpdateForm,
    ClinicCreateOrUpdateForm,
)
from .filters import AptmtFilter, AptmtForDoctorFilter
from .utils import Calendar


def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


class AllAptmtCalendarView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'appointment/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['current_view'] = 'cal'
        return context

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class MyAptmtCalendarView(LoginRequiredMixin, ListView):
    # model = Appointment
    template_name = 'appointment/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['current_view'] = 'cal'
        return context

    def get_queryset(self):
        queryset = Appointment.objects.filter(patient=self.request.user).order_by('-create_datetime')
        return queryset


class DoctorAptmtCalendarView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    # model = Appointment
    template_name = 'appointment/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['current_view'] = 'cal'
        return context

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
        return queryset

    def get_queryset(self):
        queryset = Appointment.objects.filter(doctor=self.request.user, status__status='confirmed') \
                   | Appointment.objects.filter(doctor=self.request.user, status__status='reschedule_confirmed') \
                   | Appointment.objects.filter(doctor=self.request.user, status__status='completed') \
                       .order_by('-create_datetime')
        return queryset

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_doctor and \
                self.request.user.is_patient is False and \
                self.request.user.is_staff is False and \
                self.request.user.is_superuser is False:
            return True
        return False


class AptmtDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'appointment/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AptmtDetailView, self).get_context_data(*args, **kwargs)
        context['patient_view_med_records'] = SiteSetting.objects.get(scope=0).patient_view_med_records
        return context

    def test_func(self):
        appointment = self.get_object()
        if self.request.user == appointment.patient or \
                self.request.user == appointment.doctor or \
                self.request.user.is_staff:
            return True
        return False


class AptmtDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Appointment
    template_name = 'appointment/delete.html'
    success_url = '/appointment/all/'
    success_message = f'The appointment is deleted successfully'

    def get_context_data(self, *args, **kwargs):
        context = super(AptmtDeleteView, self).get_context_data(*args, **kwargs)
        context['item'] = 'appointment'
        return context

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_superuser:
            return True
        return False


class AptmtCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Appointment
    template_name = 'appointment/create.html'
    form_class = AptmtCreateForm
    success_message = f'Your appointment is submitted successfully. Our staff will reach you ASAP.'

    def form_valid(self, form):

        now = datetime.now().strftime("%y%m%d%H%M%S")
        f = self.request.user.first_name[0].upper()
        l = self.request.user.last_name[0].upper()
        if self.request.user.is_patient:
            d = self.request.user.patient_profile.date_of_birth.strftime("%Y%m%d")
            g = self.request.user.patient_profile.gender.upper()
        appointment_number = f'HWM{f}{l}{d}{g}{now}'

        form.instance.appointment_number = appointment_number
        form.instance.patient = self.request.user
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_patient and self.request.user.patient_profile.completed_percentage == 100:
            return True
        return False


def load_clinics(request):
    speciality_id = request.GET.get('speciality')
    clinics = Clinic.objects.filter(Q(doctor_at_clinic__user__is_doctor=True)
                                    & Q(doctor_at_clinic__user__is_staff=False)
                                    & Q(doctor_at_clinic__speciality__id=speciality_id)
                                    | Q(doctor_at_clinic__second_speciality__id=speciality_id)) \
        .distinct().order_by('name')
    return render(request, 'appointment/snippets/clinic_dropdown_list_options.html', {'clinics': clinics})


# def load_doctors(request):
#     speciality_id = request.GET.get('speciality')
#     clinic_id = request.GET.get('clinic')
#     doctors = User.objects.filter(
#         Q(is_doctor=True)
#         & Q(is_staff=False)
#         & Q(doctor_profile__at_clinic__id=clinic_id)
#         & Q(doctor_profile__speciality__id=speciality_id)).distinct().order_by('first_name') \
#               | User.objects.filter(
#         Q(is_doctor=True)
#         & Q(is_staff=False)
#         & Q(doctor_profile__at_clinic__id=clinic_id)
#         & Q(doctor_profile__second_speciality__id=speciality_id)).distinct().order_by('first_name')
#     return render(request, 'appointment/snippets/doctor_dropdown_list_options.html', {'doctors': doctors})


class DocScheduleCreateByAdminView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = DoctorSchedule
    template_name = 'appointment/doc_schedule_create_by_admin.html'
    form_class = DocScheduleCreateByAdminForm
    success_url = '/doctor-schedule/all/'
    success_message = f'New doctor schedule is added successfully'

    def form_valid(self, form):
        form.instance.create_by = self.request.user
        form.instance.create_datetime = datetime.now()
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class DocScheduleCreateByDoctorView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = DoctorSchedule
    template_name = 'appointment/doc_schedule_create_by_doctor.html'
    form_class = DocScheduleCreateByDoctorForm
    success_url = '/doctor-schedule/my/'
    success_message = f'New schedule is added successfully'

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        form.instance.create_by = self.request.user
        form.instance.create_datetime = datetime.now()
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_doctor and self.request.user.is_staff == 0 and self.request.user.is_superuser == 0:
            return True
        return False


class DocScheduleDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = DoctorSchedule
    template_name = 'appointment/delete.html'
    success_message = f'Deleted successfully'

    def get_success_url(self):
        schedule = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return '/doctor-schedule/all/'
        elif schedule.doctor == self.request.user:
            return '/doctor-schedule/my/'

    def get_context_data(self, *args, **kwargs):
        context = super(DocScheduleDeleteView, self).get_context_data(*args, **kwargs)
        context['item'] = 'schedule'
        return context

    def test_func(self):
        schedule = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser or schedule.doctor == self.request.user:
            return True
        return False


class AptmtUpdateByUserView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Appointment
    template_name = 'appointment/aptmt_update_by_user.html'
    form_class = AptmtUpdateByUserForm
    success_message = f'Appointment updated successfully'

    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        appointment = self.get_object()
        if self.request.user.is_patient and appointment.patient == self.request.user \
                and appointment.status.status == 'submitted' or self.request.user.is_staff:
            return True
        return False


class AptmtUpdateByAdminView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Appointment
    template_name = 'appointment/aptmt_update_by_admin.html'
    form_class = AptmtUpdateByAdminForm
    success_message = f'Appointment updated successfully'

    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class DocScheduleUpdateByAdminView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = DoctorSchedule
    template_name = 'appointment/doc_schedule_update_by_admin.html'
    form_class = DocScheduleUpdateByAdminForm
    success_message = f'Updated successfully'
    success_url = '/doctor-schedule/all/'

    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        # docSchedule = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class DocScheduleUpdateByDoctorView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = DoctorSchedule
    template_name = 'appointment/doc_schedule_update_by_doctor.html'
    form_class = DocScheduleUpdateByDoctorForm
    success_message = f'Updated successfully'
    success_url = '/doctor-schedule/my/'

    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        # docSchedule = self.get_object()
        if self.request.user.is_doctor and self.request.user.is_staff == 0 and self.request.user.is_superuser == 0:
            return True
        return False


class MedRecordUpdateByDoctorView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    # model = Appointment
    model = MedicalRecord
    slug_field = 'appointment_id'
    slug_url_kwarg = 'appointment_id'
    template_name = 'appointment/medical_record_update_by_doctor.html'
    form_class = AptmtUpdateByDoctorForm
    success_message = f'Case record saved successfully'

    def form_valid(self, form):
        # form.instance.problems = 'test'
        form.instance.last_updated_by = self.request.user
        form.instance.last_updated_datetime = datetime.now()
        form.instance.appointment.last_updated_by = self.request.user
        form.instance.appointment.last_updated_datetime = datetime.now()
        return super().form_valid(form)

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_doctor and self.request.user.is_staff == 0 and self.request.user.is_superuser == 0:
            return True
        return False


class AptmtCancelByUserView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Appointment
    template_name = 'appointment/aptmt_cancel_by_user.html'
    success_message = f'Your appointment is cancelled'

    fields = []

    def form_valid(self, form):
        form.instance.status = Status.objects.get(id=2)
        return super().form_valid(form)

    def test_func(self):
        appointment = self.get_object()
        if self.request.user == appointment.patient \
                and appointment.status.status == 'submitted' \
                or self.request.user.is_staff:
            return True
        return False


class AptmtCompeteByDoctorView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Appointment
    template_name = 'appointment/aptmt_complete_by_doctor.html'
    success_message = f'Set to completed successfully'

    fields = []

    def form_valid(self, form):
        form.instance.status = Status.objects.get(id=6)
        return super().form_valid(form)

    def test_func(self):
        appointment = self.get_object()
        if self.request.user == appointment.doctor and self.request.user.is_doctor and (
                appointment.status.id == 4 or appointment.status.id == 5):
            return True
        return False


class AptmtFilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # queryset = super().get_queryset()
        queryset = Appointment.objects.all().order_by('-create_datetime')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        context['filterset'] = self.filterset
        context['current_view'] = 'list'
        return context


class AllAptmtListView(LoginRequiredMixin, UserPassesTestMixin, AptmtFilteredListView):
    filterset_class = AptmtFilter
    template_name = 'appointment/all_aptmts.html'
    model = Appointment
    context_object_name = 'aptmts'

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
        return queryset

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


# class AllAptmtListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     model = Appointment
#     template_name = 'appointment/all_aptmts.html'
#     context_object_name = 'aptmts'
#
#     def get_context_data(self, **kwargs):
#         context = super(AllAptmtListView, self).get_context_data(**kwargs)
#         context['form'] = AptmtFilter.form
#         return context
#
#     def get_paginate_by(self, queryset):
#         queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
#         return queryset
#
#     # def form_valid(self, form):
#     #     return super().form_valid(form)
#
#     def test_func(self):
#         # appointment = self.get_object()
#         if self.request.user.is_staff or self.request.user.is_superuser:
#             return True
#         return False


class AllDoctorScheduleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DoctorSchedule
    template_name = 'appointment/all_doc_schedule.html'
    context_object_name = 'docSchedules'
    ordering = ['-create_datetime']

    # paginate_by = 10

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).doc_schedules_per_page
        return queryset

    # def form_valid(self, form):
    #     return super().form_valid(form)

    def test_func(self):
        # docSchedules = self.get_object()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class MyScheduleListView(LoginRequiredMixin, ListView):
    model = DoctorSchedule
    template_name = 'appointment/my_schedule.html'
    context_object_name = 'docSchedules'

    # paginate_by = 10

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).doc_schedules_per_page
        return queryset

    def get_queryset(self):
        return DoctorSchedule.objects.filter(doctor=self.request.user).order_by('-create_datetime')


class MyAptmtListView(LoginRequiredMixin, AptmtFilteredListView):
    filterset_class = AptmtFilter
    model = Appointment
    template_name = 'appointment/my_aptmts.html'
    context_object_name = 'aptmts'

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
        return queryset

    def get_queryset(self):
        queryset = Appointment.objects.filter(patient=self.request.user).order_by('-create_datetime')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    # def get_queryset(self):
    #     return Appointment.objects.filter(patient=self.request.user).order_by('-create_datetime')


class DoctorAptmtListView(LoginRequiredMixin, UserPassesTestMixin, AptmtFilteredListView):
    filterset_class = AptmtForDoctorFilter
    model = Appointment
    template_name = 'appointment/doc_aptmts.html'
    context_object_name = 'aptmts'

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
        return queryset

    def get_queryset(self):
        queryset = Appointment.objects.filter(doctor=self.request.user, status__status='confirmed') \
                   | Appointment.objects.filter(doctor=self.request.user, status__status='reschedule_confirmed') \
                   | Appointment.objects.filter(doctor=self.request.user, status__status='completed') \
                       .order_by('-create_datetime')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_doctor and \
                self.request.user.is_patient is False and \
                self.request.user.is_staff is False and \
                self.request.user.is_superuser is False:
            return True
        return False


class SiteSettingUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = SiteSetting
    template_name = 'appointment/site_setting.html'
    form_class = SiteSettingForm
    slug_field = 'scope'
    slug_url_kwarg = 'scope'
    success_url = '/site-settings/0/'
    success_message = f'Site settings saved successfully'

    def get_context_data(self, *args, **kwargs):
        context = super(SiteSettingUpdateView, self).get_context_data(*args, **kwargs)
        context['clinics'] = Clinic.objects.all().order_by('name')
        return context

    def form_valid(self, form):
        # form.instance.status = Status.objects.get(id=7)
        return super().form_valid(form)

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_staff:
            return True
        return False


def check_profile_complete(request):
    if request.user.is_patient:
        profile_complete_percentage = request.user.patient_profile.completed_percentage
        if profile_complete_percentage == 100:
            return redirect('aptmt-create')
        else:
            context = {
                'title': 'Profile Not Complete',
                'profile_complete_percentage': profile_complete_percentage
            }
            return render(request, 'appointment/check_profile_complete.html', context)
    else:
        return redirect('home')


class ClinicListView(ListView):
    model = Clinic
    template_name = 'appointment/clinics.html'
    context_object_name = 'clinics'
    paginate_by = 5


class ClinicUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Clinic
    template_name = 'appointment/clinic-update.html'
    form_class = ClinicCreateOrUpdateForm
    # success_url = '/clinics/'
    success_message = f'Clinic information updated successfully'

    def form_valid(self, form):
        # form.instance.status = Status.objects.get(id=7)
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class ClinicCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Clinic
    template_name = 'appointment/clinic-create.html'
    form_class = ClinicCreateOrUpdateForm
    # success_url = '/clinics/'
    success_message = f'New clinic is added successfully'

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class ClinicDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Clinic
    template_name = 'appointment/delete.html'
    success_url = '/site-settings/0/'
    success_message = f'The clinic is deleted successfully'

    def get_context_data(self, *args, **kwargs):
        context = super(ClinicDeleteView, self).get_context_data(*args, **kwargs)
        context['item'] = 'clinic'
        return context

    def test_func(self):
        # appointment = self.get_object()
        if self.request.user.is_superuser:
            return True
        return False


class ClinicDetailView(DetailView):
    model = Clinic
    template_name = 'appointment/clinic-detail.html'
    context_object_name = 'clinic'


class DoctorListView(ListView):
    # model = User
    queryset = User.objects.filter(is_doctor=1).exclude(is_staff=1)
    template_name = 'appointment/doctors.html'
    context_object_name = 'doctors'

    def get_paginate_by(self, queryset):
        queryset = SiteSetting.objects.get(scope=0).aptmts_per_page
        return 5


class DoctorDetailView(DetailView):
    queryset = User.objects.filter(is_doctor=1).exclude(is_staff=1)
    template_name = 'appointment/doctor-detail.html'
    context_object_name = 'doctor'


def home(request):
    context = {
        'title': 'Homepage',
    }
    return render(request, 'appointment/home.html', context)


class FlatTextPageUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = FlatPage
    template_name = 'appointment/flat_text_page_update.html'
    form_class = FlatTextPageUpdateForm
    success_message = f'Updated successfully'

    def get_success_url(self):
        flat_text_page = self.get_object()
        return flat_text_page.url

    def get_context_data(self, *args, **kwargs):
        flat_text_page = self.get_object()
        context = super(FlatTextPageUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = flat_text_page.title
        return context

    def form_valid(self, form):
        # form.instance.status = Status.objects.get(id=7)
        return super().form_valid(form)

    def test_func(self):
        # flat_text_page = self.get_object()
        if self.request.user.is_superuser:
            return True
        return False
