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
    Returns the helpdesk settings for use in templates.
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
