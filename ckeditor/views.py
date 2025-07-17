from __future__ import absolute_import
from datetime import datetime
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext

from ckeditor import image_processing
from ckeditor import utils

"""
This module provides views and utility functions to handle image uploads and browsing
for CKEditor integration in a Django project.

Features:
- Secure image uploads with user-based directory restrictions.
- Image validation and thumbnail generation using CKEditor image backend.
- Recursive browsing of uploaded images with URL generation for display.
- Support for per-user upload directories controlled via settings.
- Integration with Django's default storage system for flexible file handling.

Includes:
- ImageUploadView: Class-based view to accept and process image uploads.
- Utility functions for filename generation, image file discovery, URL construction, and file type checks.
- A browse view rendering a gallery of uploaded images for user interaction.

Dependencies:
- Django framework (views, storage, settings).
- CKEditor Python package for image processing utilities.
"""

def get_upload_filename(upload_name, user):
    """
    Generate a valid upload path and filename for a given uploaded file.

    If CKEDITOR_RESTRICT_BY_USER setting is True, the file is saved in a user-specific directory.
    The path is organized by the current date (year/month/day).
    Optionally slugifies the filename if CKEDITOR_UPLOAD_SLUGIFY_FILENAME is True.

    Args:
        upload_name (str): Original name of the uploaded file.
        user (User): Django User instance performing the upload.

    Returns:
        str: Full available filename including path within the storage.
    """
    # If CKEDITOR_RESTRICT_BY_USER is True upload file to user specific path.
    if getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''

    # Generate date based path to put uploaded file.
    date_path = datetime.now().strftime('%Y/%m/%d')

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(
        settings.CKEDITOR_UPLOAD_PATH, user_path, date_path)

    if getattr(settings, "CKEDITOR_UPLOAD_SLUGIFY_FILENAME", True):
        upload_name = utils.slugify_filename(upload_name)

    return default_storage.get_available_name(os.path.join(upload_path, upload_name))


class ImageUploadView(generic.View):
    """
    Django view to handle image uploads from CKEditor.

    Accepts only POST requests with an uploaded file named 'upload'.
    Verifies the uploaded file is a valid image.
    Saves the file to storage, creates thumbnails if backend requires.
    Returns a JavaScript snippet to CKEditor callback with the uploaded file URL.

    Attributes:
        http_method_names (list): List of allowed HTTP methods. Only 'post' allowed.
    """
    http_method_names = ['post']

    def post(self, request, **kwargs):
        """
        Uploads a file and send back its URL to CKEditor.
        """
        """
        Handle POST request to upload an image file.

        Verifies the file, saves it, generates a thumbnail if needed,
        and returns a JS callback for CKEditor.

        Args:
            request (HttpRequest): Django HttpRequest object containing the file.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: JavaScript response calling CKEditor callback function.
        """
        # Get the uploaded file from request.
        upload = request.FILES['upload']

        #Verify that file is a valid image
        backend = image_processing.get_backend()
        try:
            backend.image_verify(upload)
        except utils.NotAnImageException:
            return HttpResponse("""
                       <script type='text/javascript'>
                            alert('Invalid image')
                            window.parent.CKEDITOR.tools.callFunction({0});
                       </script>""".format(request.GET['CKEditorFuncNum']))

        # Open output file in which to store upload.
        upload_filename = get_upload_filename(upload.name, request.user)
        saved_path = default_storage.save(upload_filename, upload)

        if backend.should_create_thumbnail(saved_path):
            backend.create_thumbnail(saved_path)

        url = utils.get_media_url(saved_path)

        # Respond with Javascript sending ckeditor upload url.
        return HttpResponse("""
        <script type='text/javascript'>
            window.parent.CKEDITOR.tools.callFunction({0}, '{1}');
        </script>""".format(request.GET['CKEditorFuncNum'], url))

upload = csrf_exempt(ImageUploadView.as_view())


def get_image_files(user=None, path=''):
    """
    Recursively walks all dirs under upload dir and generates a list of
    full paths for each file found.
    """
    """
    Recursively yield all image file paths under the CKEditor upload directory.

    If user is provided and CKEDITOR_RESTRICT_BY_USER is True, restricts to user-specific directories,
    except for superusers.
    """
    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    STORAGE_DIRECTORIES = 0
    STORAGE_FILES = 1

    restrict = getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False)
    if user and not user.is_superuser and restrict:
        user_path = user.username
    else:
        user_path = ''

    browse_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, user_path, path)

    try:
        storage_list = default_storage.listdir(browse_path)
    except NotImplementedError:
        return
    except OSError:
        return

    for filename in storage_list[STORAGE_FILES]:
        if os.path.splitext(filename)[0].endswith('_thumb') or os.path.basename(filename).startswith('.'):
            continue
        filename = os.path.join(browse_path, filename)
        yield filename

    for directory in storage_list[STORAGE_DIRECTORIES]:
        if directory.startswith('.'):
            continue
        directory_path = os.path.join(path, directory)
        for element in get_image_files(user=user, path=directory_path):
            yield element


def get_files_browse_urls(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    thumbnail and full image URL's for each file found.
    """
    """
    Generate a list of dictionaries representing images with URLs for browsing in CKEditor.
    """
    files = []
    for filename in get_image_files(user=user):
        src = utils.get_media_url(filename)
        if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
            thumb = utils.get_media_url(utils.get_thumb_filename(filename))
        else:
            thumb = src
        files.append({
            'thumb': thumb,
            'src': src,
            'is_image': is_image(src)
        })

    return files


def is_image(path):
    """
    #Check if a given file path corresponds to an image based on file extension.

    #Supported image extensions: jpg, jpeg, png, gif.
    """
    ext = path.split('.')[-1].lower()
    return ext in ['jpg', 'jpeg', 'png', 'gif']


def browse(request):
    """
    View to render a browsing interface for uploaded images.

    Passes a list of image files and their URLs in the template context.
    """
    context = {
        'files': get_files_browse_urls(request.user),
    }
    return render(request,'browse.html', context)
    