"""
Context Processors for Zinnia
-----------------------------

This module defines context processors that inject globally available
variables into Django templates rendered using RequestContext.

Currently included context data:
1. `ZINNIA_VERSION` - The current installed version of the Zinnia blogging engine.
2. `categories` - A queryset of top-level published blog categories, annotated with
   the count of entries in each category. Useful for rendering blog navigation menus.

To enable this context processor, add it to your Django settings under
the TEMPLATES → OPTIONS → context_processors list:

Example:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                    'zinnia.context_processors.version',
                ],
            },
        },
    ]

This ensures `ZINNIA_VERSION` and `categories` are available in all templates.
"""

from django.db.models import Count
from zinnia import __version__
from zinnia.models import Category


def version(request):
    """
    Inject Zinnia version and top-level categories into the template context.

    This context processor provides:
      - 'ZINNIA_VERSION': The current version string of the Zinnia blog engine.
      - 'categories': A queryset of top-level published categories (i.e., no parent),
        each annotated with the count of published blog entries associated with it.

    This data is useful for:
      - Displaying the version number in the footer or admin dashboard
      - Building navigation menus or sidebars based on available categories

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        dict: A dictionary containing `ZINNIA_VERSION` and `categories`.
    """
    return {
        'ZINNIA_VERSION': __version__,
        'categories': Category.published.filter(parent=None).annotate(
            count_entries_published=Count('entries')
        )
    }
