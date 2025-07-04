"""
Migration to extend the Company model with employee count.

Changes made:
- Added the `no_of_employees` field to the `Company` model.

Purpose:
This addition enables the system to store and manage information about
the number of employees in a company, which can be used for filtering,
reporting, or analytics.
"""


# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-21 13:02


from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):
    """Django Migration Class to Add 'no_of_employees' Field to Company Model."""
    dependencies = [
        ('companies', '0003_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='no_of_employees',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='No of Employees'),
        ),
    ]
