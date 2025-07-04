# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-08 23:05


from __future__ import absolute_import
from django.db import migrations

"""
Migration Script to Update Verbose Names for Recruiter Model.

This migration alters the model options for the 'Recruiter' model,
specifically updating the human-readable names used in the admin
interface and elsewhere:

- verbose_name: set to 'Recruiter'
- verbose_name_plural: set to 'Recruiters'

These changes improve clarity and consistency in the Django admin UI.

Dependencies:
    - Depends on migration '0004_company_no_of_employees' in the 'companies' app.
"""


class Migration(migrations.Migration):
    """ Migration class to modify Meta options of the Recruiter model."""
    dependencies = [
        ('companies', '0004_company_no_of_employees'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recruiter',
            options={'verbose_name': 'Recruiter', 'verbose_name_plural': 'Recruiters'},
        ),
    ]
