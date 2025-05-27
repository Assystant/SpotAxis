# -*- coding: utf-8 -*-
"""
test_ticket_lookup.py

This module tests public ticket lookup functionality in the Django Helpdesk app.
It focuses on how users (typically ticket submitters) can access their tickets via:

- Direct database ID lookup
- Public view URL (usually emailed to submitters)
- Old links remaining functional even if the ticket's queue changes

These tests ensure robust public access behavior independent of the knowledge base setting.
"""
from __future__ import absolute_import
from django.urls import reverse
from django.test import TestCase
from helpdesk.models import Ticket, Queue


class TestKBDisabled(TestCase):
    """
    Test case for ticket lookup behaviors when knowledge base (KB) is disabled or unused.

    Validates public access via ID and URL, and link integrity when ticket queues change.
    """
    def setUp(self):
        """
        Set up a ticket and a queue for testing.
        Creates one ticket in a queue that simulates a typical helpdesk submission.
        """
        q = Queue(title='Q1', slug='q1')
        q.save()
        t = Ticket(title='Test Ticket', submitter_email='test@domain.com')
        t.queue = q
        t.save()
        self.ticket = t

    def test_ticket_by_id(self):
        """
        Test if the ticket can be retrieved using its ID directly from the database.
        """
        # get the ticket from models
        t = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(t.title, self.ticket.title)

    def test_ticket_by_link(self):
        """
        Test if the ticket can be accessed via the public view link.
        Simulates a user following a link received in an email.
        """
        # Instead of using the ticket_for_url link,
        # we will exercise 'reverse' to lookup/build the URL
        # from the ticket info we have
        # http://example.com/helpdesk/view/?ticket=q1-1&email=None
        response = self.client.get(reverse('helpdesk_public_view'),
                                   {'ticket': self.ticket.ticket_for_url,
                                    'email': self.ticket.submitter_email})
        self.assertEqual(response.status_code, 200)

    def test_ticket_with_changed_queue(self):
        """
        Test if the ticket remains accessible via the original public link
        even after its queue is changed. This checks for backward compatibility
        of emailed links when internal routing changes.
        """
        # Make a ticket (already done in setup() )
        # Now make another queue
        q2 = Queue(title='Q2', slug='q2')
        q2.save()
        # grab the URL / params which would have been emailed out to submitter.
        url = reverse('helpdesk_public_view')
        params = {'ticket': self.ticket.ticket_for_url,
                  'email': self.ticket.submitter_email}
        # Pickup the ticket created in setup() and change its queue
        self.ticket.queue = q2
        self.ticket.save()

        # confirm that we can still get to a url which was emailed earlier
        response = self.client.get(url, params)
        self.assertNotContains(response, "Invalid ticket ID")
