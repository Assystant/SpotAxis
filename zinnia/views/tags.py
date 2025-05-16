"""
Views for Zinnia tags.

This module defines views to list all tags used in blog entries,
and to display all entries associated with a specific tag.
"""

from django.http import Http404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView, BaseListView

from tagging.models import Tag, TaggedItem
from tagging.utils import get_tag

from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin


class TagList(ListView):
    """
    View for listing all tags associated with published entries.

    Renders a template with all tags used on the site, along with
    the number of times each tag appears.
    """
    template_name = 'zinnia/tag_list.html'
    context_object_name = 'tag_list'

    def get_queryset(self):
        """
        Return a list of tags used by published entries.

        Each tag is annotated with `count` — the number of entries tagged with it.
        """
        return Tag.objects.usage_for_queryset(
            Entry.published.all(), counts=True
        )


class BaseTagDetail(object):
    """
    Mixin that provides the logic for tag detail views.

    Responsibilities:
    - Resolve a tag name to a `Tag` object
    - Retrieve entries associated with that tag
    - Inject the tag object into the template context
    """

    def get_queryset(self):
        """
        Retrieve the tag by name and return entries tagged with it.

        Raises:
            Http404: If no tag is found for the given name.
        """
        self.tag = get_tag(self.kwargs['tag'])
        if self.tag is None:
            raise Http404(_('No Tag found matching "%s".') % self.kwargs['tag'])

        return TaggedItem.objects.get_by_model(Entry.published.all(), self.tag)

    def get_context_data(self, **kwargs):
        """
        Add the resolved tag to the template context.
        """
        context = super(BaseTagDetail, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class TagDetail(EntryQuerysetTemplateResponseMixin,
                PrefetchCategoriesAuthorsMixin,
                BaseTagDetail,
                BaseListView):
    """
    View for displaying all entries associated with a specific tag.

    Combines:
    - EntryQuerysetTemplateResponseMixin: for customizable templates.
    - PrefetchCategoriesAuthorsMixin: for performance optimizations.
    - BaseTagDetail: for tag resolution and entry retrieval.
    - BaseListView: for list pagination and rendering.
    """
    model_type = 'tag'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        Return the slugified version of the tag name.
        Useful for template resolution and breadcrumbs.
        """
        return slugify(self.tag)
