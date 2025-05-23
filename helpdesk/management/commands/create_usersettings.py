#!/usr/bin/python
"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

See LICENSE for details.

create_usersettings.py - Easy way to create helpdesk-specific settings for 
users who don't yet have them.
"""

from __future__ import absolute_import
from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from helpdesk.models import UserSettings
from helpdesk.settings import DEFAULT_USER_SETTINGS

User = get_user_model()


class Command(BaseCommand):
    """
    Django management command to create UserSettings for users missing them.

    This command iterates over all users in the system and creates a
    UserSettings object with default settings for any user that does not
    already have one.
    """

    help = _('Check for user without django-helpdesk UserSettings '
             'and create settings if required. Uses '
             'settings.DEFAULT_USER_SETTINGS which can be overridden to '
             'suit your situation.')

    def handle(self, *args, **options):
        """
        Command entry point or handle command line

        Iterates through all users and creates default UserSettings for users
        who don't have any.

        Args:
            *args: Positional arguments (not used).
            **options: Command options (not used).
        """
        for u in User.objects.all():
            UserSettings.objects.get_or_create(user=u,
                                               defaults={'settings': DEFAULT_USER_SETTINGS})
