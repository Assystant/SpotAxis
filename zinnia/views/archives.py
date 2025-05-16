"""
Views for Zinnia archives.

This module provides class-based views for displaying blog entry archives 
organized by date — including year, month, week, day, and today's archives.
It leverages Django's generic date-based views with additional functionality 
from Zinnia's custom mixins.
"""

import datetime

from django.utils import timezone
from django.views.generic.dates import (
    BaseArchiveIndexView,
    BaseDayArchiveView,
    BaseMonthArchiveView,
    BaseTodayArchiveView,
    BaseWeekArchiveView,
    BaseYearArchiveView
)

from zinnia.models.entry import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.archives import PreviousNextPublishedMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin
from zinnia.views.mixins.templates import (
    EntryQuerysetArchiveTemplateResponseMixin,
    EntryQuerysetArchiveTodayTemplateResponseMixin
)


class EntryArchiveMixin(ArchiveMixin,
                        PreviousNextPublishedMixin,
                        PrefetchCategoriesAuthorsMixin,
                        CallableQuerysetMixin,
                        EntryQuerysetArchiveTemplateResponseMixin):
    """
    Base mixin for all archive views of Entry.

    Combines several mixins to:
    - Centralize archive configuration (ArchiveMixin).
    - Prefetch related authors and categories to reduce DB hits.
    - Provide navigation to previous/next published entries.
    - Force queryset re-evaluation using CallableQuerysetMixin.
    - Render using custom archive templates.
    """
    queryset = Entry.published.all


class EntryIndex(EntryArchiveMixin,
                 EntryQuerysetArchiveTodayTemplateResponseMixin,
                 BaseArchiveIndexView):
    """
    Archive index view.

    Displays a general list of all published entries using today's date
    as the reference.
    """
    context_object_name = 'entry_list'


class EntryYear(EntryArchiveMixin, BaseYearArchiveView):
    """
    Year-based archive view.

    Displays a list of entries grouped by year.
    """
    make_object_list = True
    template_name_suffix = '_archive_year'


class EntryMonth(EntryArchiveMixin, BaseMonthArchiveView):
    """
    Month-based archive view.

    Displays a list of entries grouped by month.
    """
    template_name_suffix = '_archive_month'


class EntryWeek(EntryArchiveMixin, BaseWeekArchiveView):
    """
    Week-based archive view.

    Displays a list of entries grouped by week.
    Adds `week_end_day` to context for displaying week range.
    """
    template_name_suffix = '_archive_week'

    def get_dated_items(self):
        """
        Adds 'week_end_day' to extra context.

        Overrides default behavior to include the last day of the week 
        (starting from `week` + 6 days) in the template context.
        """
        self.date_list, self.object_list, extra_context = super(
            EntryWeek, self).get_dated_items()
        self.date_list = self.get_date_list(self.object_list, 'day')
        extra_context['week_end_day'] = extra_context['week'] + datetime.timedelta(days=6)
        return self.date_list, self.object_list, extra_context


class EntryDay(EntryArchiveMixin, BaseDayArchiveView):
    """
    Day-based archive view.

    Displays all entries published on a specific day.
    """
    template_name_suffix = '_archive_day'


class EntryToday(EntryArchiveMixin, BaseTodayArchiveView):
    """
    Today-based archive view.

    Displays all entries published on the current day.
    Also sets the `year`, `month`, and `day` attributes explicitly 
    for use in template response mixins.
    """
    template_name_suffix = '_archive_today'

    def get_dated_items(self):
        """
        Retrieves dated items for today.

        Sets the instance variables `year`, `month`, and `day` from today's date.
        Returns the list of entries for today.
        """
        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.date()
        self.year, self.month, self.day = today.isoformat().split('-')
        return self._get_dated_items(today)
