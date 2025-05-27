# -*- coding: utf-8 -*-


from __future__ import absolute_import
import os
from sys import path

from django.db import models, migrations
from django.core import serializers

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filename = 'emailtemplate.json'

def deserialize_fixture():
    """
    Load and deserialize JSON fixture data from a predefined file.

    Reads the JSON fixture file located in the fixtures directory, deserializes its
    contents into Django model instances, and returns them as a list.

    Returns:
        list: A list of deserialized Django model instances from the fixture.

    Notes:
        The deserialization process ignores non-existent fields to maintain compatibility.
    """

    fixture_file = os.path.join(fixture_dir, fixture_filename)

    with open(fixture_file, 'rb') as fixture:
        return list(serializers.deserialize('json', fixture, ignorenonexistent=True))


def load_fixture(apps, schema_editor):
    """
    Load and save deserialized fixture objects into the database.

    This function is intended to be run during a data migration to populate the database
    with predefined EmailTemplate objects from the JSON fixture.

    Parameters:
        apps (Apps): The registry of historical models available during migration.
        schema_editor (SchemaEditor): The database schema editor for executing SQL.
    """
    objects = deserialize_fixture()

    for obj in objects:
        obj.save()


def unload_fixture(apps, schema_editor):
    """
    Remove EmailTemplate objects or all that were loaded from the fixture.

    This function deletes all EmailTemplate instances matching the primary keys of
    the deserialized fixture objects. It is used as the reverse operation of
    `load_fixture` during migration rollback.

    Parameters:
        apps (Apps): The registry of historical models available during migration.
        schema_editor (SchemaEditor): The database schema editor for executing SQL.
    """


    objects = deserialize_fixture()

    EmailTemplate = apps.get_model("helpdesk", "emailtemplate")
    EmailTemplate.objects.filter(pk__in=[ obj.object.pk for obj in objects ]).delete()


class Migration(migrations.Migration):
    """Defines the migration for loading and unloading EmailTemplate fixtures."""
    dependencies = [
        ('helpdesk', '0002_populate_usersettings'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
