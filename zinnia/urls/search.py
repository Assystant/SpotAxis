"""
URLs for the Zinnia search view.

This endpoint allows users to search published blog entries by keyword.

The view handles:
- Validating the search query
- Performing full-text search
- Returning matching published entries

View Used:
- EntrySearch: A paginated search result view for entries.
"""

from django.conf.urls import url
from zinnia.views.search import EntrySearch

urlpatterns = [
    # --------------------------------------------------------------
    # Entry Search View
    # Example: /search/?pattern=django
    # Displays a paginated list of entries matching the search term
    # --------------------------------------------------------------
    url(r'^$', EntrySearch.as_view(),
        name='entry_search'),
]
