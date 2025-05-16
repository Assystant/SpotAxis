"""
URLs for the Zinnia HTML sitemap view.

This route serves a **human-readable** sitemap — listing all:
- Published blog entries
- Categories
- Authors

It helps visitors explore the blog’s content structure and supports SEO
via internal linking (distinct from XML sitemaps used by search engines).

View Used:
- Sitemap: A template-based view that displays all content groupings.
"""

from django.conf.urls import url
from zinnia.views.sitemap import Sitemap

urlpatterns = [
    # --------------------------------------------------------------
    # HTML Sitemap View
    # Example: /sitemap/
    # Lists all published entries, categories, and authors
    # --------------------------------------------------------------
    url(r'^$', Sitemap.as_view(),
        name='sitemap'),
]
