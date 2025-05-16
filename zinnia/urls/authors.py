"""
URLs for the Zinnia authors views.

These URL patterns provide access to:
- A list of all authors who have published blog entries
- A detail view of a specific author's published entries
- Paginated versions of the author's entries

View Classes Used:
- AuthorList: Lists all authors
- AuthorDetail: Shows entries by a specific author
"""

from django.conf.urls import url

from zinnia.urls import _  # Optional translation-aware wrapper for regexes
from zinnia.views.authors import AuthorList, AuthorDetail

urlpatterns = [
    # -------------------------------
    # Author Index
    # Example: /authors/
    # -------------------------------
    url(r'^$',
        AuthorList.as_view(),
        name='author_list'),

    # --------------------------------------------------------
    # Author Detail View with Pagination
    # Example: /authors/johndoe/page/2/
    # Allows browsing multiple pages of an author's entries
    # --------------------------------------------------------
    url(_(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$'),
        AuthorDetail.as_view(),
        name='author_detail_paginated'),

    # -----------------------------------------
    # Author Detail View (Non-paginated fallback)
    # Example: /authors/johndoe/
    # Shows entries from a specific author
    # -----------------------------------------
    url(r'^(?P<username>[.+-@\w]+)/$',
        AuthorDetail.as_view(),
        name='author_detail'),
]
