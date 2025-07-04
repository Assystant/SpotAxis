# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-19 23:00


from __future__ import absolute_import
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

"""
Migration to create the RecruiterInvitation model.

This migration introduces the 'RecruiterInvitation' model used to manage
invitations sent by existing users to potential recruiters via email.
The model stores the invitee's email, an invitation token for verification,
and a reference to the user who sent the invitation.

Dependencies:
    - Depends on the swappable AUTH_USER_MODEL setting.
    - Depends on the '0006_auto_20160916_1136' migration in the 'companies' app.
"""

class Migration(migrations.Migration):
    """Migration class to add the RecruiterInvitation model."""
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0006_auto_20160916_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecruiterInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, default=None, max_length=254, null=True, verbose_name=b'email')),
                ('invitation_token', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name=b'token')),
                ('invited_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'Invited by')),
            ],
            options={
                'verbose_name': 'Recruiter Invitation',
                'verbose_name_plural': 'Recruiter Invitations',
            },
        ),
    ]
