# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-14 00:39


from __future__ import absolute_import
from django.db import migrations, models
import vacancies.models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0045_auto_20170314_0027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='unpub_date',
            field=models.DateField(default=vacancies.models.get_30_days_later, verbose_name='Date of unpublication'),
        ),
    ]
