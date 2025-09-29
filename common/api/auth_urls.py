from django.urls import path, re_path
from .views import AuthViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', AuthViewSet.as_view({'post': 'signup'}), name='auth_signup'),
    path('login/', TokenObtainPairView.as_view(), name='auth_login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='auth_logout'),
    re_path(r'^verify/(?P<activation_key>[^/.]+)/$', AuthViewSet.as_view({'get': 'verify'}), name='auth_verify'),
    path('password/change/', AuthViewSet.as_view({'post': 'password_change'}), name='auth_password_change'),
    path('password/reset/', AuthViewSet.as_view({'post': 'password_reset'}), name='auth_password_reset'),
    path('password/reset/confirm/', AuthViewSet.as_view({'post': 'password_reset_confirm'}), name='auth_password_reset_confirm'),
    path('username/recover/', AuthViewSet.as_view({'post': 'username_recover'}), name='auth_username_recover'),
]
