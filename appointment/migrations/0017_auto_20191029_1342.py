# Generated by Django 2.2.5 on 2019-10-29 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0016_auto_20191028_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='colour',
            field=models.CharField(max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_number',
            field=models.CharField(default='INDEX20194229', max_length=50),
        ),
    ]