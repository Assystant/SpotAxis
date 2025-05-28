from __future__ import absolute_import
from helpdesk.models import Queue, Ticket
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse


class PublicActionsTestCase(TestCase):
    """
    TestCase class to validate public ticket actions in the helpdesk system.

    This test suite ensures that users can:
    - View their ticket via a public interface using email and ticket ID
    - Close a ticket that is already marked as resolved
    """
    def setUp(self):
        """
        Create a queue & ticket we can use for later tests.
        """
        self.queue = Queue.objects.create(title='Category 1',
                                          slug='q',
                                          allow_public_submission=True,
                                          new_ticket_cc='new.public@example.com',
                                          updated_ticket_cc='update.public@example.com')
        self.ticket = Ticket.objects.create(title='Test Ticket',
                                            queue=self.queue,
                                            submitter_email='test.submitter@example.com',
                                            description='This is a test ticket.')

        self.client = Client()

    def test_public_view_ticket(self):
        """
        Test whether a user can view a ticket using the public interface.

        Simulates a GET request with correct ticket ID and submitter email.
        Asserts that:
        - Response status code is 200 (OK)
        - The 'public_view_form.html' template is not rendered (implying successful ticket load)
        """
        response = self.client.get('%s?ticket=%s&email=%s' % (
            reverse('helpdesk_public_view'),
            self.ticket.ticket_for_url,
            'test.submitter@example.com'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'helpdesk/public_view_form.html')

    def test_public_close(self):
        """
        Test that a user can close a resolved ticket through the public interface.

        Steps:
        - Sets the ticket status to RESOLVED and adds a resolution note.
        - Makes a GET request with the 'close' parameter.
        - Asserts:
            - Response redirects (302)
            - Status changes to CLOSED
            - Resolution message is preserved
            - A new follow-up is added

        Restores:
        - Original status and resolution to avoid side effects on other tests.
        """
        old_status = self.ticket.status
        old_resolution = self.ticket.resolution
        resolution_text = 'Resolved by test script'

        ticket = Ticket.objects.get(id=self.ticket.id)
        
        ticket.status = Ticket.RESOLVED_STATUS
        ticket.resolution = resolution_text
        ticket.save()

        current_followups = ticket.followup_set.all().count()
        
        response = self.client.get('%s?ticket=%s&email=%s&close' % (
            reverse('helpdesk_public_view'),
            ticket.ticket_for_url,
            'test.submitter@example.com'))
        
        ticket = Ticket.objects.get(id=self.ticket.id)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'helpdesk/public_view_form.html')
        self.assertEqual(ticket.status, Ticket.CLOSED_STATUS)
        self.assertEqual(ticket.resolution, resolution_text)
        self.assertEqual(current_followups+1, ticket.followup_set.all().count())
        
        ticket.resolution = old_resolution
        ticket.status = old_status
        ticket.save()
