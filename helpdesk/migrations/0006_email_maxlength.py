# -*- coding: utf-8 -*-


from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):
    """
    Migration to alter email-related fields in the Queue, Ticket, and TicketCC models.

    This migration modifies the following fields to allow null and blank values, 
    and adds or updates help text and verbose names:

    - Queue.email_address: EmailField for outgoing emails from the queue.
    Help text clarifies it should match the mailbox email if using IMAP/POP3.

    - Ticket.submitter_email: EmailField for the submitter's email.
    Help text notes the submitter receives emails for all public follow-ups.

    - TicketCC.email: EmailField for CC email addresses of non-user followers.

    Attributes:
        dependencies (list): Migrations that must be applied before this one.
        operations (list): List of AlterField operations updating email fields.
    """

    dependencies = [
        ('helpdesk', '0005_queues_no_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='email_address',
            field=models.EmailField(help_text='All outgoing e-mails for this queue will use this e-mail address. If you use IMAP or POP3, this should be the e-mail address for that mailbox.', max_length=254, null=True, verbose_name='E-Mail Address', blank=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='submitter_email',
            field=models.EmailField(help_text='The submitter will receive an email for all public follow-ups left for this task.', max_length=254, null=True, verbose_name='Submitter E-Mail', blank=True),
        ),
        migrations.AlterField(
            model_name='ticketcc',
            name='email',
            field=models.EmailField(help_text='For non-user followers, enter their e-mail address', max_length=254, null=True, verbose_name='E-Mail Address', blank=True),
        ),
    ]
