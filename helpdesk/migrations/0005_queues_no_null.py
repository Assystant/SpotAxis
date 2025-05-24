# -*- coding: utf-8 -*-


from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):
    """
    Migration to update ManyToManyField definitions on several models related to queues.

    This migration modifies the 'queues' field in the following models: 
    - EscalationExclusion
    - IgnoreEmail
    - PresetReply

    Each altered field now includes a help text explaining that leaving the field blank
    means the entry applies to all queues, while selecting specific queues limits
    the effect to those queues only.

    Attributes:
        dependencies (list): List of migration dependencies that must be applied before this migration.
        operations (list): List of migration operations altering fields in the specified models.

    Operations:
        AlterField for 'queues' on:
            - EscalationExclusion: ManyToManyField to 'Queue' with a descriptive help_text.
            - IgnoreEmail: ManyToManyField to 'Queue' with a descriptive help_text.
            - PresetReply: ManyToManyField to 'Queue' with a descriptive help_text.
    """


    dependencies = [
        ('helpdesk', '0004_add_per_queue_staff_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escalationexclusion',
            name='queues',
            field=models.ManyToManyField(help_text='Leave blank for this exclusion to be applied to all queues, or select those queues you wish to exclude with this entry.', to='helpdesk.Queue', blank=True),
        ),
        migrations.AlterField(
            model_name='ignoreemail',
            name='queues',
            field=models.ManyToManyField(help_text='Leave blank for this e-mail to be ignored on all queues, or select those queues you wish to ignore this e-mail for.', to='helpdesk.Queue', blank=True),
        ),
        migrations.AlterField(
            model_name='presetreply',
            name='queues',
            field=models.ManyToManyField(help_text='Leave blank to allow this reply to be used for all queues, or select those queues you wish to limit this reply to.', to='helpdesk.Queue', blank=True),
        ),
    ]
