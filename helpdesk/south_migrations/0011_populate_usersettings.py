# -*- coding: utf-8 -*-
from __future__ import absolute_import
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.contrib.auth import get_user_model
from helpdesk.settings import DEFAULT_USER_SETTINGS


def pickle_settings(data):
    """
    Serialize and encode the given data using cPickle and base64 encoding.
    
    This function pickles the given data object using cPickle and then
    encodes the pickled bytes into a base64 string. This approach ensures
    consistent serialization of user settings as defined at migration creation time.
    
    Args:
        data (Any): The Python object (typically a dict) representing user settings.
        
    Returns:
        str: A base64 encoded string representing the pickled data.
    """
    """Pickling as defined at migration's creation time"""
    import pickle
    from helpdesk.lib import b64encode
    return b64encode(pickle.dumps(data))


# https://docs.djangoproject.com/en/1.7/topics/migrations/#data-migrations
def populate_usersettings(orm):
    """Create a UserSettings entry for each existing user.
    This will only happen once (at install time, or at upgrade)
    when the UserSettings model doesn't already exist."""

    _User = get_user_model()
    
    # Import historical version of models
    User = orm[_User._meta.app_label+'.'+_User._meta.model_name]
    UserSettings = orm["helpdesk"+'.'+"UserSettings"]
    settings_pickled = pickle_settings(DEFAULT_USER_SETTINGS)

    for u in User.objects.all():
        try:
            UserSettings.objects.get(user=u)
        except UserSettings.DoesNotExist:
            UserSettings.objects.create(user=u, settings_pickled=settings_pickled)

class Migration(DataMigration):
    """
    South data migration class to populate UserSettings for existing users.
    
    This migration runs the populate_usersettings function forwards, and does not
    implement backwards migration since removing these settings could cause data loss.
    
    Attributes:
        models (dict): Dictionary of models used during the migration.
    """
    def forwards(self, orm):
        """
        Run the data migration forwards to populate UserSettings for all users.
        
        Args:
            orm (object): The historical ORM passed by South.
        """
        populate_usersettings(orm)

    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'helpdesk.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'settings_pickled': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['helpdesk']
    symmetrical = True
