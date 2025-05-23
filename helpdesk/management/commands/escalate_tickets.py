#!/usr/bin/python
"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

scripts/escalate_tickets.py - Easy way to escalate tickets based on their age,
                              designed to be run from Cron or similar.
"""


from __future__ import absolute_import
from __future__ import print_function
from datetime import timedelta, date
import getopt
from optparse import make_option
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.translation import ugettext as _

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from helpdesk.models import Queue, Ticket, FollowUp, EscalationExclusion, TicketChange
from helpdesk.lib import send_templated_mail, safe_template_context


class Command(BaseCommand):
    """
    Django management command to escalate tickets in specified queues.

    Options:
        --queues: Comma-separated list of queue slugs to include (default is all).
        --verboseescalation: Enables verbose output during escalation process.

    The command filters tickets based on status, on_hold, priority, and last escalation date,
    and escalates them by lowering their priority number and notifying relevant parties.
    """
    def __init__(self):
        BaseCommand.__init__(self)

        self.option_list += (
            make_option(
                '--queues',
                help='Queues to include (default: all). Use queue slugs'),
            make_option(
                '--verboseescalation',
                action='store_true',
                default=False,
                help='Display a list of dates excluded'),
            )

    def handle(self, *args, **options):
        """
        Entry point for the management command.

        Parses options, validates queues, and calls the escalate_tickets function.
        """
        verbose = False
        queue_slugs = None
        queues = []

        if options['verboseescalation']:
            verbose = True
        if options['queues']:
            queue_slugs = options['queues']

        if queue_slugs is not None:
            queue_set = queue_slugs.split(',')
            for queue in queue_set:
                try:
                    Queue.objects.get(slug__exact=queue)
                except Queue.DoesNotExist:
                    raise CommandError("Queue %s does not exist." % queue)
                queues.append(queue)

        escalate_tickets(queues=queues, verbose=verbose)


def escalate_tickets(queues, verbose):
    """
    Escalate tickets for the given queues based on queue escalation settings.

    Args:
        queues (list of str): List of queue slugs to process. If empty, all queues
                              with escalation configured are processed.
        verbose (bool): If True, prints detailed processing information.

    The function:
      - Computes the number of working days since the last escalation,
        accounting for EscalationExclusion days.
      - Finds tickets that are open or reopened, not on hold, and whose last escalation
        or creation date is older than the required escalation date.
      - Lowers their priority by 1 (higher priority).
      - Sends notification emails to the submitter, queue CC, and assigned user.
      - Adds a public FollowUp note and a TicketChange record for the priority update.
    """
    queryset = Queue.objects.filter(escalate_days__isnull=False).exclude(escalate_days=0)
    if queues:
        queryset = queryset.filter(slug__in=queues)

    for q in queryset:
        last = date.today() - timedelta(days=q.escalate_days)
        today = date.today()
        workdate = last

        days = 0

        while workdate < today:
            if EscalationExclusion.objects.filter(date=workdate).count() == 0:
                days += 1
            workdate = workdate + timedelta(days=1)

        req_last_escl_date = date.today() - timedelta(days=days)

        if verbose:
            print(("Processing: %s" % q))

        for t in q.ticket_set.filter(
                      Q(status=Ticket.OPEN_STATUS)
                      | Q(status=Ticket.REOPENED_STATUS)
                ).exclude(
                    priority=1
                ).filter(
                      Q(on_hold__isnull=True)
                      | Q(on_hold=False)
                ).filter(
                      Q(last_escalation__lte=req_last_escl_date)
                      | Q(last_escalation__isnull=True, created__lte=req_last_escl_date)
                ):

            t.last_escalation = timezone.now()
            t.priority -= 1
            t.save()

            context = safe_template_context(t)

            if t.submitter_email:
                send_templated_mail(
                    'escalated_submitter',
                    context,
                    recipients=t.submitter_email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )

            if t.queue.updated_ticket_cc:
                send_templated_mail(
                    'escalated_cc',
                    context,
                    recipients=t.queue.updated_ticket_cc,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )

            if t.assigned_to:
                send_templated_mail(
                    'escalated_owner',
                    context,
                    recipients=t.assigned_to.email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )

            if verbose:
                print(("  - Esclating %s from %s>%s" % (
                    t.ticket,
                    t.priority+1,
                    t.priority
                    )
                ))

            f = FollowUp(
                ticket=t,
                title='Ticket Escalated',
                date=timezone.now(),
                public=True,
                comment=_('Ticket escalated after %s days' % q.escalate_days),
            )
            f.save()

            tc = TicketChange(
                followup=f,
                field=_('Priority'),
                old_value=t.priority + 1,
                new_value=t.priority,
            )
            tc.save()


def usage():
    print("Options:")
    print(" --queues: Queues to include (default: all). Use queue slugs")
    print(" --verboseescalation: Display a list of dates excluded")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], ['queues=', 'verboseescalation'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    verbose = False
    queue_slugs = None
    queues = []

    for o, a in opts:
        if o == '--verboseescalation':
            verbose = True
        if o == '--queues':
            queue_slugs = a

    if queue_slugs is not None:
        queue_set = queue_slugs.split(',')
        for queue in queue_set:
            try:
                q = Queue.objects.get(slug__exact=queue)
            except Queue.DoesNotExist:
                print(("Queue %s does not exist." % queue))
                sys.exit(2)
            queues.append(queue)

    escalate_tickets(queues=queues, verbose=verbose)
