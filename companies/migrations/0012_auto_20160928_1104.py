# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-28 11:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0011_auto_20160920_1740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruiter',
            name='application_process_management',
        ),
        migrations.RemoveField(
            model_name='recruiter',
            name='job_management',
        ),
        migrations.RemoveField(
            model_name='recruiter',
            name='site_management',
        ),
        migrations.RemoveField(
            model_name='recruiter',
            name='team_management',
        ),
        migrations.AddField(
            model_name='recruiter',
            name='membership',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]