# -*- coding: utf-8 -*-


from __future__ import absolute_import
from django.contrib.auth import get_user_model
from django.db import models, migrations

from helpdesk.settings import DEFAULT_USER_SETTINGS


def picke_settings(data):
    """Pickling as defined at migration's creation time"""
    """
    Serialize and encode the given data using pickle and base64.

    This function pickles the provided Python data object using the pickle module
    and then encodes the pickled byte stream into a base64 string for safe storage.

    The implementation imports pickle with backward compatibility for Python 2 and 3.

    Parameters:
        data (any): The Python object to be serialized.

    Returns:
        str: A base64-encoded string of the pickled data.
    """
    try:
        import pickle
    except ImportError:
        import pickle as pickle
    from helpdesk.lib import b64encode
    return b64encode(pickle.dumps(data))


# https://docs.djangoproject.com/en/1.7/topics/migrations/#data-migrations
def populate_usersettings(apps, schema_editor):
    """Create a UserSettings entry for each existing user.
    This will only happen once (at install time, or at upgrade)
    when the UserSettings model doesn't already exist."""

    _User = get_user_model()
    User = apps.get_model(_User._meta.app_label, _User._meta.model_name)

    # Import historical version of models
    UserSettings = apps.get_model("helpdesk", "UserSettings")

    settings_pickled = picke_settings(DEFAULT_USER_SETTINGS)

    for u in User.objects.all():
        try:
            UserSettings.objects.get(user=u)
        except UserSettings.DoesNotExist:
            UserSettings.objects.create(user=u, settings_pickled=settings_pickled)


noop = lambda *args, **kwargs: None

class Migration(migrations.Migration):
    """
    Defines the database migration for populating user settings.

    This migration depends on the initial migration '0001_initial' and runs a data
    migration operation to create default UserSettings entries for existing users.

    Attributes:
        dependencies (list): List of migration dependencies that must be applied before this one.
        operations (list): List of migration operations to be performed, including the
                        data population function and a no-op reverse migration.
    """

    dependencies = [
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_usersettings, reverse_code=noop),
    ]


