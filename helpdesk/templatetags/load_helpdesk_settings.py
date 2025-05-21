"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

templatetags/load_helpdesk_settings.py - returns the settings as defined in 
                                    django-helpdesk/helpdesk/settings.py
"""
from __future__ import absolute_import
from django.template import Library
from helpdesk import settings as helpdesk_settings_config
import logging

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def load_helpdesk_settings():
    """
    Custom template filter to expose helpdesk settings in templates.

    Args:
        request: The HTTP request object (not used directly, just for interface compatibility).

    Returns:
        module: The helpdesk settings module with all custom configuration attributes.
        str: An empty string if the import or access fails.
    """
    try:
        return helpdesk_settings_config
    except Exception as e:
        logger.error("'load_helpdesk_settings' template tag (django-helpdesk) crashed with the following error:", exc_info=e)
        return ''
