# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-02 17:23


from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0013_auto_20160902_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='public_postulate',
            name='discard',
            field=models.BooleanField(default=False, verbose_name='Discarded'),
        ),
    ]
