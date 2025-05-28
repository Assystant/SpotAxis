from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from zinnia.models import Entry, Author, Category
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from .serializers import EntrySerializer, AuthorSerializer, CategorySerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an entry to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the authors of the entry
        if isinstance(obj, Entry):
            return request.user in obj.authors.all()
        return False


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name', 'email']

    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get all entries by this author"""
        author = self.get_object()
        entries = author.entries.all()
        serializer = EntrySerializer(entries, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def published_entries(self, request, pk=None):
        """Get published entries by this author"""
        author = self.get_object()
        entries = author.entries.filter(status=PUBLISHED)
        serializer = EntrySerializer(entries, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'slug', 'description']
    ordering_fields = ['title', 'slug']
    filterset_fields = ['parent']

    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get all entries in this category"""
        category = self.get_object()
        entries = category.entries.all()
        serializer = EntrySerializer(entries, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def published_entries(self, request, pk=None):
        """Get published entries in this category"""
        category = self.get_object()
        entries = category.entries.filter(status=PUBLISHED)
        serializer = EntrySerializer(entries, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get the complete category tree"""
        root_categories = Category.objects.filter(parent=None)
        serializer = CategorySerializer(root_categories, many=True, context={'request': request})
        return Response(serializer.data)


class EntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing blog entries.
    """
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'slug', 'content', 'lead', 'excerpt']
    ordering_fields = [
        'title', 'slug', 'publication_date', 'creation_date', 
        'last_update', 'featured', 'comment_count'
    ]
    filterset_fields = [
        'status', 'featured', 'authors', 'categories', 
        'sites', 'comment_enabled', 'login_required'
    ]

    def get_queryset(self):
        """
        Optionally restricts the returned entries based on various filters.
        """
        queryset = Entry.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(publication_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(publication_date__lte=end_date)
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__in=tag_list).distinct()
        
        return queryset

    @action(detail=False, methods=['get'])
    def published(self, request):
        """Get all published entries"""
        entries = Entry.objects.filter(status=PUBLISHED)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get all featured entries"""
        entries = Entry.objects.filter(featured=True)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent entries (last 5)"""
        entries = Entry.objects.filter(
            status=PUBLISHED,
            publication_date__lte=timezone.now()
        ).order_by('-publication_date')[:5]
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an entry"""
        entry = self.get_object()
        if entry.status != PUBLISHED:
            entry.status = PUBLISHED
            entry.save()
            serializer = self.get_serializer(entry)
            return Response(serializer.data)
        return Response(
            {'detail': 'Entry is already published.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish an entry"""
        entry = self.get_object()
        if entry.status == PUBLISHED:
            entry.status = DRAFT
            entry.save()
            serializer = self.get_serializer(entry)
            return Response(serializer.data)
        return Response(
            {'detail': 'Entry is not published.'},
            status=status.HTTP_400_BAD_REQUEST
        )
