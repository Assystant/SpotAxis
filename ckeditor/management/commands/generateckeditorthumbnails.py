from __future__ import absolute_import
import os

from django.conf import settings
from django.core.management.base import NoArgsCommand

from ckeditor.views import get_image_files
from ckeditor.utils import get_thumb_filename
from ckeditor.image_processing import get_backend

"""
Django management command to create thumbnail images for files managed
by django-ckeditor's image browser.

This command scans all existing uploaded images and generates missing
thumbnail files. It is especially useful when integrating django-ckeditor
into a project with pre-existing uploaded images that lack thumbnails.

The command relies on the configured CKEDITOR_IMAGE_BACKEND to perform
thumbnail creation. If no backend is enabled, it exits gracefully.
"""

class Command(NoArgsCommand):
    """
    Creates thumbnail files for the CKEditor file image browser.
    Useful if starting to use django-ckeditor with existing images.
    """
    """
    Management command class to create thumbnails for CKEditor image files.

    Iterates through all image files found in the upload directory,
    checks for the existence of corresponding thumbnails, and generates
    them if missing.
    """
    def handle_noargs(self, **options):
        """
        Entry point for the management command.

        Checks if an image backend is configured and then processes all
        images to create thumbnails where necessary. Outputs progress and
        error messages to the console.
        """
        if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
            backend = get_backend()
            for image in get_image_files():
                if not self._thumbnail_exists(image):
                    self.stdout.write("Creating thumbnail for %s" % image)
                    try:
                        backend.create_thumbnail(image)
                    except Exception as e:
                        self.stdout.write("Couldn't create thumbnail for %s: %s" % (image, e))
            self.stdout.write("Finished")
        else:
            self.stdout.write("No thumbnail backend is enabled")

    def _thumbnail_exists(self, image_path):
        """Checks if a thumbnail file already exists for the given image."""
        thumb_path = self._to_absolute_path(
            get_thumb_filename(image_path)
        )
        return os.path.isfile(thumb_path)

    @staticmethod
    def _to_absolute_path(image_path):
        """Converts a relative media file path to an absolute filesystem path."""
        return os.path.join(settings.MEDIA_ROOT, image_path)
