from datetime import datetime, timedelta
from calendar import HTMLCalendar
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Status


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(appointment_datetime__day=day)
        d = ''
        for event in events_per_day:
            # if event.doctor is None:
            #     d += f'<div class="cal-event" style="background-color:#{event.status.colour}">' \
            #          f'<a href="{event.get_html_url}" class="font-italic text-white" >' \
            #          f'Doctor Not yet set' \
            #          f'</a></div>'
            # else:
            d += f'<div class="cal-event" style="background-color:#{event.status.colour}">' \
                 f'<a href="{event.get_html_url}" class="text-white" >' \
                 f'{event.patient}' \
                 f'</a></div>'

        if day != 0:
            return f"<td><span class='cal-date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        if self.user.is_superuser or self.user.is_staff:
            events = Appointment.objects.filter(appointment_datetime__year=self.year,
                                                appointment_datetime__month=self.month)
        elif self.user.is_patient:
            events = Appointment.objects.filter(patient=self.user,
                                                appointment_datetime__year=self.year,
                                                appointment_datetime__month=self.month)
        elif self.user.is_doctor and \
                self.user.is_patient is False and \
                self.user.is_staff is False and \
                self.user.is_superuser is False:
            events = Appointment.objects.filter(doctor=self.user, status__status='confirmed') \
                     | Appointment.objects.filter(doctor=self.user, status__status='reschedule_confirmed') \
                     | Appointment.objects.filter(doctor=self.user, status__status='completed') \
                         .order_by('-create_datetime')

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="cal-calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal
