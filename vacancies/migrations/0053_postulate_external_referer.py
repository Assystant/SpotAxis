# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-10-11 19:12


from __future__ import absolute_import
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0021_externalreferal'),
        ('vacancies', '0052_auto_20170402_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='postulate',
            name='external_referer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='companies.ExternalReferal'),
        ),
    ]
