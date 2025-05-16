"""
Views for Zinnia comments.

This module provides custom handling of comment success pages,
including redirection logic based on comment visibility.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponsePermanentRedirect
from django.template.defaultfilters import slugify
from django.views.generic.base import TemplateResponseMixin, View

import django_comments as comments


class CommentSuccess(TemplateResponseMixin, View):
    """
    View for handling successful submission of a comment on a Zinnia Entry.

    Behavior:
    - If the comment exists and is public, redirect to the comment's permalink.
    - If the comment is not public or doesn't exist, render a confirmation template.

    This logic ensures a user-friendly flow whether moderation is enabled or not.
    """
    template_name = 'comments/zinnia/entry/posted.html'

    def get_context_data(self, **kwargs):
        """
        Provide the comment object to the template context if available.
        """
        return {'comment': self.comment}

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to the comment success endpoint.

        Query Params:
            c (int): The primary key of the comment.

        Returns:
            - Permanent redirect to the comment's anchor if it is public.
            - A rendered success page if the comment is not public or invalid.
        """
        self.comment = None

        if 'c' in request.GET:
            try:
                # Retrieve the comment by primary key
                self.comment = comments.get_model().objects.get(
                    pk=request.GET['c']
                )
            except (ObjectDoesNotExist, ValueError):
                # Invalid or nonexistent comment, fall through to template
                pass

        if self.comment and self.comment.is_public:
            # Redirect to the exact comment anchor on the entry page
            return HttpResponsePermanentRedirect(
                self.comment.get_absolute_url(
                    '#comment-%(id)s-by-') + slugify(self.comment.user_name)
            )

        # If comment isn't public or not found, render fallback template
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
