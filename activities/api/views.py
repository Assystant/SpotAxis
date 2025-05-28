from rest_framework import viewsets
from activities.models import Activity, Notification, MessageChunk

from activities.api.serializers import *


class ActivityViewSet(viewsets.ModelViewSet):
    queryset= Activity.objects.all()
    serializer_class= ActivitySerializer


class MessageChunkViewSet(viewsets.ModelViewSet):
    queryset= MessageChunk.objects.all()
    serializer_class= MessageChunkSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset= Notification.objects.all()
    serializer_class= NotificationSerializer

