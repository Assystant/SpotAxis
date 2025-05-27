from __future__ import absolute_import
import mimetypes
import os.path
import random
import string

from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify

"""This module provides utility functions and exceptions for handling file
operations related to image uploads, specifically for CKEditor integration in Django.

It includes functions to slugify filenames, generate random strings,
construct thumbnail filenames, retrieve MIME types for image extensions,
and obtain media URLs from stored file paths."""

class NotAnImageException(Exception):
    """
    Exception raised when a file is determined not to be a valid image.

    This exception can be used to handle invalid image uploads or processing errors
    where the file content does not correspond to an image format.
    """
    pass


def slugify_filename(filename):
    """Slugify a filename to make it safe for URLs and file systems."""
    name, ext = os.path.splitext(filename)
    slugified = get_slugified_name(name)
    return slugified + ext


def get_slugified_name(filename):
    """Slugify a string or return a random string if slugification results in an empty string."""
    slugified = slugify(filename)
    return slugified or get_random_string()


def get_random_string():
    """Generate a random string of 6 lowercase letters."""
    return ''.join(random.sample(string.ascii_lowercase*6, 6))


def get_thumb_filename(file_name):
    """
    Generate thumb filename by adding _thumb to end of
    filename before . (if present)
    """
    return '{0}_thumb{1}'.format(*os.path.splitext(file_name))


def get_image_format(extension):
    """Get the MIME type corresponding to a file extension."""
    mimetypes.init()
    return mimetypes.types_map[extension.lower()]


def get_media_url(path):
    """
    Determine system file's media URL.
    Get the media URL for a given storage path.
    """
    return default_storage.url(path)
