from rest_framework import serializers
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from zinnia.models import Entry, Author, Category
from zinnia.managers import PUBLISHED
from django.utils import timezone

# Import existing serializers from other modules
from ckeditor.api.serializers import RichTextSerializer
from scheduler.api.serializers import ScheduleSerializer
from customField.api.serializers import FieldSerializer


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model (uses the custom user model).

    Adds calculated fields:
    - entries_count: Total entries written by the author.
    - published_entries_count: Total published entries by the author.
    """
    entries_count = serializers.SerializerMethodField()
    published_entries_count = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'entries_count', 'published_entries_count', 'get_absolute_url'
        ]
        read_only_fields = ['id', 'entries_count', 'published_entries_count', 'get_absolute_url']

    def get_entries_count(self, obj):
        """
        Returns the total number of entries by the author.
        """
        return obj.entries.count()

    def get_published_entries_count(self, obj):
        """
        Returns the number of published entries by the author.
        """
        return obj.entries.filter(status=PUBLISHED).count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    tree_path = serializers.CharField(read_only=True)
    entries_count = serializers.SerializerMethodField()
    published_entries_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'title', 'slug', 'description', 'parent',
            'tree_path', 'entries_count', 'published_entries_count',
            'children', 'get_absolute_url'
        ]
        read_only_fields = [
            'id', 'tree_path', 'entries_count',
            'published_entries_count', 'children', 'get_absolute_url'
        ]

    def get_entries_count(self, obj):
        """
        Returns the total number of entries in this category.
        """
        return obj.entries.count()

    def get_published_entries_count(self, obj):
        """
        Returns the number of published entries in this category.
        """
        return obj.entries.filter(status=PUBLISHED).count()

    def get_children(self, obj):
        """
        Returns the serialized child categories for this category.
        """
        children = obj.get_children()
        if children:
            return CategorySerializer(children, many=True).data
        return []


class EntrySerializer(serializers.ModelSerializer):
    """Serializer for the Entry model (blog post)."""
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    sites = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.all(),
        many=True
    )
    ckeditor_content = RichTextSerializer(source='ckeditor', read_only=True)
    scheduler = ScheduleSerializer(read_only=True)
    custom_fields = FieldSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    html_content = serializers.CharField(read_only=True)
    html_preview = serializers.CharField(read_only=True)
    word_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(source='comment_count', read_only=True)
    pingbacks_count = serializers.IntegerField(source='pingback_count', read_only=True)
    trackbacks_count = serializers.IntegerField(source='trackback_count', read_only=True)
    is_actual = serializers.BooleanField(read_only=True)
    is_visible = serializers.BooleanField(read_only=True)
    short_url = serializers.URLField(read_only=True)
    related_entries = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = [
            'id', 'title', 'slug', 'status', 'status_display',
            'publication_date', 'start_publication', 'end_publication',
            'sites', 'creation_date', 'last_update',
            'content', 'html_content', 'html_preview', 'word_count',
            'lead', 'excerpt', 'image', 'image_caption',
            'featured', 'authors', 'categories', 'tags',
            'comment_enabled', 'pingback_enabled', 'trackback_enabled',
            'comments_count', 'pingbacks_count', 'trackbacks_count',
            'login_required', 'password',
            'content_template', 'detail_template',
            'is_actual', 'is_visible', 'short_url',
            'related_entries', 'get_absolute_url',
            'ckeditor_content', 'scheduler', 'custom_fields'
        ]
        read_only_fields = [
            'id', 'creation_date', 'last_update',
            'html_content', 'html_preview', 'word_count',
            'comments_count', 'pingbacks_count', 'trackbacks_count',
            'is_actual', 'is_visible', 'short_url',
            'related_entries', 'get_absolute_url',
            'ckeditor_content', 'scheduler', 'custom_fields'
        ]

    def get_related_entries(self, obj):
        related = obj.related_published
        if related:
            return EntrySerializer(related, many=True).data
        return []

    def validate(self, data):
        """
        Check that start_publication is before end_publication.
        """
        if data.get('start_publication') and data.get('end_publication'):
            if data['start_publication'] > data['end_publication']:
                raise serializers.ValidationError(
                    "End publication must occur after start publication"
                )
        return data 