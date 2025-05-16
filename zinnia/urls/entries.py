"""
URLs for the Zinnia entry detail view.

This route enables date-based access to individual blog entries,
commonly used for permalink-style blog URLs in the format:

    /YYYY/MM/DD/entry-slug/

View Used:
- EntryDetail: Displays the content of a single blog entry, with
  support for preview, protection (e.g., password), and caching.
"""

from django.conf.urls import url

from zinnia.views.entries import EntryDetail

urlpatterns = [
    # -----------------------------------------------------------------------
    # Entry Detail View
    # Example: /2025/05/15/my-awesome-article/
    # Extracts year, month, day, and slug from the URL to identify the entry.
    # Slug must match the entry’s slug field, and the date must match its publication date.
    # -----------------------------------------------------------------------
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        EntryDetail.as_view(),
        name='entry_detail'),
]
