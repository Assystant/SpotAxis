"""
Views for Zinnia authors.

This module provides class-based views for displaying lists of authors
and detailed views showing entries published by specific authors.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic.list import BaseListView, ListView

from zinnia.models.author import Author
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin


class AuthorList(ListView):
    """
    View returning a list of all published authors.

    Displays all authors who have published entries, annotated with the 
    number of entries they’ve published.
    """

    def get_queryset(self):
        """
        Returns a queryset of published authors with their entry count.

        Uses `.annotate()` to add a `count_entries_published` field 
        representing how many entries each author has published.
        """
        return Author.published.all().annotate(
            count_entries_published=Count('entries'))


class BaseAuthorDetail(object):
    """
    Mixin providing logic for the author detail view.

    This mixin:
    - Fetches the author object using the `username` from the URL.
    - Returns a queryset of all published entries by that author.
    - Adds the author to the view's context.
    """

    def get_queryset(self):
        """
        Fetch the author by their username and return their published entries.
        """
        self.author = get_object_or_404(
            Author, **{Author.USERNAME_FIELD: self.kwargs['username']}
        )
        return self.author.entries_published()

    def get_context_data(self, **kwargs):
        """
        Add the current `author` object to the context for template access.
        """
        context = super(BaseAuthorDetail, self).get_context_data(**kwargs)
        context['author'] = self.author
        return context


class AuthorDetail(EntryQuerysetTemplateResponseMixin,
                   PrefetchCategoriesAuthorsMixin,
                   BaseAuthorDetail,
                   BaseListView):
    """
    Detailed author view combining multiple mixins:

    - EntryQuerysetTemplateResponseMixin:
        Provides custom template support based on entry list context.
    - PrefetchCategoriesAuthorsMixin:
        Optimizes DB queries by prefetching related authors and categories.
    - BaseAuthorDetail:
        Provides core logic to get the author and their entries.
    - BaseListView:
        Implements list-like behavior to display a list of entries.

    This view shows all blog entries published by a specific author.
    """
    model_type = 'author'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        Return a display-friendly name for the current author.

        Defaults to the author's full name. Could be changed to `get_username()`
        for stricter uniqueness or legacy usage.
        """
        return self.author.get_full_name()
