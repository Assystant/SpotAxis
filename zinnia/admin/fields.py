"""
Fields for Zinnia admin

Defines custom form fields for handling MPTT (Modified Preorder Tree Traversal)
models in the Django admin, particularly for hierarchical category selection.

Used in:
- Category selection with proper tree indentation
- Sorting based on tree position
"""

from django import forms
from django.utils.encoding import smart_text


class MPTTModelChoiceIterator(forms.models.ModelChoiceIterator):
    """
    Custom iterator for MPTT models used in admin forms.

    Extends ModelChoiceIterator to append additional metadata
    like tree ID and left value to each choice for sorting.
    """

    def choice(self, obj):
        """
        Override the choice method to attach MPTT tree position.

        Args:
            obj (Model): The model instance being rendered as a choice.

        Returns:
            tuple: Standard choice tuple with an appended (tree_id, left) position.
        """
        tree_id = getattr(obj, self.queryset.model._mptt_meta.tree_id_attr, 0)
        left = getattr(obj, self.queryset.model._mptt_meta.left_attr, 0)
        return super(MPTTModelChoiceIterator, self).choice(obj) + ((tree_id, left),)


class MPTTModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Custom ModelMultipleChoiceField for MPTT models.

    Adds visual indentation to labels to reflect tree hierarchy.
    """

    def __init__(self, level_indicator='|--', *args, **kwargs):
        """
        Initialize the field with a custom level indicator.

        Args:
            level_indicator (str): String used to visually indent nested nodes.
        """
        self.level_indicator = level_indicator
        super(MPTTModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """
        Generate a label that includes tree-level indentation.

        Args:
            obj (Model): The model instance.

        Returns:
            str: Indented label representing the node's depth.
        """
        label = smart_text(obj)
        prefix = self.level_indicator * getattr(obj, obj._mptt_meta.level_attr)
        return '%s %s' % (prefix, label) if prefix else label

    def _get_choices(self):
        """
        Override choices to use MPTT-aware iterator.

        Returns:
            MPTTModelChoiceIterator: Custom iterator class.
        """
        return MPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)
