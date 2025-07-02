from __future__ import absolute_import
from django.db import models
from django import forms

from ckeditor.widgets import CKEditorWidget

"""
Module defining custom Django model and form fields for integrating
CKEditor rich text editing capabilities.

Provides:
- RichTextField: A Django model TextField subclass that uses CKEditor
  for rich text input, supporting custom configurations and plugins.
- RichTextFormField: A Django form CharField subclass that uses the
  CKEditorWidget for rendering the rich text editor widget.

Also includes South introspection rules for migrations compatibility.
"""

class RichTextField(models.TextField):
    """
    A Django model field that uses CKEditor for rich text editing.

    Allows configuration of CKEditor through optional parameters:
    - config_name: name of the CKEditor configuration to use.
    - extra_plugins: list of additional CKEditor plugins to enable.
    - external_plugin_resources: list of external plugin resources.

    Extends the standard TextField to use a custom form field with CKEditor.
    """
    def __init__(self, *args, **kwargs):
        """Initialize the RichTextField."""
        self.config_name = kwargs.pop("config_name", "default")
        self.extra_plugins = kwargs.pop("extra_plugins", [])
        self.external_plugin_resources = kwargs.pop("external_plugin_resources", [])
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """Returns the form field for this model field."""
        defaults = {
            'form_class': RichTextFormField,
            'config_name': self.config_name,
            'extra_plugins' : self.extra_plugins,
            'external_plugin_resources': self.external_plugin_resources
        }
        defaults.update(kwargs)
        return super(RichTextField, self).formfield(**defaults)


class RichTextFormField(forms.fields.CharField):
    """
    A Django form field that uses CKEditorWidget for rich text editing.

    Wraps a CharField and replaces its widget with CKEditorWidget,
    configured via constructor parameters.
    """
    def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
        """Initialize the RichTextFormField."""
        kwargs.update({'widget': CKEditorWidget(config_name=config_name, extra_plugins=extra_plugins, external_plugin_resources=external_plugin_resources)})
        super(RichTextFormField, self).__init__(*args, **kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [r"^ckeditor\.fields\.RichTextField"])
except:
    pass
