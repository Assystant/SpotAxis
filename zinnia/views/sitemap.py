"""
Views for Zinnia HTML-based sitemap.

This module defines a class-based view that renders a sitemap page
listing all published entries, categories, and authors. This is 
separate from an XML sitemap used by search engines.
"""

from django.views.generic import TemplateView

from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry


class Sitemap(TemplateView):
    """
    Human-readable sitemap view for the weblog.

    Renders an HTML template (`zinnia/sitemap.html`) that lists:
    - All published blog entries
    - All published categories
    - All published authors

    Useful for site visitors who want a full overview of content,
    and can also enhance SEO through internal linking.
    """
    template_name = 'zinnia/sitemap.html'

    def get_context_data(self, **kwargs):
        """
        Add all necessary content objects to the context for rendering.

        Returns:
            dict: Template context containing:
                - entries: QuerySet of all published entries
                - categories: QuerySet of all published categories
                - authors: QuerySet of all published authors
        """
        context = super(Sitemap, self).get_context_data(**kwargs)
        context.update({
            'entries': Entry.published.all(),
            'categories': Category.published.all(),
            'authors': Author.published.all()
        })
        return context
