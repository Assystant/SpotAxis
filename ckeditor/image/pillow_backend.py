from __future__ import absolute_import
from io import BytesIO
import os.path

"""
Pillow backend for image processing used by django-ckeditor.

This backend provides real implementations for image verification
and thumbnail creation using the Pillow (PIL) library. It verifies
uploaded files as images, creates thumbnails of a fixed size, and
determines whether thumbnails should be created for given files.
"""

try:
    from PIL import Image, ImageOps
except ImportError:
    from PIL import Image, ImageOps
    #import Image
    #import ImageOps

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from ckeditor import utils

THUMBNAIL_SIZE = (75, 75)


def image_verify(f):
    """Verify that the uploaded file is a valid image."""
    try:
        Image.open(f).verify()
    except IOError:
        raise utils.NotAnImageException


def create_thumbnail(file_path):
    """
    Create a thumbnail for the specified image file.

    The thumbnail will be a 75x75 pixel image, cropped and scaled to fit.
    """
    thumbnail_filename = utils.get_thumb_filename(file_path)
    thumbnail_format = utils.get_image_format(os.path.splitext(file_path)[1])
    file_format = thumbnail_format.split('/')[1]

    image = default_storage.open(file_path)
    image = Image.open(image)

    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    thumbnail_io = BytesIO()
    imagefit.save(thumbnail_io, format=file_format)

    thumbnail = InMemoryUploadedFile(
        thumbnail_io,
        None,
        thumbnail_filename,
        thumbnail_format,
        len(thumbnail_io.getvalue()),
        None)
    thumbnail.seek(0)

    return default_storage.save(thumbnail_filename, thumbnail)


def should_create_thumbnail(file_path):
    """Determine if a thumbnail should be created for the specified file."""
    image = default_storage.open(file_path)
    try:
        Image.open(image)
    except IOError:
        return False
    else:
        return True
