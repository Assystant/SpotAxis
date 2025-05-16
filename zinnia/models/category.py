"""
Category model for Zinnia.

This module defines a hierarchical category system using MPTT (Modified Preorder Tree Traversal),
allowing entries (blog posts) to be organized into nested categories.

Each category can have a parent category, enabling a tree structure like:
  - Programming
    - Python
    - JavaScript
  - Career
    - Interviews
    - Resumes
"""

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

from zinnia.managers import EntryRelatedPublishedManager
from zinnia.managers import entries_published


@python_2_unicode_compatible
class Category(MPTTModel):
    """
    A model representing blog post categories, supporting a nested structure.

    Categories are implemented using MPTT for efficient tree traversal.
    Each category can optionally have a parent category to form a hierarchy.
    """

    title = models.CharField(
        _('title'), max_length=255,
        help_text=_("The display title of the category."))

    slug = models.SlugField(
        _('slug'), unique=True, max_length=255,
        help_text=_("URL-safe slug used to build the category's URL."))

    description = models.TextField(
        _('description'), blank=True,
        help_text=_("Optional description of the category."))

    parent = TreeForeignKey(
        'self',
        related_name='children',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('parent category'),
        help_text=_("Optional parent category for nesting."))

    # Managers
    objects = TreeManager()
    published = EntryRelatedPublishedManager()

    def entries_published(self):
        """
        Returns:
            QuerySet: The list of published blog entries associated with this category.
        """
        return entries_published(self.entries)

    @property
    def tree_path(self):
        """
        Builds the full path to the category by concatenating the slugs
        of all its ancestors, followed by its own slug.

        Returns:
            str: The tree path used for constructing nested URLs.
        """
        if self.parent_id:
            return '/'.join(
                [ancestor.slug for ancestor in self.get_ancestors()] + [self.slug])
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        """
        Constructs the URL to the category detail page using its tree path.

        Returns:
            tuple: A Django named URL pattern with arguments.
        """
        return ('zinnia:category_detail', (self.tree_path,))

    def __str__(self):
        """
        Returns:
            str: The category title for display in admin and templates.
        """
        return self.title

    class Meta:
        """
        Meta options for the Category model.
        """
        ordering = ['title']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    class MPTTMeta:
        """
        Meta options for MPTT tree behavior.

        This controls the ordering of categories in the tree by title.
        """
        order_insertion_by = ['title']
