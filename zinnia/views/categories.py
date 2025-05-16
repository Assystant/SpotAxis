"""
Views for Zinnia categories.

This module provides class-based views to display lists of blog categories 
and detailed views of entries grouped under a specific category.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic.list import BaseListView, ListView

from zinnia.models.category import Category
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin


def get_category_or_404(path):
    """
    Retrieve a `Category` instance by its path.

    The path is assumed to be a slash-separated string of category slugs,
    with the final slug identifying the target category.

    Args:
        path (str): A string path like 'programming/python/advanced'

    Returns:
        Category: A matching Category instance or raises 404.
    """
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


class CategoryList(ListView):
    """
    View to display a list of all published categories.

    Each category is annotated with the number of published entries
    that belong to it.
    """

    def get_queryset(self):
        """
        Return all published categories, each annotated with
        `count_entries_published`, the number of published entries.
        """
        return Category.published.all().annotate(
            count_entries_published=Count('entries'))


class BaseCategoryDetail(object):
    """
    Mixin providing the logic for category detail views.

    This mixin:
    - Fetches the category based on the slug path.
    - Retrieves the entries published under that category.
    - Injects the category into the view context.
    """

    def get_queryset(self):
        """
        Retrieve the category by its slug path and return its published entries.

        Uses `get_category_or_404()` to extract the category based on the
        last component in the path.
        """
        self.category = get_category_or_404(self.kwargs['path'])
        return self.category.entries_published()

    def get_context_data(self, **kwargs):
        """
        Add the current category instance to the template context.
        """
        context = super(BaseCategoryDetail, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CategoryDetail(EntryQuerysetTemplateResponseMixin,
                     PrefetchCategoriesAuthorsMixin,
                     BaseCategoryDetail,
                     BaseListView):
    """
    Detailed view for displaying entries in a given category.

    This view combines multiple mixins:
    - EntryQuerysetTemplateResponseMixin:
        Provides custom template resolution for categories.
    - PrefetchCategoriesAuthorsMixin:
        Optimizes DB queries by prefetching related objects.
    - BaseCategoryDetail:
        Fetches the category and associated entries.
    - BaseListView:
        Adds pagination and list-rendering support.
    """
    model_type = 'category'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        Return the category's slug to be used as its model name.
        """
        return self.category.slug
