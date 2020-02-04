import django_filters
from django_filters.widgets import RangeWidget
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Appointment

today = datetime.today()

CHOICES = (
    (-7, 'in the PAST 7 days'),
    (-30, 'in the PAST 30 days'),
    (-90, 'in the PAST 90 days'),
    (7, 'in the NEXT 7 days'),
    (30, 'in the NEXT 30 days'),
    (90, 'in the NEXT 90 days'),
)

DOC_STATUS_CHOICES = (
    (4, 'Confirmed'),
    (5, 'Reschedule Confirmed'),
    (6, 'Completed'),
)


class AptmtFilter(django_filters.FilterSet):
    # first_name = django_filters.CharFilter(lookup_expr='icontains')
    # status = django_filters.ChoiceFilter(lookup_expr='exact')
    # name = django_filters.CharFilter(field_name='Name', method='filter_by_name')
    date_range = django_filters.ChoiceFilter(label='Scheduled Date', choices=CHOICES, method='filter_by_date')

    # date_range2 = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))

    class Meta:
        model = Appointment
        fields = ['status', 'speciality', ]

    # def filter_by_name(self, queryset, name, value):
    #     return queryset.get(patient__icontains=value)

    def filter_by_date(self, queryset, name, value):
        target_day = today + timedelta(days=int(value))
        if int(value) > 0:
            return queryset.filter(appointment_datetime__range=[today, target_day])
        elif int(value) < 0:
            return queryset.filter(appointment_datetime__range=[target_day, today])


class AptmtForDoctorFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(label='Status', choices=DOC_STATUS_CHOICES, method='filter_by_status')
    date_range = django_filters.ChoiceFilter(label='Scheduled Date', choices=CHOICES, method='filter_by_date')

    class Meta:
        model = Appointment
        fields = ['speciality', ]

    def filter_by_status(self, queryset, name, value):
        return queryset.filter(status_id=int(value))

    def filter_by_date(self, queryset, name, value):
        target_day = today + timedelta(days=int(value))
        if int(value) > 0:
            return queryset.filter(appointment_datetime__range=[today, target_day])
        elif int(value) < 0:
            return queryset.filter(appointment_datetime__range=[target_day, today])
