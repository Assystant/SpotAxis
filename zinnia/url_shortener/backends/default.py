"""Default URL shortener backend for Zinnia"""
from __future__ import absolute_import
import string

from django.contrib.sites.models import Site
from django.urls import reverse
from TRM.settings import HOSTED_URL
from zinnia.settings import PROTOCOL

BASE36_ALPHABET = string.digits + string.ascii_uppercase


def base36(value):
    """
    Encode int to base 36.
    """
    result = ''
    while value:
        value, i = divmod(value, 36)
        result = BASE36_ALPHABET[i] + result
    return result


def backend(entry):
    """
    Default URL shortener backend for Zinnia.
    """
    # return '%s://%s%s' % (
    #     PROTOCOL, Site.objects.get_current().domain,
    #     reverse('zinnia:entry_shortlink', args=[base36(entry.pk)]))
    return '%s%s' % (
        HOSTED_URL,
        reverse('zinnia:entry_shortlink', args=[base36(entry.pk)])
    )
