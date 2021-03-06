# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-09-11 17:46
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Check',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=30)),
                ('order', django.contrib.postgres.fields.jsonb.JSONField()),
                ('status', models.CharField(max_length=30)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdf/')),
            ],
        ),
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('api_key', models.CharField(max_length=100)),
                ('check_type', models.CharField(max_length=30)),
                ('point_id', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='check',
            name='printer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checks', to='api.Printer'),
        ),
    ]
