# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-17 13:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0037_auto_20170117_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='public_postulate',
            name='pid',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='vacancies.Postulate'),
        ),
    ]