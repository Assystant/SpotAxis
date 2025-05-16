"""
Views for Zinnia trackbacks.

This module provides a view to receive and process trackbacks
from other blogs, allowing them to notify when they link to an entry.
"""

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import django_comments as comments

from zinnia.flags import TRACKBACK, get_user_flagger
from zinnia.models.entry import Entry
from zinnia.signals import trackback_was_posted


class EntryTrackback(TemplateView):
    """
    View for handling incoming trackbacks to blog entries.

    A trackback is a type of comment where another blog notifies
    this site that it has linked to one of its entries.

    Supported Methods:
    - GET: Redirects to the entry's full URL.
    - POST: Accepts and records a trackback.
    """
    content_type = 'text/xml'
    template_name = 'zinnia/entry_trackback.xml'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Disable CSRF protection for this view,
        as trackbacks typically originate from external systems.
        """
        return super(EntryTrackback, self).dispatch(*args, **kwargs)

    def get_object(self):
        """
        Retrieve the target Entry based on its primary key (from URL kwargs).

        Returns:
            Entry: A published blog entry object.
        """
        return get_object_or_404(Entry.published, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """
        On GET requests, redirect permanently to the entry's canonical URL.

        This provides graceful handling if a user or bot visits the trackback endpoint.
        """
        entry = self.get_object()
        return HttpResponsePermanentRedirect(entry.get_absolute_url())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to submit a new trackback.

        Required POST parameters:
            - url: The source URL linking to the entry.

        Optional:
            - title: The title of the referring page.
            - excerpt: A short summary or snippet.
            - blog_name: The name of the referring blog.

        If trackbacks are disabled for the entry, or if the URL
        has already been registered, a descriptive error response is rendered.
        Otherwise, the trackback is recorded as a `django_comment`,
        flagged as a trackback, and a signal is emitted.
        """
        url = request.POST.get('url')

        if not url:
            # If no URL, fallback to GET behavior
            return self.get(request, *args, **kwargs)

        entry = self.get_object()
        site = Site.objects.get_current()

        if not entry.trackbacks_are_open:
            return self.render_to_response({
                'error': 'Trackback is not enabled for %s' % entry.title
            })

        title = request.POST.get('title') or url
        excerpt = request.POST.get('excerpt') or title
        blog_name = request.POST.get('blog_name') or title
        ip_address = request.META.get('REMOTE_ADDR', None)

        # Create or get existing trackback comment
        trackback, created = comments.get_model().objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Entry),
            object_pk=entry.pk,
            site=site,
            user_url=url,
            user_name=blog_name,
            ip_address=ip_address,
            defaults={
                'comment': excerpt,
                'submit_date': timezone.now()
            }
        )

        if created:
            # Mark as a trackback and emit signal
            trackback.flags.create(user=get_user_flagger(), flag=TRACKBACK)
            trackback_was_posted.send(trackback.__class__,
                                      trackback=trackback,
                                      entry=entry)
        else:
            return self.render_to_response({
                'error': 'Trackback is already registered'
            })

        return self.render_to_response({})
