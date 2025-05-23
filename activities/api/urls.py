from rest_framework import DefaultRouter

from activities.api.views import ActivityViewSet,MessageChunkViewSet,NotificationViewSet


router= DefaultRouter()

router.register(r'activities', ActivityViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'message-chunks', MessageChunkViewSet)

urlpatterns= router.urls