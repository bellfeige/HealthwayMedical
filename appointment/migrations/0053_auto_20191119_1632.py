# Generated by Django 2.2.5 on 2019-11-19 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0052_auto_20191119_1631'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='p_doctor',
            new_name='preferred_doctor',
        ),
    ]
