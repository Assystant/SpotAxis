# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-28 19:48


from __future__ import absolute_import
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0008_auto_20161027_2327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['-last_updated'], 'verbose_name': 'Activity', 'verbose_name_plural': 'Activities'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-last_updated'], 'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
    ]
