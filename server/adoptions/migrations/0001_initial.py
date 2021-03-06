# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-05 21:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0003_auto_20171120_1005'),
        ('recipients', '0002_auto_20171127_1122'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adoption',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('status', models.CharField(choices=[('PENDING_APPROVAL', 'Pending approval'), ('APPROVED', 'Approved'), ('DENIED', 'Rejected'), ('CANCELED', 'Canceled')], default='PENDING_APPROVAL', max_length=30, verbose_name='Status')),
                ('status_set_at', models.DateTimeField(auto_now_add=True, verbose_name='Status set at')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('adopter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='adoptions', to='users.UserProfile', verbose_name='Adopter')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='adoptions', to='recipients.Recipient', verbose_name='Recipient')),
            ],
            options={
                'verbose_name': 'Adoption',
                'verbose_name_plural': 'Adoptions',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('planned_delivery_date', models.DateField(blank=True, null=True, verbose_name='Planned delivery date')),
                ('package_description', models.TextField(blank=True, verbose_name='Package description')),
                ('delivery_description', models.TextField(blank=True, verbose_name='Delivery description')),
                ('status', models.CharField(choices=[('PLANNED', 'Planned'), ('PENDING', 'Pending'), ('DELIVERED', 'Delivered'), ('CANCELED', 'Canceled')], default='PLANNED', max_length=20, verbose_name='Status')),
                ('status_set_at', models.DateTimeField(auto_now_add=True, verbose_name='Status set at')),
                ('delivery_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='users.UserProfile', verbose_name='Delivery from')),
                ('delivery_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='recipients.Recipient', verbose_name='Delivery to')),
            ],
            options={
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
            },
        ),
        migrations.CreateModel(
            name='PackageType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('name', models.CharField(max_length=70, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Package type',
                'verbose_name_plural': 'Package types',
            },
        ),
        migrations.AddField(
            model_name='delivery',
            name='package_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='adoptions.PackageType', verbose_name='Package type'),
        ),
    ]
