"""Filters for Zinnia admin"""
from __future__ import absolute_import
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy 

from zinnia.models.author import Author
from zinnia.models.category import Category


class RelatedPublishedFilter(SimpleListFilter):
    """
    Base filter for related objects to published entries.
    """
    model = None
    lookup_key = None

    def lookups(self, request, model_admin):
        """
        Return published objects with the number of entries.
        """
        active_objects = self.model.published.all().annotate(
            count_entries_published=Count('entries')).order_by(
            '-count_entries_published', '-pk')
        for active_object in active_objects:
            yield (
                str(active_object.pk), ngettext_lazy(
                    '%(item)s (%(count)i entry)',
                    '%(item)s (%(count)i entries)',
                    active_object.count_entries_published) % {
                    'item': smart_str(active_object),
                    'count': active_object.count_entries_published})

    def queryset(self, request, queryset):
        """
        Return the object's entries if a value is set.
        """
        if self.value():
            params = {self.lookup_key: self.value()}
            return queryset.filter(**params)


class AuthorListFilter(RelatedPublishedFilter):
    """
    List filter for EntryAdmin with published authors only.
    """
    model = Author
    lookup_key = 'authors__id'
    title = _('published authors')
    parameter_name = 'author'


class CategoryListFilter(RelatedPublishedFilter):
    """
    List filter for EntryAdmin about categories
    with published entries.
    """
    model = Category
    lookup_key = 'categories__id'
    title = _('published categories')
    parameter_name = 'category'
