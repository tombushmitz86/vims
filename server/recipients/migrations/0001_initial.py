# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-21 20:38
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('geography', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('phone', models.CharField(max_length=25, validators=[django.core.validators.RegexValidator('^[0-9() -]{6,25}$')], verbose_name='Phone')),
                ('street_number', models.IntegerField(verbose_name='Street number')),
                ('floor', models.SmallIntegerField(verbose_name='Floor')),
                ('apartment', models.IntegerField(verbose_name='Apartment')),
                ('background_story', models.TextField(blank=True, verbose_name='Background story')),
                ('number_of_people', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Number of people')),
                ('recipient_tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('holocaust-survivor', 'Holocaust survivor'), ('handicapped', 'Handicapped'), ('avrech', 'Avrech'), ('galmud', 'Galmud'), ('new-immigrant', 'New immigrant'), ('unhealthy', 'Unhealthy'), ('senior-citizen', 'Senior citizen')], max_length=30, verbose_name='Recipient tag'), size=None, verbose_name='Recipient tags')),
                ('display_in_website', models.BooleanField(default=True, verbose_name='Display in website')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('blacklisted', models.BooleanField(default=False, verbose_name='Blacklisted')),
                ('street', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recipients', to='geography.Street', verbose_name='Street')),
            ],
            options={
                'verbose_name': 'Recipient',
                'verbose_name_plural': 'Recipients',
            },
        ),
    ]
