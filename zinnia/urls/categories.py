"""
URLs for the Zinnia category views.

These URL patterns provide access to:
- A list of all published categories
- A detail view for entries under a specific category
- Paginated views for category entry lists

View Classes Used:
- CategoryList:   Displays all categories
- CategoryDetail: Displays entries within a specific category path
"""

from django.conf.urls import url

from zinnia.urls import _  # Allows optional translation of URL regex patterns
from zinnia.views.categories import CategoryList, CategoryDetail

urlpatterns = [
    # -------------------------------------------------
    # Category Index
    # Example: /category/
    # Shows all categories that have published entries
    # -------------------------------------------------
    url(r'^category/$',
        CategoryList.as_view(),
        name='category_list'),

    # ----------------------------------------------------------
    # Category Detail View with Pagination
    # Example: /programming/python/page/2/
    # Displays the entries in the category, paginated
    # 'path' can represent nested slugs like 'programming/python'
    # ----------------------------------------------------------
    url(_(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$'),
        CategoryDetail.as_view(),
        name='category_detail_paginated'),

    # ----------------------------------------------------------
    # Category Detail View (Non-paginated fallback)
    # Example: /programming/python/
    # Displays entries in the specified category
    # ----------------------------------------------------------
    url(r'^(?P<path>[-\/\w]+)/$',
        CategoryDetail.as_view(),
        name='category_detail'),
]
