"""
Views for Zinnia entries search.

This module defines class-based views to allow users
to search published blog entries using a query pattern.
"""

from django.utils.translation import ugettext as _
from django.views.generic.list import ListView

from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


class BaseEntrySearch(object):
    """
    Mixin that implements the logic for entry search functionality.

    This handles:
    - Retrieving and validating the search pattern from the request.
    - Executing the search query.
    - Populating the template context with the search pattern and error (if any).

    Attributes:
        pattern (str): The user-provided search query.
        error (str or None): An error message if search is invalid.
    """
    pattern = ''
    error = None

    def get_queryset(self):
        """
        Build the queryset of published entries based on the search pattern.

        Validates the query parameter:
        - If it's missing or too short, sets an error message.
        - If valid, performs a full-text search on entries.

        Returns:
            QuerySet: Matching published entries or empty queryset.
        """
        entries = Entry.published.none()

        if self.request.GET:
            self.pattern = self.request.GET.get('pattern', '')
            if len(self.pattern) < 3:
                self.error = _('The pattern is too short')
            else:
                entries = Entry.published.search(self.pattern)
        else:
            self.error = _('No pattern to search found')

        return entries

    def get_context_data(self, **kwargs):
        """
        Extend context with search pattern and error message.

        Returns:
            dict: Updated context for the template.
        """
        context = super(BaseEntrySearch, self).get_context_data(**kwargs)
        context.update({
            'pattern': self.pattern,
            'error': self.error
        })
        return context


class EntrySearch(PrefetchCategoriesAuthorsMixin,
                  BaseEntrySearch,
                  ListView):
    """
    Entry search view that displays search results for a pattern.

    Combines:
    - `PrefetchCategoriesAuthorsMixin` to optimize DB access.
    - `BaseEntrySearch` to handle form logic and validation.
    - `ListView` to paginate and render the entries list.

    Attributes:
        paginate_by (int): Number of results per page.
        template_name_suffix (str): Template suffix used to resolve search results.
    """
    paginate_by = PAGINATION
    template_name_suffix = '_search'
