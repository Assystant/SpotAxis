# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-13 16:12


from __future__ import absolute_import
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0042_auto_20170313_1429'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancy',
            name='scheduled',
        ),
    ]
