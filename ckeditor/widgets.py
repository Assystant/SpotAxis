# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django import forms
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.core.exceptions import ImproperlyConfigured
# from django.forms.util import flatatt
from django.forms.utils import flatatt

from django.utils.functional import Promise
from django.utils.encoding import force_str
from django.core.serializers.json import DjangoJSONEncoder

class LazyEncoder(DjangoJSONEncoder):
    """
    JSON encoder subclass that serializes Django lazy translation objects.

    This encoder converts instances of django.utils.functional.Promise (used for lazy
    translation strings) into regular strings for JSON serialization.

    Methods:
        default(obj): Override the default JSON encoding method to handle Promise instances.
    """
    def default(self, obj):
        """
        Serialize objects to JSON format, converting lazy translation strings to regular strings.

        Args:
            obj (object): The object to serialize.

        Returns:
            str or super().default: The serialized JSON string or the result of the parent default method.
        """
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


json_encode = LazyEncoder().encode

DEFAULT_CONFIG = {
    'skin': 'bootstrapck',
#     'toolbar_Basic': [
#         ['Source', '-', 'Bold', 'Italic']
#     ],
#     'toolbar_Full': [
#         ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
#         # [ 'Link','Unlink','Anchor'],
#         # ['Image', 'Flash', 'Table', 'HorizontalRule'],
#         ['TextColor', 'BGColor'],
#         # ['Smiley', 'SpecialChar'], ['Source'],
#     ],
    'toolbar': 'Full',
#     # 'height': 'auto',
#     # 'width': 'auto',
#     # 'filebrowserWindowWidth': 940,
#     # 'filebrowserWindowHeight': 725,
#     # 'toolbar' : 'Basic',
#     # 'uiColor' : '#9AB8F3'
}


class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.

    Django form widget providing CKEditor integration for rich text editing.
    """
    class Media:
        """
        Media class to define required JavaScript files for the widget.

        Attributes:
            js (tuple): Tuple of JavaScript file URLs to include.
        """
        js = ()
        jquery_url = getattr(settings, 'CKEDITOR_JQUERY_URL', None)
        if jquery_url:
            js += (jquery_url, )
        try:
            js += (
                settings.STATIC_URL + 'ckeditor/ckeditor/ckeditor.js',
                settings.STATIC_URL + 'ckeditor/ckeditor-init.js',
            )
        except AttributeError:
            raise ImproperlyConfigured("django-ckeditor requires \
                    CKEDITOR_MEDIA_PREFIX setting. This setting specifies a \
                    URL prefix to the ckeditor JS and CSS media (not \
                    uploaded media). Make sure to use a trailing slash: \
                    CKEDITOR_MEDIA_PREFIX = '/media/ckeditor/'")

    def __init__(self, config_name='default', extra_plugins=None, external_plugin_resources=None, *args, **kwargs):
        """Initialize the CKEditor widget."""
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG.copy()

        # Try to get valid config from settings.
        configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
        if configs:
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if config_name in configs:
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                                setting must be a dictionary type.' % \
                                config_name)
                    # Override defaults with settings config.
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' \
                            found in your CKEDITOR_CONFIGS setting." % \
                            config_name)
            else:
                raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                        dictionary type.')

        extra_plugins = extra_plugins or []

        if extra_plugins:
            self.config['extraPlugins'] = ','.join(extra_plugins)

        self.external_plugin_resources = external_plugin_resources or []

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the HTML of the widget including CKEditor initialization.

        Args:
            name (str): Name of the form field.
            value (str or None): Value of the field (HTML content).
            attrs (dict, optional): Additional HTML attributes for the widget.

        Returns:
            SafeString: Marked safe HTML string including textarea and CKEditor setup script.
        """
        if value is None:
            value = ''
        final_attrs = {**self.attrs, **(attrs or {}), 'name': name}
        self.config.setdefault('filebrowserUploadUrl', reverse('ckeditor_upload'))
        self.config.setdefault('filebrowserBrowseUrl', reverse('ckeditor_browse'))
        if not self.config.get('language'):
            self.config['language'] = get_language()

        return mark_safe(render_to_string('ckeditor/widget.html', {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_str(value)),
            'id': final_attrs['id'],
            'config': json_encode(self.config),
            'external_plugin_resources' : self.external_plugin_resources
        }))
