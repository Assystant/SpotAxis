"""
URLs for the Zinnia shortlink feature.

This endpoint provides compact, base36-encoded URLs for blog entries.

Usage example:
    - A shortlink like `/e/1Z/` (where `1Z` is base36 of entry ID 71)
      redirects to the full entry URL: `/2025/05/15/my-entry-title/`

View Used:
- EntryShortLink: Decodes the token and redirects to the entry’s canonical URL.
"""

from django.conf.urls import url
from zinnia.views.shortlink import EntryShortLink

urlpatterns = [
    # ---------------------------------------------------------------
    # Shortlink Redirect View
    # Example: /e/1Z/
    # Matches base36-encoded primary key in `token`
    # Redirects to the corresponding entry's full URL
    # ---------------------------------------------------------------
    url(r'^(?P<token>[\dA-Z]+)/$',
        EntryShortLink.as_view(),
        name='entry_shortlink'),
]
