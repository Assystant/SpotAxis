from django.urls import path, include

app_name = 'common_api'

urlpatterns = [
    path('api/common/', include('common.api.urls')),
] 