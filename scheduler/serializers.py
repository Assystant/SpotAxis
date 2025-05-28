from rest_framework import serializers
from .models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    local_time = serializers.SerializerMethodField()
    local_time_only = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id',
            'scheduled_on',
            'offset',
            'user',
            'status',
            'status_display',
            'application',
            'local_time',
            'local_time_only',
        ]

    def get_local_time(self, obj):
        return obj.local_time()

    def get_local_time_only(self, obj):
        return obj.local_time_only()