# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-04-02 09:28


from __future__ import absolute_import
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customField', '__first__'),
        ('vacancies', '0049_vacancytags_vacancy'),
    ]

    operations = [
        migrations.AddField(
            model_name='postulate',
            name='custom_form_application',
            field=models.ManyToManyField(default=None, to='customField.FieldValue'),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='has_custom_form',
            field=models.BooleanField(default=False, verbose_name=b'Has Custom Form?'),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='template',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='customField.Template'),
        ),
    ]
