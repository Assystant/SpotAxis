from __future__ import absolute_import
from django.conf import settings
"""
Module to select and provide the appropriate image processing backend
for CKEditor image handling in Django.

Based on the Django settings, this module imports and returns the
configured backend module for image operations.

If the setting 'CKEDITOR_IMAGE_BACKEND' is set to 'pillow', the Pillow
backend is used; otherwise, a dummy backend is provided as fallback.
"""


def get_backend():
    """
    Returns the image processing backend module based on Django settings.

    Checks the 'CKEDITOR_IMAGE_BACKEND' setting to determine which backend
    to use. If set to 'pillow', imports and returns the Pillow backend.
    Otherwise, returns a dummy backend that provides no-op implementations.

    Returns:
        module: The selected backend module for image processing.
    """
    backend = getattr(settings, "CKEDITOR_IMAGE_BACKEND", None)

    if backend == "pillow":
        from ckeditor.image import pillow_backend as backend
    else:
        from ckeditor.image import dummy_backend as backend
    return backend
