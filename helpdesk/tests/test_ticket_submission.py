"""
This module tests ticket submission workflows in the Django Helpdesk application.
It covers direct ticket creation via ORM and public ticket submission through forms.
Scenarios tested include:
- Public and private queue handling
- Email notifications upon submission
- Handling of custom fields in tickets
"""

from __future__ import absolute_import
from helpdesk.models import Queue, CustomField, Ticket
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.urls import reverse

try:  # python 3
    from urllib.parse import urlparse
except ImportError:  # python 2
    from urllib.parse import urlparse


class TicketBasicsTestCase(TestCase):
    """
    TestCase for basic ticket submission behaviors:
    - Direct ORM-based creation
    - Public form submission
    - Email notification handling
    - Custom field submission
    """
    fixtures = ['emailtemplate.json']

    def setUp(self):
        """
        Set up test queues and default ticket data.
        """
        self.queue_public = Queue.objects.create(
            title='Category 1',
            slug='q1',
            allow_public_submission=True,
            new_ticket_cc='new.public@example.com',
            updated_ticket_cc='update.public@example.com')
        self.queue_private = Queue.objects.create(
            title='Category 2',
            slug='q2',
            allow_public_submission=False,
            new_ticket_cc='new.private@example.com',
            updated_ticket_cc='update.private@example.com')

        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'Some Test Ticket',
        }

        self.client = Client()

    def test_create_ticket_direct(self):
        """
        Test creating a ticket directly using the model.
        Ensure ticket URL format and email count remain unchanged.
        """
        email_count = len(mail.outbox)
        ticket_data = dict(queue=self.queue_public, **self.ticket_data)
        ticket = Ticket.objects.create(**ticket_data)
        self.assertEqual(ticket.ticket_for_url, "q1-%s" % ticket.id)
        self.assertEqual(email_count, len(mail.outbox))

    def test_create_ticket_public(self):
        """
        Test ticket submission via the public helpdesk form.
        Ensure valid redirection and that three emails are sent:
        - Submitter, New Ticket CC, Updated Ticket CC
        """
        email_count = len(mail.outbox)

        response = self.client.get(reverse('helpdesk_home'))
        self.assertEqual(response.status_code, 200)

        post_data = {
                'title': 'Test ticket title',
                'queue': self.queue_public.id,
                'submitter_email': 'ticket1.submitter@example.com',
                'body': 'Test ticket body',
                'priority': 3,
                }

        response = self.client.post(reverse('helpdesk_home'), post_data, follow=True)
        last_redirect = response.redirect_chain[-1]
        last_redirect_url = last_redirect[0]
        # last_redirect_status = last_redirect[1]

        # Ensure we landed on the "View" page.
        # Django 1.9 compatible way of testing this
        # https://docs.djangoproject.com/en/1.9/releases/1.9/#http-redirects-no-longer-forced-to-absolute-uris
        urlparts = urlparse(last_redirect_url)
        self.assertEqual(urlparts.path, reverse('helpdesk_public_view'))

        # Ensure submitter, new-queue + update-queue were all emailed.
        self.assertEqual(email_count+3, len(mail.outbox))

    def test_create_ticket_private(self):
        """
        Test that submitting to a private queue via the public form fails.
        Expect no emails and a validation error in the response.
        """
        email_count = len(mail.outbox)
        post_data = {
            'title': 'Private ticket test',
            'queue': self.queue_private.id,
            'submitter_email': 'ticket2.submitter@example.com',
            'body': 'Test ticket body',
            'priority': 3,
        }

        response = self.client.post(reverse('helpdesk_home'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(email_count, len(mail.outbox))
        self.assertContains(response, 'Select a valid choice.')

    def test_create_ticket_customfields(self):
        """
        Test ticket submission with a custom field.
        Ensure correct email notifications and redirect.
        """
        email_count = len(mail.outbox)
        queue_custom = Queue.objects.create(
            title='Category 3',
            slug='q3',
            allow_public_submission=True,
            updated_ticket_cc='update.custom@example.com')
        custom_field_1 = CustomField.objects.create(
            name='textfield',
            label='Text Field',
            data_type='varchar',
            max_length=100,
            ordering=10,
            required=False,
            staff_only=False)
        post_data = {
            'queue': queue_custom.id,
            'title': 'Ticket with custom text field',
            'submitter_email': 'ticket3.submitter@example.com',
            'body': 'Test ticket body',
            'priority': 3,
            'custom_textfield': 'This is my custom text.',
        }

        response = self.client.post(reverse('helpdesk_home'), post_data, follow=True)

        custom_field_1.delete()
        last_redirect = response.redirect_chain[-1]
        last_redirect_url = last_redirect[0]
        # last_redirect_status = last_redirect[1]
        
        # Ensure we landed on the "View" page.
        # Django 1.9 compatible way of testing this
        # https://docs.djangoproject.com/en/1.9/releases/1.9/#http-redirects-no-longer-forced-to-absolute-uris
        urlparts = urlparse(last_redirect_url)
        self.assertEqual(urlparts.path, reverse('helpdesk_public_view'))

        # Ensure only two e-mails were sent - submitter & updated.
        self.assertEqual(email_count+2, len(mail.outbox))
