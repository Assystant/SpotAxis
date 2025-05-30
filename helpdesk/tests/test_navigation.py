"""
Tests for helpdesk knowledgebase behavior when disabled.

Ensures that navigation and URL reversing handle the knowledgebase being turned off gracefully.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.urls import reverse
from django.test import TestCase

from helpdesk.tests.helpers import get_staff_user, reload_urlconf


class TestKBDisabled(TestCase):
    """
    Test case for helpdesk with knowledgebase feature disabled.

    Temporarily disables the knowledgebase setting for each test and reloads URL configurations.
    """
    def setUp(self):
        """Disable the knowledgebase feature before each test and reload URL configs."""
        from helpdesk import settings

        self.HELPDESK_KB_ENABLED = settings.HELPDESK_KB_ENABLED
        if self.HELPDESK_KB_ENABLED:
            settings.HELPDESK_KB_ENABLED = False
            reload_urlconf()

    def tearDown(self):
        """Restore the original knowledgebase setting and reload URL configs after each test."""
        from helpdesk import settings

        if self.HELPDESK_KB_ENABLED:
            settings.HELPDESK_KB_ENABLED = True
            reload_urlconf()

    def test_navigation(self):

        """Test proper rendering of navigation.html by accessing the dashboard"""

        """
        Test proper rendering of navigation.html by accessing the dashboard
        
        Verify that the dashboard page renders correctly without knowledgebase URLs.

        Confirms that reversing 'helpdesk_kb_index' raises NoReverseMatch,
        and that the dashboard loads with HTTP 200 status.
        """

        from django.urls import NoReverseMatch

        self.client.login(username=get_staff_user().get_username(), password='password')
        self.assertRaises(NoReverseMatch, reverse, 'helpdesk_kb_index')
        try:
            response = self.client.get(reverse('helpdesk_dashboard'))
        except NoReverseMatch as e:
            if 'helpdesk_kb_index' in e.message:
                self.fail("Please verify any unchecked references to helpdesk_kb_index (start with navigation.html)")
            else:
                raise
        else:
            self.assertEqual(response.status_code, 200)
