# Generated by Django 2.2.5 on 2019-10-26 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0008_auto_20191026_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appointment_number',
            field=models.CharField(default='INDEX20190926', max_length=50),
        ),
    ]