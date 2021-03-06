# Generated by Django 2.2.5 on 2019-11-04 02:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0024_auto_20191102_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteDefaultSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paginate_by', models.PositiveSmallIntegerField(default=8)),
                ('can_patient_view_med_records', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_number',
            field=models.CharField(default='INDEX20191104104117', max_length=50),
        ),
        migrations.CreateModel(
            name='DoctorSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('end_datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
