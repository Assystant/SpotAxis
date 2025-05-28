from rest_framework import serializers
from activities.models import *

class MessageChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model= MessageChunk
        fields='__all__'
        read_only_fields=('last_updated')
    

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Activity
        fields='__all__'
        read_only_fields=('last_updated','timestamp')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Notification
        fields='__all__'
        read_only_fields=('last_updated','timestamp','seen')

