# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-20 13:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0008_auto_20160920_1229'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recruiter',
            options={'permissions': (('team_management', 'Team Management'), ('site_management', 'Site Management'), ('job_management', 'Job Management'), ('application_process_management', 'Application Process Management')), 'verbose_name': 'Recruiter', 'verbose_name_plural': 'Recruiters'},
        ),
    ]
