"""
Utility functions for the Django Helpdesk project.

Includes user management helpers and URL configuration reload functionality.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
from django.contrib.auth import get_user_model
import importlib

User = get_user_model()


def get_staff_user(username='helpdesk.staff', password='password'):
    """
    Retrieve or create a staff user for the helpdesk.

    If a user with the given username does not exist, creates one with the provided password
    and sets it as staff. If the user exists, updates the password. Returns the user instance.
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password, email='staff@example.com')
        user.is_staff = True
        user.save()
    else:
        user.set_password(password)
        user.save()
    return user


def reload_urlconf(urlconf=None):
    """
    Reload Django URL configuration modules to apply changes immediately.

    If no urlconf is provided, uses the project's ROOT_URLCONF from settings.
    Reloads both the helpdesk-specific and project URL modules, then clears URL caches.

    Uses 'imp.reload' for compatibility with Python 3.
    """

    #from imp import reload  # python 3 needs this import.

    if urlconf is None:
        from django.conf import settings

        urlconf = settings.ROOT_URLCONF

    if HELPDESK_URLCONF in sys.modules:
        importlib.reload(sys.modules[HELPDESK_URLCONF])

    if urlconf in sys.modules:
        importlib.reload(sys.modules[urlconf])

    from django.urls import clear_url_caches
    clear_url_caches()


HELPDESK_URLCONF = 'helpdesk.urls'
