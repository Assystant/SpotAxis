"""
URLs for the Zinnia archive views.

These routes provide access to blog entries grouped by:
- Index (all entries)
- Year
- Week
- Month
- Day
- Today

Each view supports optional pagination via a `page/<page_number>/` suffix.

View Classes Used:
- EntryIndex:     Archive of all entries
- EntryYear:      Year-based archive
- EntryWeek:      Week-based archive (ISO week number)
- EntryMonth:     Month-based archive
- EntryDay:       Day-based archive
- EntryToday:     Entries from the current day
"""

from django.conf.urls import url

from zinnia.urls import _  # Optional translation for URL patterns
from zinnia.views.archives import (
    EntryIndex, EntryYear, EntryWeek,
    EntryMonth, EntryDay, EntryToday
)

# --------------------------
# Index Archives (all posts)
# --------------------------
index_patterns = [
    url(r'^$',
        EntryIndex.as_view(),
        name='entry_archive_index'),
    url(_(r'^page/(?P<page>\d+)/$'),
        EntryIndex.as_view(),
        name='entry_archive_index_paginated'),
]

# --------------------------
# Year-Based Archives
# Example: /2025/ or /2025/page/2/
# --------------------------
year_patterns = [
    url(r'^(?P<year>\d{4})/$',
        EntryYear.as_view(),
        name='entry_archive_year'),
    url(_(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$'),
        EntryYear.as_view(),
        name='entry_archive_year_paginated'),
]

# --------------------------
# Week-Based Archives
# Example: /2025/week/20/ or /2025/week/20/page/2/
# --------------------------
week_patterns = [
    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/$'),
        EntryWeek.as_view(),
        name='entry_archive_week'),
    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/page/(?P<page>\d+)/$'),
        EntryWeek.as_view(),
        name='entry_archive_week_paginated'),
]

# --------------------------
# Month-Based Archives
# Example: /2025/05/ or /2025/05/page/2/
# --------------------------
month_patterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        EntryMonth.as_view(),
        name='entry_archive_month'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$'),
        EntryMonth.as_view(),
        name='entry_archive_month_paginated'),
]

# --------------------------
# Day-Based Archives
# Example: /2025/05/15/ or /2025/05/15/page/2/
# --------------------------
day_patterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        EntryDay.as_view(),
        name='entry_archive_day'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/page/(?P<page>\d+)/$'),
        EntryDay.as_view(),
        name='entry_archive_day_paginated'),
]

# --------------------------
# Today's Archive
# Example: /today/ or /today/page/2/
# --------------------------
today_patterns = [
    url(_(r'^today/$'),
        EntryToday.as_view(),
        name='entry_archive_today'),
    url(_(r'^today/page/(?P<page>\d+)/$'),
        EntryToday.as_view(),
        name='entry_archive_today_paginated'),
]

# ----------------------------------
# Combine all patterns into a list
# ----------------------------------
archive_patterns = (
    index_patterns +
    year_patterns +
    week_patterns +
    month_patterns +
    day_patterns +
    today_patterns
)

# Main URL patterns exposed by this module
urlpatterns = archive_patterns
