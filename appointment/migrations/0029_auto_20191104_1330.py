# Generated by Django 2.2.5 on 2019-11-04 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0028_auto_20191104_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='can_patient_view_med_records',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_number',
            field=models.CharField(default='INDEX20191104133039', max_length=50),
        ),
    ]
