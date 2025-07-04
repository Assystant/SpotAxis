# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-27 10:56


from __future__ import absolute_import
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('action_url', models.URLField(blank=True, default=None, null=True)),
                ('subscribers', models.ManyToManyField(related_name='subscribers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('seen', models.BooleanField(default=False)),
                ('action_url', models.URLField(blank=True, default=None, null=True)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'NotificationTemplate',
                'verbose_name_plural': 'NotificationTemplates',
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplateVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('var_name', models.CharField(max_length=50)),
                ('var_name_plural', models.CharField(max_length=50)),
                ('order', models.PositiveSmallIntegerField()),
                ('slug', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'NotificationTemplateVariable',
                'verbose_name_plural': 'NotificationTemplateVariables',
            },
        ),
        migrations.AddField(
            model_name='notificationtemplate',
            name='variables',
            field=models.ManyToManyField(to='activities.NotificationTemplateVariable'),
        ),
        migrations.AddField(
            model_name='notification',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activities.NotificationTemplate'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
