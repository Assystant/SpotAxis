"""
Forms for Zinnia admin

Defines custom Django ModelForms for the Zinnia admin interface:
- `CategoryAdminForm`: Validates parent category relationships.
- `EntryAdminForm`: Handles MPTT category selection with advanced widgets.
"""

from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from zinnia.admin.fields import MPTTModelMultipleChoiceField
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.widgets import MiniTextarea
from zinnia.admin.widgets import TagAutoComplete
from zinnia.models.category import Category
from zinnia.models.entry import Entry


class CategoryAdminForm(forms.ModelForm):
    """
    Custom admin form for the Category model.

    Adds validation for self-parenting and a TreeNode dropdown
    for hierarchical category selection.
    """
    parent = TreeNodeChoiceField(
        label=_('Parent category'),
        empty_label=_('No parent category'),
        level_indicator='|--', required=False,
        queryset=Category.objects.all()
    )

    def __init__(self, *args, **kwargs):
        """
        Add admin site wrapper to the parent field's widget.
        """
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget,
            Category.parent.field.remote_field,
            self.admin_site
        )

    def clean_parent(self):
        """
        Ensure a category is not set as its own parent.
        """
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A category cannot be parent of itself.'),
                code='self_parenting'
            )
        return data

    class Meta:
        """
        Meta configuration for CategoryAdminForm.
        """
        model = Category
        fields = forms.ALL_FIELDS


class EntryAdminForm(forms.ModelForm):
    """
    Custom admin form for the Entry model.

    Enhances category and text field widgets for better admin UX.
    """
    categories = MPTTModelMultipleChoiceField(
        label=_('Categories'), required=False,
        queryset=Category.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('categories'))
    )

    def __init__(self, *args, **kwargs):
        """
        Add admin site wrapper to the categories field.
        """
        super(EntryAdminForm, self).__init__(*args, **kwargs)
        self.fields['categories'].widget = RelatedFieldWidgetWrapper(
            self.fields['categories'].widget,
            Entry.categories.field.remote_field,
            self.admin_site
        )

    class Meta:
        """
        Meta configuration for EntryAdminForm.
        """
        model = Entry
        fields = forms.ALL_FIELDS
        widgets = {
            'tags': TagAutoComplete,
            'lead': MiniTextarea,
            'excerpt': MiniTextarea,
            'image_caption': MiniTextarea,
        }
