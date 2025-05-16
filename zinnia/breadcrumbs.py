"""
Breadcrumb module for Zinnia

This module builds contextual breadcrumbs for various views in the Zinnia blogging engine.
Breadcrumbs are used in templates to help users understand the structure and location of the current page.

Key Concepts:
-------------
- Each breadcrumb is represented by a `Crumb` object, which has a `name` and an optional `url`.
- This module provides breadcrumbs for:
    - Archive views by date (year, month, day, week)
    - Entry detail pages
    - Author, Category, Tag listing and detail pages
    - Paginated views (e.g., Page 2 of Author list)

Breadcrumb Building Functions:
------------------------------
- `year_crumb(date)`, `month_crumb(date)`, `day_crumb(date)`:
    Generate date-based crumbs for archive navigation.

- `entry_breadcrumbs(entry)`:
    Returns a list of breadcrumbs for a blog entry including its year, month, day, and title.

- `MODEL_BREADCRUMBS`:
    A dispatch table mapping model names (e.g., 'Author', 'Category') to breadcrumb generator functions.

- `retrieve_breadcrumbs(path, model_instance, root_name)`:
    Main function to build breadcrumbs for any Zinnia-managed URL.
    Handles:
      - Model detail views
      - Archive views with or without dates
      - Week-based archive URLs
      - Paginated pages (via `handle_page_crumb` decorator)

Regular Expressions:
---------------------
- `ARCHIVE_REGEXP`: Matches URLs containing year/month/day components.
- `ARCHIVE_WEEK_REGEXP`: Matches URLs containing year/week.
- `PAGE_REGEXP`: Matches pagination URLs (e.g., `/page/2/`).

Decorator:
----------
- `handle_page_crumb(func)`:
    Wraps the main breadcrumb function to detect and append page-specific breadcrumbs
    like "Page 2" if applicable.

Example Usage:
--------------
Called internally in Zinnia views or templates to generate breadcrumbs like:
```
[Home] > [Categories] > [Web Development] > [Django] > [Page 2]
[Home] > [2023] > [May] > [10] > [My Blog Post Title]
```

All breadcrumbs are returned as a list of `Crumb` objects.
These can be iterated in a template to render a navigation trail.
"""


import re
from datetime import datetime
from functools import wraps

from django.core.urlresolvers import reverse
from django.utils.dateformat import format
from django.utils.timezone import is_aware
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _


class Crumb(object):
    """
    Part of the breadcrumbs.
    """
    def __init__(self, name, url=None):
        self.name = name
        self.url = url


def year_crumb(date):
    """
    Crumb for a year.
    """
    year = date.strftime('%Y')
    return Crumb(year, reverse('zinnia:entry_archive_year',
                               args=[year]))


def month_crumb(date):
    """
    Crumb for a month.
    """
    year = date.strftime('%Y')
    month = date.strftime('%m')
    month_text = format(date, 'F').capitalize()
    return Crumb(month_text, reverse('zinnia:entry_archive_month',
                                     args=[year, month]))


def day_crumb(date):
    """
    Crumb for a day.
    """
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    return Crumb(day, reverse('zinnia:entry_archive_day',
                              args=[year, month, day]))


def entry_breadcrumbs(entry):
    """
    Breadcrumbs for an Entry.
    """
    date = entry.publication_date
    if is_aware(date):
        date = localtime(date)
    return [year_crumb(date), month_crumb(date),
            day_crumb(date), Crumb(entry.title)]

MODEL_BREADCRUMBS = {'Tag': lambda x: [Crumb(_('Tags'),
                                             reverse('zinnia:tag_list')),
                                       Crumb(x.name)],
                     'Author': lambda x: [Crumb(_('Authors'),
                                                reverse('zinnia:author_list')),
                                          Crumb(x.__str__())],
                     'Category': lambda x: [Crumb(
                         _('Categories'), reverse('zinnia:category_list'))] +
                     [Crumb(anc.__str__(), anc.get_absolute_url())
                      for anc in x.get_ancestors()] + [Crumb(x.title)],
                     'Entry': entry_breadcrumbs}

ARCHIVE_REGEXP = re.compile(
    r'.*(?P<year>\d{4})/(?P<month>\d{2})?/(?P<day>\d{2})?.*')

ARCHIVE_WEEK_REGEXP = re.compile(
    r'.*(?P<year>\d{4})/week/(?P<week>\d+)?.*')

PAGE_REGEXP = re.compile(r'page/(?P<page>\d+).*$')


def handle_page_crumb(func):
    """
    Decorator for handling the current page in the breadcrumbs.
    """
    @wraps(func)
    def wrapper(path, model, page, root_name):
        path = PAGE_REGEXP.sub('', path)
        breadcrumbs = func(path, model, root_name)
        if page:
            if page.number > 1:
                breadcrumbs[-1].url = path
                page_crumb = Crumb(_('Page %s') % page.number)
                breadcrumbs.append(page_crumb)
        return breadcrumbs
    return wrapper


@handle_page_crumb
def retrieve_breadcrumbs(path, model_instance, root_name=''):
    """
    Build a semi-hardcoded breadcrumbs
    based of the model's url handled by Zinnia.
    """
    breadcrumbs = []
    zinnia_root_path = reverse('zinnia:entry_archive_index')

    if root_name:
        breadcrumbs.append(Crumb(root_name, zinnia_root_path))

    if model_instance is not None:
        key = model_instance.__class__.__name__
        if key in MODEL_BREADCRUMBS:
            breadcrumbs.extend(MODEL_BREADCRUMBS[key](model_instance))
            return breadcrumbs

    date_match = ARCHIVE_WEEK_REGEXP.match(path)
    if date_match:
        year, week = date_match.groups()
        year_date = datetime(int(year), 1, 1)
        date_breadcrumbs = [year_crumb(year_date),
                            Crumb(_('Week %s') % week)]
        breadcrumbs.extend(date_breadcrumbs)
        return breadcrumbs

    date_match = ARCHIVE_REGEXP.match(path)
    if date_match:
        date_dict = date_match.groupdict()
        path_date = datetime(
            int(date_dict['year']),
            date_dict.get('month') is not None and
            int(date_dict.get('month')) or 1,
            date_dict.get('day') is not None and
            int(date_dict.get('day')) or 1)

        date_breadcrumbs = [year_crumb(path_date)]
        if date_dict['month']:
            date_breadcrumbs.append(month_crumb(path_date))
        if date_dict['day']:
            date_breadcrumbs.append(day_crumb(path_date))
        breadcrumbs.extend(date_breadcrumbs)
        breadcrumbs[-1].url = None
        return breadcrumbs

    url_components = [comp for comp in
                      path.replace(zinnia_root_path, '', 1).split('/')
                      if comp]
    if len(url_components):
        breadcrumbs.append(Crumb(_(url_components[-1].capitalize())))

    return breadcrumbs
