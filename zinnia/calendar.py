"""Calendar module for Zinnia

Provides a custom Calendar class that extends Python’s HTMLCalendar to display
a monthly calendar view with integration of Zinnia blog entries.

Features:
- Highlights days with published entries using a CSS class and link.
- Displays weekday headers and localized first day of week.
- Adds footer with previous/next month navigation.

Classes:
    Calendar: Custom calendar for rendering Zinnia blog entries.
"""

from __future__ import absolute_import

from calendar import HTMLCalendar
from datetime import date

from django.core.urlresolvers import reverse
from django.utils.dates import MONTHS
from django.utils.dates import WEEKDAYS_ABBR
from django.utils.formats import date_format
from django.utils.formats import get_format

from zinnia.models.entry import Entry

AMERICAN_TO_EUROPEAN_WEEK_DAYS = [6, 0, 1, 2, 3, 4, 5]


class Calendar(HTMLCalendar):
    """
    Extension of the HTMLCalendar that integrates Zinnia blog entries.

    Highlights dates with published entries, adding hyperlinks to archive day views.
    """

    def __init__(self):
        """
        Retrieve and convert the localized first weekday at initialization.
        """
        HTMLCalendar.__init__(self, AMERICAN_TO_EUROPEAN_WEEK_DAYS[
            get_format('FIRST_DAY_OF_WEEK')])

    def formatday(self, day, weekday):
        """
        Return a day as a table cell with a link if entries are published this day.

        Args:
            day (int): Day of the month
            weekday (int): Day of the week (0 = Monday, 6 = Sunday)

        Returns:
            str: HTML <td> element
        """
        if day and day in self.day_entries:
            day_date = date(self.current_year, self.current_month, day)
            archive_day_url = reverse('zinnia:entry_archive_day',
                                      args=[day_date.strftime('%Y'),
                                            day_date.strftime('%m'),
                                            day_date.strftime('%d')])
            return '<td class="%s entry"><a href="%s" '\
                   'class="archives">%d</a></td>' % (
                       self.cssclasses[weekday], archive_day_url, day)

        return super(Calendar, self).formatday(day, weekday)

    def formatweekday(self, day):
        """
        Return a weekday name translated as a table header.

        Args:
            day (int): Weekday number

        Returns:
            str: HTML <th> element
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day],
                                           WEEKDAYS_ABBR[day].title())

    def formatweekheader(self):
        """
        Return a header row for the week wrapped in <thead>.

        Returns:
            str: HTML <thead> element
        """
        return '<thead>%s</thead>' % super(Calendar, self).formatweekheader()

    def formatfooter(self, previous_month, next_month):
        """
        Return a footer with navigation links for previous and next months.

        Args:
            previous_month (date): Previous month to link
            next_month (date): Next month to link

        Returns:
            str: HTML <tfoot> row
        """
        footer = '<tfoot><tr>' \
                 '<td colspan="3" class="prev">%s</td>' \
                 '<td class="pad">&nbsp;</td>' \
                 '<td colspan="3" class="next">%s</td>' \
                 '</tr></tfoot>'
        if previous_month:
            previous_content = '<a href="%s" class="previous-month">%s</a>' % (
                reverse('zinnia:entry_archive_month', args=[
                    previous_month.strftime('%Y'),
                    previous_month.strftime('%m')]),
                date_format(previous_month, 'YEAR_MONTH_FORMAT'))
        else:
            previous_content = '&nbsp;'

        if next_month:
            next_content = '<a href="%s" class="next-month">%s</a>' % (
                reverse('zinnia:entry_archive_month', args=[
                    next_month.strftime('%Y'),
                    next_month.strftime('%m')]),
                date_format(next_month, 'YEAR_MONTH_FORMAT'))
        else:
            next_content = '&nbsp;'

        return footer % (previous_content, next_content)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name translated as a table caption.

        Args:
            theyear (int): Year to display
            themonth (int): Month to display
            withyear (bool): Include year in the name

        Returns:
            str: HTML <caption> element
        """
        monthname = '%s %s' % (MONTHS[themonth].title(), theyear)
        return '<caption>%s</caption>' % monthname

    def formatmonth(self, theyear, themonth, withyear=True,
                    previous_month=None, next_month=None):
        """
        Return a full formatted month table with day links and navigation.

        Args:
            theyear (int): Year to render
            themonth (int): Month to render
            withyear (bool): Show year in the month caption
            previous_month (date): Previous month date for nav link
            next_month (date): Next month date for nav link

        Returns:
            str: HTML <table> representing the calendar
        """
        self.current_year = theyear
        self.current_month = themonth
        self.day_entries = [date.day
                            for date in Entry.published.filter(
                                publication_date__year=theyear,
                                publication_date__month=themonth
                                ).datetimes('publication_date', 'day')]
        v = []
        a = v.append
        a('<table class="%s">' % (
            self.day_entries and 'entries-calendar' or 'no-entries-calendar'))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        a(self.formatfooter(previous_month, next_month))
        a('\n<tbody>\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</tbody>\n</table>')
        a('\n')
        return ''.join(v)
