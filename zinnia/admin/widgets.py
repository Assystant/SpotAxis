"""
Widgets for Zinnia admin

Defines custom Django admin widgets for:
- MPTT-enabled multi-select interfaces
- Tag auto-completion using Select2
- Compact textareas for minimal UI
"""

import json

from django.contrib.admin import widgets
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms import Media
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from tagging.models import Tag
from zinnia.models import Entry


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    """
    MPTT-compatible version of FilteredSelectMultiple.

    Adds support for rendering tree structure metadata (tree ID, left value)
    to assist in frontend sorting and hierarchical UI.
    """

    def __init__(self, verbose_name, is_stacked=False, attrs=None, choices=()):
        """
        Initializes the widget with optional stacking and choices.

        Args:
            verbose_name (str): Display label.
            is_stacked (bool): Whether to stack the selection box vertically.
            attrs (dict): HTML attributes.
            choices (iterable): Optional initial choices.
        """
        super(MPTTFilteredSelectMultiple, self).__init__(
            verbose_name, is_stacked, attrs, choices)

    def render_option(self, selected_choices, option_value, option_label, sort_fields):
        """
        Render a single option with MPTT tree metadata attributes.

        Args:
            selected_choices (set): Set of selected values.
            option_value (str): Value for the <option>.
            option_label (str): Display label for the <option>.
            sort_fields (tuple): Tree sorting info (tree_id, left).

        Returns:
            str: Rendered <option> element.
        """
        option_value = force_text(option_value)
        option_label = escape(force_text(option_label))

        selected_html = mark_safe(' selected="selected"') if option_value in selected_choices else ''
        return format_html(
            six.text_type('<option value="{1}"{2} data-tree-id="{3}" data-left-value="{4}">{0}</option>'),
            option_label, option_value, selected_html,
            sort_fields[0], sort_fields[1]
        )

    def render_options(self, choices=None, selected_choices=None):
        """
        Render all <option> elements with tree structure metadata.

        Returns:
            str: Combined HTML for all rendered options.
        """
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label, sort_fields in self.choices:
            output.append(self.render_option(
                selected_choices, option_value, option_label, sort_fields))
        return '\n'.join(output)

    @property
    def media(self):
        """
        Include JS files needed for MPTT multi-select behavior.
        """
        js = ['admin/js/core.js',
              'zinnia/admin/mptt/js/mptt_m2m_selectbox.js',
              'admin/js/SelectFilter2.js']
        return Media(js=[staticfiles_storage.url(path) for path in js])


class TagAutoComplete(widgets.AdminTextInputWidget):
    """
    Text input widget for tags with Select2-based autocompletion.
    """

    def get_tags(self):
        """
        Collect existing tags from Entry model.

        Returns:
            list of str: Tag names for autocomplete suggestions.
        """
        return [tag.name for tag in Tag.objects.usage_for_model(Entry)]

    def render(self, name, value, attrs=None):
        """
        Render the widget and inject Select2 JS initialization script.

        Returns:
            str: HTML + JS for rendering the autocomplete input.
        """
        output = [super(TagAutoComplete, self).render(name, value, attrs)]
        output.append('<script type="text/javascript">')
        output.append('(function($) {')
        output.append('  $(document).ready(function() {')
        output.append('    $("#id_%s").select2({' % name)
        output.append('       width: "element",')
        output.append('       maximumInputLength: 50,')
        output.append('       tokenSeparators: [",", " "],')
        output.append('       tags: %s' % json.dumps(self.get_tags()))
        output.append('     });')
        output.append('    });')
        output.append('}(django.jQuery));')
        output.append('</script>')
        return mark_safe('\n'.join(output))

    @property
    def media(self):
        """
        Include Select2 CSS and JS for autocompletion support.
        """
        def static(path):
            return staticfiles_storage.url('zinnia/admin/select2/%s' % path)

        return Media(
            css={'all': (static('css/select2.css'),)},
            js=(static('js/select2.js'),)
        )


class MiniTextarea(widgets.AdminTextareaWidget):
    """
    Smaller textarea widget for compact form layouts in admin.

    Default height is 2 rows.
    """
    rows = 2

    def __init__(self, attrs=None):
        """
        Initialize with fewer rows for vertical space saving.
        """
        super(MiniTextarea, self).__init__({'rows': self.rows})
