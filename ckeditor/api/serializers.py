from rest_framework import serializers
from ckeditor.fields import RichTextField


class RichTextSerializer(serializers.Serializer):
    """
    Serializer for CKEditor's RichTextField.
    This serializer can be used to serialize any model field that uses RichTextField.
    """
    content = serializers.CharField(style={'base_template': 'textarea.html'})

    class Meta:
        fields = ['content'] 