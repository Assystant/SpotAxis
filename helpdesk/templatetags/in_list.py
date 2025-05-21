"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

templatetags/in_list.py - Very simple template tag to allow us to use the
                          equivilent of 'if x in y' in templates. eg:

Assuming 'food' = 'pizza' and 'best_foods' = ['pizza', 'pie', 'cake]:

{% if food|in_list:best_foods %}
 You've selected one of our favourite foods!
{% else %}
 Your food isn't one of our favourites.
{% endif %}
"""

from __future__ import absolute_import
from django import template


def in_list(value, arg):
    """
    Check if the given value is present in the provided list (arg).

    Args:
        value: The item to check for.
        arg: The list to search within. Defaults to an empty list if None.

    Returns:
        bool: True if value is in arg, else False.
    """
    return value in (arg or [])

register = template.Library()
register.filter(in_list)
