"""
URLs for Zinnia's syndication feeds.

These endpoints serve various RSS or Atom feeds related to:
- Latest blog entries
- Discussions (comments, pingbacks, trackbacks)
- Author, category, tag-based entries
- Search results
- Entry-specific interactions

Each feed corresponds to a different class-based feed defined in `zinnia.feeds`.

Feeds can be consumed by RSS readers, aggregators, or external tools.

Feed Classes Used:
- LastEntries
- LastDiscussions
- SearchEntries
- TagEntries
- AuthorEntries
- CategoryEntries
- EntryDiscussions
- EntryComments
- EntryPingbacks
- EntryTrackbacks
"""

from django.conf.urls import url

from zinnia.feeds import (
    AuthorEntries,
    CategoryEntries,
    EntryComments,
    EntryDiscussions,
    EntryPingbacks,
    EntryTrackbacks,
    LastDiscussions,
    LastEntries,
    SearchEntries,
    TagEntries
)
from zinnia.urls import _  # Optional translation for URL patterns

urlpatterns = [
    # -----------------------------------------------
    # Global feed of latest published entries
    # Example: /feeds/
    # -----------------------------------------------
    url(r'^$',
        LastEntries(),
        name='entry_feed'),

    # -----------------------------------------------
    # Global feed of latest discussions (comments, etc.)
    # Example: /feeds/discussions/
    # -----------------------------------------------
    url(_(r'^discussions/$'),
        LastDiscussions(),
        name='discussion_feed'),

    # -----------------------------------------------
    # Feed for entry search results
    # Example: /feeds/search/?pattern=django
    # -----------------------------------------------
    url(_(r'^search/$'),
        SearchEntries(),
        name='entry_search_feed'),

    # -----------------------------------------------
    # Tag-based feed
    # Example: /feeds/tags/django/
    # -----------------------------------------------
    url(_(r'^tags/(?P<tag>[^/]+(?u))/$'),
        TagEntries(),
        name='tag_feed'),

    # -----------------------------------------------
    # Author-based feed
    # Example: /feeds/authors/johndoe/
    # -----------------------------------------------
    url(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='author_feed'),

    # -----------------------------------------------
    # Category-based feed
    # Example: /feeds/categories/python/web/
    # -----------------------------------------------
    url(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='category_feed'),

    # -----------------------------------------------
    # Entry-specific discussions feed (comments + pingbacks + trackbacks)
    # Example: /feeds/discussions/2025/05/15/my-entry/
    # -----------------------------------------------
    url(_(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryDiscussions(),
        name='entry_discussion_feed'),

    # -----------------------------------------------
    # Entry-specific comment feed
    # Example: /feeds/comments/2025/05/15/my-entry/
    # -----------------------------------------------
    url(_(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryComments(),
        name='entry_comment_feed'),

    # -----------------------------------------------
    # Entry-specific pingback feed
    # Example: /feeds/pingbacks/2025/05/15/my-entry/
    # -----------------------------------------------
    url(_(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryPingbacks(),
        name='entry_pingback_feed'),

    # -----------------------------------------------
    # Entry-specific trackback feed
    # Example: /feeds/trackbacks/2025/05/15/my-entry/
    # -----------------------------------------------
    url(_(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryTrackbacks(),
        name='entry_trackback_feed'),
]
