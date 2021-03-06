# Generated by Django 2.0 on 2017-12-29 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDay',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('date', models.DateField(verbose_name='Date')),
                ('logistics_center', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='logistics.LogisticsCenter', verbose_name='Logistics center')),
            ],
            options={
                'verbose_name': 'Activity day',
                'verbose_name_plural': 'Activity day',
            },
        ),
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('description', models.TextField(unique=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Activity type',
                'verbose_name_plural': 'Activity types',
            },
        ),
        migrations.AddField(
            model_name='activityday',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='activities.ActivityType', verbose_name='Type'),
        ),
        migrations.AlterUniqueTogether(
            name='activityday',
            unique_together={('date', 'type', 'logistics_center')},
        ),
    ]
