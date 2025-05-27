from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

"""
Module to validate the Django CKEditor configuration during project startup.

Checks that if 'ckeditor' is included in INSTALLED_APPS, then the mandatory
setting CKEDITOR_UPLOAD_PATH is defined in Django settings. Raises
ImproperlyConfigured if the required setting is missing, guiding the user
to properly configure the upload path for CKEditor media files.

This ensures that the CKEditor file upload functionality has a valid
storage location configured before the application runs.
"""

if 'ckeditor' in settings.INSTALLED_APPS:
    # Confirm CKEDITOR_UPLOAD_PATH setting has been specified.
    try:
        settings.CKEDITOR_UPLOAD_PATH
    except AttributeError:
        raise ImproperlyConfigured("django-ckeditor requires \
                CKEDITOR_UPLOAD_PATH setting. This setting specifies an \
                relative path to your ckeditor media upload directory. Make \
                sure you have write permissions for the path, i.e.: \
                CKEDITOR_UPLOAD_PATH = 'content/ckeditor/' which \
                will be added to SITE_MEDIA/MEDIA_ROOT where needed by storage engine.")
