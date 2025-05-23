"""
Django template tags module for django-helpdesk application.

This module provides custom template tags to access the helpdesk settings
within Django templates. It registers a simple tag `load_helpdesk_settings`
that exposes the helpdesk configuration, allowing template authors to
dynamically utilize settings defined in the helpdesk app.

Logging is configured for error tracking to assist debugging if the settings
cannot be loaded properly.

Imports:
    - absolute_import: Ensures absolute imports for compatibility.
    - django.template: Used to create and register custom template tags.
    - helpdesk.settings: The settings module of the django-helpdesk app.
    - logging: For capturing and logging errors.
"""

from __future__ import absolute_import
from django import template
from helpdesk import settings as helpdesk_settings_config
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Register the template library
register = template.Library()

@register.simple_tag
def load_helpdesk_settings():
    """
    Template tag to load and return the helpdesk settings configuration.

    Returns:
        helpdesk_settings_config: The settings module object from django-helpdesk.

    If an error occurs during retrieval, logs the error with traceback and returns
    an empty dictionary as a safe fallback to prevent template rendering failure.
    """
    try:
        # Return the settings object for use in templates
        return helpdesk_settings_config
    except Exception as e:
        # Log the error with full traceback for debugging
        logger.error(
            "'load_helpdesk_settings' template tag (django-helpdesk) encountered an error.",
            exc_info=True
        )
        # Return an empty dictionary or default fallback value
        return {}
