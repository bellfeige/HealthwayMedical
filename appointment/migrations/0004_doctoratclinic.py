# Generated by Django 2.2.5 on 2019-10-23 12:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0003_delete_speciality'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorAtClinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointment.Clinic')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
    ]
