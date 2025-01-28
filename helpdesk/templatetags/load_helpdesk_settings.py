from __future__ import absolute_import
from django.template import Library
from helpdesk import settings as helpdesk_settings_config
import logging

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def load_helpdesk_settings():
    """
    Returns the helpdesk settings for use in templates.
    """
    try:
        return helpdesk_settings_config
    except Exception as e:
        logger.error("'load_helpdesk_settings' template tag (django-helpdesk) crashed with the following error:", exc_info=e)
        return ''
