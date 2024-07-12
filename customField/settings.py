"""
Settings for Custom Fields 
"""
from django.conf import settings

TEMPLATE_MANAGER = getattr(settings, 'CF_TEMPLATE_MANAGER', settings.AUTH_USER_MODEL)

ALLOWED_FORM_FIELDS = getattr(settings, 'CF_ALLOWED_FORM_FIELDS',
                                (('CharField',), ('ChoiceField',), ('MultipleChoiceField',),))
ALLOWED_FORM_WIDGETS = getattr(settings, 'CF_ALLOWED_FORM_WIDGETS',
                                (('TextInput',),('Textarea',),('CheckboxInput',),('Select',),('SelectMultiple',),('RadioSelect',),('CheckboxSelectMultiple',),))