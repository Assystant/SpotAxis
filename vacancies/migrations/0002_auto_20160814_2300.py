# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-14 23:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancy',
            name='area',
        ),
        migrations.RemoveField(
            model_name='vacancy',
            name='municipal',
        ),
        migrations.RemoveField(
            model_name='vacancy',
            name='state',
        ),
    ]