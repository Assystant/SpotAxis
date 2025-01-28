"""Context Processors for Zinnia"""
from __future__ import absolute_import
from zinnia import __version__
from zinnia.models import Category
from django.db.models import Count

def version(request):
    """
    Add version of Zinnia to the context.
    """
    return {'ZINNIA_VERSION': __version__,
    		'categories': Category.published.filter(parent=None).annotate(count_entries_published=Count('entries'))
    		}