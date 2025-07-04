# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-22 18:57


from __future__ import absolute_import
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0011_auto_20160920_1740'),
        ('vacancies', '0021_vacancy_recruiters'),
    ]

    operations = [
        migrations.CreateModel(
            name='Postulate_Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name=b'Criteria Name')),
                ('score', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Applicant Stage',
                'verbose_name_plural': 'Applicant Stages',
            },
        ),
        migrations.CreateModel(
            name='Postulate_Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Applicant Stage',
                'verbose_name_plural': 'Applicant Stages',
            },
        ),
        migrations.CreateModel(
            name='Public_Postulate_Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Public Applicant Stage',
                'verbose_name_plural': 'Public Applicant Stages',
            },
        ),
        migrations.CreateModel(
            name='StageCriterion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name=b'Criteria Name')),
            ],
            options={
                'verbose_name': 'Stage Criterion',
                'verbose_name_plural': 'Stage Criterion',
            },
        ),
        
    ]
