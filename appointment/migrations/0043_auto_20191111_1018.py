# Generated by Django 2.2.5 on 2019-11-11 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0042_sitesetting_schedule_per_page'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sitesetting',
            old_name='paginate_by',
            new_name='aptmts_per_page',
        ),
        migrations.AlterField(
            model_name='sitesetting',
            name='schedule_per_page',
            field=models.SmallIntegerField(default=10),
        ),
    ]
