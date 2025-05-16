"""
Author model for Zinnia.

This module defines a proxy model around Django's User model,
enabling additional behaviors specific to authors in the blog system,
such as retrieving published entries and generating author URLs.

It uses a safe utility to support both default and custom user models.
"""

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from zinnia.managers import EntryRelatedPublishedManager
from zinnia.managers import entries_published


def safe_get_user_model():
    """
    Safely loads the configured User model, whether it's the default
    Django User model or a custom one defined via AUTH_USER_MODEL.

    Returns:
        Model: The registered user model class.
    """
    user_app, user_model = settings.AUTH_USER_MODEL.split('.')
    return apps.get_registered_model(user_app, user_model)


class AuthorPublishedManager(models.Model):
    """
    Abstract model that adds a custom manager for retrieving published entries
    related to an author, without overriding the original User model's manager.

    This solves issue #307 related to manager conflicts in proxy models.
    """
    published = EntryRelatedPublishedManager()

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Author(safe_get_user_model(), AuthorPublishedManager):
    """
    Proxy model around the configured User model (custom or default).

    Extends the User model to support additional blog-related features,
    such as getting an author's published entries and constructing their
    profile URL for the Zinnia blog system.

    This does not create a new database table.
    """

    def entries_published(self):
        """
        Retrieves all published blog entries written by this author.

        Returns:
            QuerySet: A queryset of the author's published blog posts.
        """
        return entries_published(self.entries)

    @models.permalink
    def get_absolute_url(self):
        """
        Builds the absolute URL to the author's profile page using their username.

        Returns:
            tuple: A tuple representing the named URL and arguments.
        """
        return ('zinnia:author_detail', [self.get_username()])

    def __str__(self):
        """
        Returns a human-readable representation of the author.

        If the full name is available, it is returned; otherwise, the username is used.

        Returns:
            str: The author's display name.
        """
        return self.get_full_name() or self.get_username()

    class Meta:
        """
        Meta information for the Author proxy model.

        Declares this as a proxy model, meaning it shares the same
        database table as the User model but allows custom behavior.
        """
        proxy = True
