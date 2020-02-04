# Generated by Django 2.2.5 on 2019-10-31 05:25

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0019_auto_20191031_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medical_record_update_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='last_updated_datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_number',
            field=models.CharField(default='INDEX20191031132516', max_length=50),
        ),
    ]