# Generated by Django 2.2.5 on 2019-11-25 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20191125_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorprofile',
            name='contact_number',
            field=models.CharField(max_length=50, null=True),
        ),
    ]