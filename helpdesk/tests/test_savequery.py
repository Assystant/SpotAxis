# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.urls import reverse
from django.test import TestCase
from helpdesk.models import Queue
from helpdesk.tests.helpers import get_staff_user


class TestSavingSharedQuery(TestCase):
    """
    TestCase for verifying the functionality of saving shared queries
    in the Django helpdesk application.
    """
    def setUp(self):
        """
        Set up a sample Queue instance for use in the test case.

        Creates:
        - A Queue object with a title and slug, saved to the test database.
        """
        q = Queue(title='Q1', slug='q1')
        q.save()
        self.q = q

    def test_cansavequery(self):
        """
        Test whether a user can save a shared query.

        Steps:
        - Logs in with a staff user account.
        - Sends a POST request to the 'save query' view with a title,
          associated queue, shared flag, and an encoded query string.
        
        Asserts:
        - The server responds with a 302 redirect status code (successful save).
        - The redirect URL includes a reference to the saved query.
        """
        url = reverse('helpdesk_savequery')
        self.client.login(username=get_staff_user().get_username(),
                          password='password')
        response = self.client.post(
            url,
            data={
                'title': 'ticket on my category',
                'queue': self.q,
                'shared': 'on',
                'query_encoded':
                    'KGRwMApWZmlsdGVyaW5nCnAxCihkcDIKVnN0YXR1c19faW4KcDMKKG'
                    'xwNApJMQphSTIKYUkzCmFzc1Zzb3J0aW5nCnA1ClZjcmVhdGVkCnA2CnMu'
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('tickets/?saved_query=1' in response.url)
