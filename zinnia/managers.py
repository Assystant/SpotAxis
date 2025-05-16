"""
Managers of Zinnia

This module contains custom model managers and utility functions
used for retrieving and manipulating published entries and associated
objects within the Zinnia blogging application.

It defines:
- Constants for entry publication status
- Utility functions for filtering published tags and entries
- Custom managers for Entry and Entry-related models that include only
  published and site-aware data
"""

from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone

from zinnia.settings import SEARCH_FIELDS

# Constants representing the status of an entry
DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """
    Return the tags that are associated with published entries only.

    This function uses the `django-tagging` library to retrieve
    tag usage statistics and then filters tags that are linked
    to published entries.

    Returns:
        QuerySet of `Tag` objects used in published entries.
    """
    from tagging.models import Tag
    from zinnia.models.entry import Entry
    tags_entry_published = Tag.objects.usage_for_queryset(
        Entry.published.all())
    # Workaround for issue #44 in django-tagging
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


def entries_published(queryset):
    """
    Filter a queryset to return only published entries.

    An entry is considered published if:
    - Its status is PUBLISHED
    - The current time is within the publication window (start to end)
    - The entry is associated with the current Site

    Args:
        queryset (QuerySet): The initial queryset to filter.

    Returns:
        QuerySet: A filtered queryset of published entries.
    """
    now = timezone.now()
    return queryset.filter(
        models.Q(start_publication__lte=now) |
        models.Q(start_publication=None),
        models.Q(end_publication__gt=now) |
        models.Q(end_publication=None),
        status=PUBLISHED,
        sites=Site.objects.get_current()
    )


class EntryPublishedManager(models.Manager):
    """
    Custom manager for retrieving published blog entries only.

    Provides methods for:
    - Getting all published entries
    - Getting entries published on the current site
    - Searching through published entries
    """

    def get_queryset(self):
        """
        Override default queryset to return only published entries.

        Returns:
            QuerySet: Published entries.
        """
        return entries_published(
            super(EntryPublishedManager, self).get_queryset()
        )

    def on_site(self):
        """
        Return published entries for the current Site only.

        Returns:
            QuerySet: Entries associated with the current Site.
        """
        return super(EntryPublishedManager, self).get_queryset().filter(
            sites=Site.objects.get_current()
        )

    def search(self, pattern):
        """
        Search published entries using a search pattern.

        Tries to use the advanced search engine, and falls back to
        basic search if unavailable.

        Args:
            pattern (str): Search input.

        Returns:
            QuerySet: Search results.
        """
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """
        Perform advanced search using external search backend.

        Args:
            pattern (str): Search input.

        Returns:
            QuerySet: Matching entries using advanced logic.
        """
        from zinnia.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """
        Fallback search method using simple text matching.

        Searches each word in the pattern across all SEARCH_FIELDS.

        Args:
            pattern (str): Search input.

        Returns:
            QuerySet: Matching entries.
        """
        lookup = None
        for word in pattern.split():
            query_part = models.Q()
            for field in SEARCH_FIELDS:
                query_part |= models.Q(**{f'{field}__icontains': word})
            lookup = query_part if lookup is None else lookup | query_part
        return self.get_queryset().filter(lookup)


class EntryRelatedPublishedManager(models.Manager):
    """
    Custom manager for retrieving objects related to published entries.

    Useful for tags, categories, or other relations that link to `Entry`
    models through a ForeignKey or ManyToMany relationship.
    """

    def get_queryset(self):
        """
        Override default queryset to include only objects related
        to published entries.

        Returns:
            QuerySet: Related objects associated with published entries.
        """
        now = timezone.now()
        return super(EntryRelatedPublishedManager, self).get_queryset().filter(
            models.Q(entries__start_publication__lte=now) |
            models.Q(entries__start_publication=None),
            models.Q(entries__end_publication__gt=now) |
            models.Q(entries__end_publication=None),
            entries__status=PUBLISHED,
            entries__sites=Site.objects.get_current()
        ).distinct()
