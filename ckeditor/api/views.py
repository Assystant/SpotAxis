from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ckeditor import utils
from ckeditor import image_processing
from ckeditor.views import *

class UploadImageAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        file = request.FILES.get('upload')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        backend = image_processing.get_backend()
        try:
            backend.image_verify(file)
        except utils.NotAnImageException:
            return Response({"error": "Invalid image"}, status=400)

        filename = get_upload_filename(file.name, request.user)
        saved_path = default_storage.save(filename, file)

        if backend.should_create_thumbnail(saved_path):
            backend.create_thumbnail(saved_path)

        url = utils.get_media_url(saved_path)
        return Response({"url": url})

class BrowseImagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        files = get_files_browse_urls(request.user)
        return Response(files)