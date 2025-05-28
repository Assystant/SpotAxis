"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/feeds.py - A handful of staff-only RSS feeds to provide ticket details
                 to feed readers or similar software.

These feeds allow users to subscribe and stay up to date with open tickets,
unassigned tickets, recent activity, and queue-based ticket listings.
"""

from __future__ import absolute_import
from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.urlrs import reverse
from django.db.models import Q
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404

from helpdesk.models import Ticket, FollowUp, Queue

User = get_user_model()


class OpenTicketsByUser(Feed):
    """
    Provides an RSS feed of all open and reopened tickets assigned to a specific user.

    If a queue slug is provided, it further filters the tickets within that queue.

    Used for personalized views of pending workload for staff members in specific queues.
    """

    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    def get_object(self, request, user_name, queue_slug=None):
        """Retrieves the user (and optionally a queue) based on provided URL parameters."""
        user = get_object_or_404(User, username=user_name)
        if queue_slug:
            queue = get_object_or_404(Queue, slug=queue_slug)
        else:
            queue = None

        return {'user': user, 'queue': queue}

    def title(self, obj):
        """Generates the feed title with the username and optionally the queue name."""
        if obj['queue']:
            return _("Helpdesk: Open Tickets in queue %(queue)s for %(username)s") % {
                'queue': obj['queue'].title,
                'username': obj['user'].get_username(),
                }
        else:
            return _("Helpdesk: Open Tickets for %(username)s") % {
                'username': obj['user'].get_username(),
                }

    def description(self, obj):
        """Creates a descriptive sentence summarizing the filtered tickets."""
        if obj['queue']:
            return _("Open and Reopened Tickets in queue %(queue)s for %(username)s") % {
                'queue': obj['queue'].title,
                'username': obj['user'].get_username(),
                }
        else:
            return _("Open and Reopened Tickets for %(username)s") % {
                'username': obj['user'].get_username(),
                }

    def link(self, obj):
        """Returns the URL that links to the filtered ticket list in the web interface."""
        if obj['queue']:
            return '%s?assigned_to=%s&queue=%s' % (
                reverse('helpdesk_list'),
                obj['user'].id,
                obj['queue'].id,
                )
        else:
            return '%s?assigned_to=%s' % (
                reverse('helpdesk_list'),
                obj['user'].id,
                )

    def items(self, obj):
        """Returns a queryset of Ticket objects that are either OPEN or REOPENED and assigned to the specified user (optionally filtered by queue)."""
        if obj['queue']:
            return Ticket.objects.filter(
                    assigned_to=obj['user']
                ).filter(
                    queue=obj['queue']
                ).filter(
                    Q(status=Ticket.OPEN_STATUS) | Q(status=Ticket.REOPENED_STATUS)
                )
        else:
            return Ticket.objects.filter(
                    assigned_to=obj['user']
                ).filter(
                    Q(status=Ticket.OPEN_STATUS) | Q(status=Ticket.REOPENED_STATUS)
                )

    def item_pubdate(self, item):
        """Uses the created date of the ticket as the published timestamp in the feed."""
        return item.created

    def item_author_name(self, item):
        """Returns the assigned user’s name, or 'Unassigned' if no user is set."""
        if item.assigned_to:
            return item.assigned_to.get_username()
        else:
            return _('Unassigned')


class UnassignedTickets(Feed):
    """
    Provides an RSS feed of all unassigned tickets that are either open or reopened.

    Useful for staff members or managers to monitor unassigned workload.
    """

    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    title = _('Helpdesk: Unassigned Tickets')
    description = _('Unassigned Open and Reopened tickets')
    link = ''  # '%s?assigned_to=' % reverse('helpdesk_list')

    def items(self, obj):
        """Filters tickets with no assignee and a status of OPEN or REOPENED."""
        return Ticket.objects.filter(
                assigned_to__isnull=True
            ).filter(
                Q(status=Ticket.OPEN_STATUS) | Q(status=Ticket.REOPENED_STATUS)
            )

    def item_pubdate(self, item):
        """Ticket creation date used as publication time."""
        return item.created

    def item_author_name(self, item):
        """Returns 'Unassigned' for all items in this feed."""
        if item.assigned_to:
            return item.assigned_to.get_username()
        else:
            return _('Unassigned')


class RecentFollowUps(Feed):
    """
    Lists the most recent 20 follow-ups on tickets.

    This includes ticket comments, email replies, attachments, and resolutions.
    Helps users stay informed on all ticket-related activity.
    """

    title_template = 'helpdesk/rss/recent_activity_title.html'
    description_template = 'helpdesk/rss/recent_activity_description.html'

    title = _('Helpdesk: Recent Followups')
    description = _('Recent FollowUps, such as e-mail replies, comments, attachments and resolutions')
    link = '/tickets/'  # reverse('helpdesk_list')

    def items(self):
        """Returns the 20 most recent FollowUp objects ordered by descending date."""
        return FollowUp.objects.order_by('-date')[:20]


class OpenTicketsByQueue(Feed):
    """
    Displays open and reopened tickets for a specific queue.

    Used to monitor ticket activity within a department or product team.
    """

    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    def get_object(self, request, queue_slug):
        """Returns the Queue instance based on the given slug."""
        return get_object_or_404(Queue, slug=queue_slug)

    def title(self, obj):
        """Returns the feed title indicating the queue name."""
        return _('Helpdesk: Open Tickets in queue %(queue)s') % {
            'queue': obj.title,
            }

    def description(self, obj):
        """Describes the feed contents (open/reopened tickets) for the queue."""
        return _('Open and Reopened Tickets in queue %(queue)s') % {
            'queue': obj.title,
            }

    def link(self, obj):
        """Generates a direct URL to the ticket list filtered by the queue."""
        return '%s?queue=%s' % (
            reverse('helpdesk_list'),
            obj.id,
            )

    def items(self, obj):
        """Returns open and reopened tickets in the specified queue."""
        return Ticket.objects.filter(
                queue=obj
            ).filter(
                Q(status=Ticket.OPEN_STATUS) | Q(status=Ticket.REOPENED_STATUS)
            )

    def item_pubdate(self, item):
        """Publishes the creation date as the feed timestamp."""
        return item.created

    def item_author_name(self, item):
        """Returns the ticket assignee's username, or 'Unassigned' if no one is assigned."""
        if item.assigned_to:
            return item.assigned_to.get_username()
        else:
            return _('Unassigned')

