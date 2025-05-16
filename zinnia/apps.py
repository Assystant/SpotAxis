"""
App configuration for the Zinnia blog engine used in SpotAxis.

This module sets up the Zinnia app with custom metadata and initializes
comment moderation and signal connections upon application readiness.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ZinniaConfig(AppConfig):
    """
    Configuration class for the Zinnia application.

    Attributes:
        name (str): Full Python path to the application.
        label (str): Short name for the app used internally.
        verbose_name (str): Human-readable name for the admin interface.
    """
    name = 'zinnia'
    label = 'zinnia'
    verbose_name = _('SpotAxis Resources')

    def ready(self):
        """
        Hook executed when the application is ready.

        Registers the Entry model with the comment moderation system
        and connects custom signals for entries and discussions.
        """
        from django_comments.moderation import moderator
        from zinnia.signals import connect_entry_signals
        from zinnia.signals import connect_discussion_signals
        from zinnia.moderator import EntryCommentModerator

        entry_klass = self.get_model('Entry')

        # Register the Entry model for comment moderation
        moderator.register(entry_klass, EntryCommentModerator)

        # Connect blog entry-related signals
        connect_entry_signals()

        # Connect discussion-related signals (comments, pingbacks, etc.)
        connect_discussion_signals()
