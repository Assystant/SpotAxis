"""
URLs for the Zinnia comment views.

This module provides a URL endpoint for handling post-comment submission
behavior — specifically, the redirection or rendering of a success/confirmation
page after a user posts a comment.

View Used:
- CommentSuccess: Determines if a comment is visible (public) and either
  redirects to it or shows a confirmation message.
"""

from django.conf.urls import url

from zinnia.urls import _  # Optional translation for URL patterns
from zinnia.views.comments import CommentSuccess

urlpatterns = [
    # ---------------------------------------------------------
    # Comment Success View
    # Example: /comments/success/
    # Determines whether to redirect to the comment or show a message.
    # Used after a comment form is submitted (e.g., via POST).
    # ---------------------------------------------------------
    url(_(r'^success/$'),
        CommentSuccess.as_view(),
        name='comment_success'),
]
