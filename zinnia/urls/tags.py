"""
URLs for the Zinnia tag views.

These routes allow users to:
- Browse all tags used in blog entries
- View entries associated with a specific tag
- Paginate results for tag-specific entry listings

View Classes Used:
- TagList:    Lists all tags in use
- TagDetail:  Displays entries for a given tag
"""

from django.conf.urls import url

from zinnia.urls import _  # Optional i18n for translatable URL patterns
from zinnia.views.tags import TagList, TagDetail

urlpatterns = [
    # --------------------------------------------------------------
    # Tag Index View
    # Example: /tags/
    # Lists all tags used on published blog entries
    # --------------------------------------------------------------
    url(r'^$',
        TagList.as_view(),
        name='tag_list'),

    # --------------------------------------------------------------
    # Tag Detail View
    # Example: /tags/django/
    # Shows all published entries associated with the given tag
    # --------------------------------------------------------------
    url(r'^(?P<tag>[^/]+(?u))/$',
        TagDetail.as_view(),
        name='tag_detail'),

    # --------------------------------------------------------------
    # Tag Detail Paginated View
    # Example: /tags/django/page/2/
    # Shows paginated entries for the tag
    # --------------------------------------------------------------
    url(_(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$'),
        TagDetail.as_view(),
        name='tag_detail_paginated'),
]
