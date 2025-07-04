# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-11-05 12:05


from __future__ import absolute_import
from django.db import migrations, models
import django.db.models.deletion

"""
Migration to add ServiceCategory model and link it to Services.

This migration performs the following operations:
- Creates a new model `ServiceCategory` with fields:
  - id: Auto-increment primary key
  - name: Optional name of the category
  - codename: Optional short code for the category
- Adds a foreign key field `category` to the existing `Services` model, 
  linking each service to a service category.

Dependencies:
    - payments.0003_auto_20161105_1043
"""

class Migration(migrations.Migration):
    """
    Migration class to add ServiceCategory model and category field to Services.
    
    Operations:
        - Create ServiceCategory model.
        - Add ForeignKey 'category' field to Services model.
    """
    dependencies = [
        ('payments', '0003_auto_20161105_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('codename', models.CharField(blank=True, default=None, max_length=5, null=True)),
            ],
            options={
                'verbose_name': 'ServiceCategory',
                'verbose_name_plural': 'ServiceCategories',
            },
        ),
        migrations.AddField(
            model_name='services',
            name='category',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.ServiceCategory'),
        ),
    ]
