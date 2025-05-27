"""
apps.py - App configuration for the django-helpdesk application.

Defines the HelpdeskConfig class used by Django for app-specific settings
and metadata.

Version: 0.2.0
"""

from django.apps import AppConfig


class HelpdeskConfig(AppConfig):
    """
    Django application configuration for the 'helpdesk' app.

    Attributes:
        name (str): Internal Python path for the app ('helpdesk').
        verbose_name (str): Human-readable name shown in the admin.
    """
    name = 'helpdesk'
    verbose_name = "Helpdesk"
