# Generated by Django 2.0 on 2018-01-19 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_auto_20171230_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityday',
            name='display_in_website',
            field=models.BooleanField(default=True, verbose_name='Display in website'),
        ),
    ]
