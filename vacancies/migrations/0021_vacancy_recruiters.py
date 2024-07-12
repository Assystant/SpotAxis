# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-22 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0011_auto_20160920_1740'),
        ('vacancies', '0020_auto_20160913_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='recruiters',
            field=models.ManyToManyField(default=None, to='companies.Recruiter', verbose_name=b'Recruiter'),
        ),
    ]