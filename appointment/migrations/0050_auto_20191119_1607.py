# Generated by Django 2.2.5 on 2019-11-19 08:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0049_auto_20191119_1605'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='doctor',
            new_name='actual_doctor',
        ),
    ]