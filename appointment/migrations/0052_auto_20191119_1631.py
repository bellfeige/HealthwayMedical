# Generated by Django 2.2.5 on 2019-11-19 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0051_auto_20191119_1623'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='preferred_doctor',
            new_name='p_doctor',
        ),
    ]
