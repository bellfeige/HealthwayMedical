# Generated by Django 2.2.5 on 2019-10-23 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20191023_2014'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Speciality',
            new_name='DoctorSpeciality',
        ),
    ]
