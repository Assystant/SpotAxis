from __future__ import absolute_import
import os.path

from ckeditor import utils

"""
Dummy backend for image processing used by django-ckeditor.

This backend provides placeholder implementations for image verification
and thumbnail creation functions. It does not perform any actual image
processing and serves as a fallback when no real image backend is configured.
"""

def create_thumbnail(file_path, format):
    """Dummy function for creating a thumbnail of an image."""
    raise NotImplementedError


def should_create_thumbnail(file_path):
    """Determine whether a thumbnail should be created for the given file."""
    return False


def image_verify(file_object):
    """Verify if the uploaded file is a valid image based on file extension."""
    valid_extensions = ['.jpeg', '.jpg', '.gif', '.png']
    _, extension = os.path.splitext(file_object.name)
    if not extension.lower() in valid_extensions:
        raise utils.NotAnImageException
