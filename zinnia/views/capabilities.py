"""
Views for Zinnia capabilities.

These views expose metadata and discovery endpoints for clients, bots,
and editors (like Windows Live Writer), following common conventions
such as humans.txt, RSD, and OpenSearch.
"""

from django.contrib.sites.models import Site
from django.views.generic.base import TemplateView

from zinnia.settings import COPYRIGHT, FEEDS_FORMAT, PROTOCOL


class CapabilityView(TemplateView):
    """
    Base view for rendering weblog capability endpoints.

    Injects shared metadata into the template context for various
    capability files like `humans.txt`, `rsd.xml`, etc.
    """

    def get_context_data(self, **kwargs):
        """
        Populate the template context with metadata needed
        for describing the blog's technical capabilities.
        """
        context = super(CapabilityView, self).get_context_data(**kwargs)
        context.update({
            'protocol': PROTOCOL,              # e.g., 'http' or 'https'
            'copyright': COPYRIGHT,            # e.g., '© 2025 by Author'
            'feeds_format': FEEDS_FORMAT,      # e.g., 'atom' or 'rss'
            'site': Site.objects.get_current() # current domain/site object
        })
        return context


class HumansTxt(CapabilityView):
    """
    View to serve a `humans.txt` file.

    Used for providing credit to people behind the website.
    See: http://humanstxt.org/
    """
    content_type = 'text/plain'
    template_name = 'zinnia/humans.txt'


class RsdXml(CapabilityView):
    """
    View to serve `rsd.xml` (Really Simple Discovery).

    Enables editors to discover the blog's API and service endpoints.
    See: https://en.wikipedia.org/wiki/Really_Simple_Discovery
    """
    content_type = 'application/rsd+xml'
    template_name = 'zinnia/rsd.xml'


class WLWManifestXml(CapabilityView):
    """
    View to serve `wlwmanifest.xml`.

    Used by Windows Live Writer and compatible blogging tools
    to interact with blog publishing APIs.
    See: https://learn.microsoft.com/en-us/previous-versions/bb463260(v=msdn.10)
    """
    content_type = 'application/wlwmanifest+xml'
    template_name = 'zinnia/wlwmanifest.xml'


class OpenSearchXml(CapabilityView):
    """
    View to serve `opensearch.xml`.

    Describes how a site’s search engine can be integrated into
    browsers and search boxes.
    See: https://www.opensearch.org/
    """
    content_type = 'application/opensearchdescription+xml'
    template_name = 'zinnia/opensearch.xml'
