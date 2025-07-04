# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-11-05 10:43

"""
Migration to update model options and constraints for Transactions and PriceSlab.

This migration performs the following changes:
- Updates the verbose names and ordering for the `Transactions` model.
- Modifies the unique constraint on `PriceSlab` to include the `package` field
  along with `currency` and `slab_period`.

Dependencies:
    - payments.0002_auto_20161105_1039
"""

from __future__ import absolute_import
from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration class to apply model options and unique constraint updates.

    Operations:
        - Alter `Transactions` model options for better naming and ordering.
        - Update unique together constraint on `PriceSlab` to ('currency', 'slab_period', 'package').
    """
    dependencies = [
        ('payments', '0002_auto_20161105_1039'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transactions',
            options={'ordering': ('-timestamp',), 'verbose_name': 'Transaction', 'verbose_name_plural': 'Transactions'},
        ),
        migrations.AlterUniqueTogether(
            name='priceslab',
            unique_together=set([('currency', 'slab_period', 'package')]),
        ),
    ]
