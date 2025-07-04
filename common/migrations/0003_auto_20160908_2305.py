# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-08 23:05


from __future__ import absolute_import
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20160902_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True, unique=True, verbose_name=b'Name')),
                ('symbol', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'Symbol')),
                ('symbol_native', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'Native Symbol')),
                ('decimal_digits', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'No of Decimal Digits')),
                ('rounding', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'Rounding')),
                ('code', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'Code')),
                ('name_plural', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True, verbose_name=b'Plural Name')),
            ],
            options={
                'ordering': ['code'],
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name': 'Country', 'verbose_name_plural': 'Countries'},
        ),
    ]
