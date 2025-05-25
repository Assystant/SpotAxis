from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from .views import EntryViewSet, AuthorViewSet, CategoryViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'entries', EntryViewSet, basename='entry')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'categories', CategoryViewSet, basename='category')

# The API URLs are now determined automatically by the router
# We include the docs URLs for API documentation
urlpatterns = [
    path('', include(router.urls)),
    path('docs/', include_docs_urls(title='Zinnia API')),
    path('api-auth/', include('rest_framework.urls')),  # Adds login to the browsable API
]
