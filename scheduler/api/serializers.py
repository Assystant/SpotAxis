from rest_framework import serializers
from scheduler.models import Schedule
from vacancies.api.serializers import PostulateSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    application = PostulateSerializer(read_only=True)
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=Schedule.objects.all(),
        source='application',
        write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    local_time = serializers.DateTimeField(read_only=True)
    local_time_only = serializers.TimeField(read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'scheduled_on', 'offset', 'status', 'status_display',
            'application', 'application_id', 'user',
            'local_time', 'local_time_only'
        ]
        read_only_fields = [
            'id', 'status_display', 'local_time',
            'local_time_only', 'user'
        ] 