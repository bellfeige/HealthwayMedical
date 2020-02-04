# Generated by Django 2.2.5 on 2019-11-19 08:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0048_delete_largecontext'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='preferred_doctor',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_doctor', to=settings.AUTH_USER_MODEL),
        ),
    ]
