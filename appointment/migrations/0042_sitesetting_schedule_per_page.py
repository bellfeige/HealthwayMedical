# Generated by Django 2.2.5 on 2019-11-11 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0041_doctorschedule_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='schedule_per_page',
            field=models.SmallIntegerField(null=True),
        ),
    ]