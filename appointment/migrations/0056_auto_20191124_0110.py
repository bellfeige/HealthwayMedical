# Generated by Django 2.2.5 on 2019-11-24 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0055_delete_largecontext'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appointment_datetime',
            field=models.DateTimeField(),
        ),
    ]
