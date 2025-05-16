"""
Filters for Zinnia admin

Provides custom Django admin list filters for:
- Filtering entries by published authors.
- Filtering entries by categories with published entries.
These filters appear in the sidebar of the admin interface.
"""

from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from zinnia.models.author import Author
from zinnia.models.category import Category


class RelatedPublishedFilter(SimpleListFilter):
    """
    Abstract base class for admin filters that operate on related objects
    which have published entries (e.g., authors, categories).

    Subclasses must define:
        - model: the related model to filter by (e.g., Author)
        - lookup_key: the queryset filter key (e.g., 'authors__id')
    """
    model = None
    lookup_key = None

    def lookups(self, request, model_admin):
        """
        Define the filter options displayed in the sidebar.

        Returns:
            list of tuple: Each tuple is (ID, label) for filter dropdown.
        """
        active_objects = self.model.published.all().annotate(
            count_entries_published=Count('entries')
        ).order_by('-count_entries_published', '-pk')

        for active_object in active_objects:
            yield (
                str(active_object.pk),
                ungettext_lazy(
                    '%(item)s (%(count)i entry)',
                    '%(item)s (%(count)i entries)',
                    active_object.count_entries_published
                ) % {
                    'item': smart_text(active_object),
                    'count': active_object.count_entries_published
                }
            )

    def queryset(self, request, queryset):
        """
        Filter the queryset based on selected filter value.

        Args:
            request: The current request.
            queryset: The base queryset.

        Returns:
            QuerySet: The filtered queryset.
        """
        if self.value():
            return queryset.filter(**{self.lookup_key: self.value()})


class AuthorListFilter(RelatedPublishedFilter):
    """
    Custom admin filter to show only published authors.

    Appears in EntryAdmin's sidebar under "published authors".
    """
    model = Author
    lookup_key = 'authors__id'
    title = _('published authors')
    parameter_name = 'author'


class CategoryListFilter(RelatedPublishedFilter):
    """
    Custom admin filter to show only categories with published entries.

    Appears in EntryAdmin's sidebar under "published categories".
    """
    model = Category
    lookup_key = 'categories__id'
    title = _('published categories')
    parameter_name = 'category'
