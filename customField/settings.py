from __future__ import absolute_import
from django.conf import settings

"""
Settings for Custom Fields 
"""
"""
Settings for Custom Fields

This module defines configuration variables used by the custom field system.
These include allowed field types, widget types, and the user model
responsible for managing templates.
"""



TEMPLATE_MANAGER = getattr(settings, 'CF_TEMPLATE_MANAGER', settings.AUTH_USER_MODEL)
"""
Specifies the user model responsible for managing templates.

This is set via the Django setting `CF_TEMPLATE_MANAGER`. If not specified, 
it defaults to Django's `AUTH_USER_MODEL`.
"""


ALLOWED_FORM_FIELDS = getattr(settings, 'CF_ALLOWED_FORM_FIELDS',
                                (('CharField',), ('ChoiceField',), ('MultipleChoiceField',),))
"""
A tuple of allowed Django form fields for use in custom field definitions.

Each entry is a tuple with the name of a Django form field (e.g., `CharField`, 
`ChoiceField`, `MultipleChoiceField`). This list can be overridden by setting
`CF_ALLOWED_FORM_FIELDS` in Django settings.
"""

ALLOWED_FORM_WIDGETS = getattr(settings, 'CF_ALLOWED_FORM_WIDGETS',
                                (('TextInput',),('Textarea',),('CheckboxInput',),('Select',),('SelectMultiple',),('RadioSelect',),('CheckboxSelectMultiple',),))
"""
A tuple of allowed Django form widgets for rendering custom fields.

Each entry is a tuple with the name of a Django form widget (e.g., 
`TextInput`, `Textarea`, `CheckboxInput`, etc.). This can be overridden 
in Django settings with `CF_ALLOWED_FORM_WIDGETS`.
"""
