
from __future__ import absolute_import
from datetime import timedelta
from django.db import models
from TRM import settings
from vacancies.models import Postulate
# Create your models here.
"""
Schedule models module.

Defines the Schedule model which tracks scheduled events linked to user applications.
It supports status tracking and local time adjustments based on an offset value.

Attributes:
    STATUS_CHOICES (tuple): Choices for the status field, indicating whether a schedule is pending or completed.
"""

STATUS_CHOICES = (
    ('0', 'Pending'),
    ('1', 'Completed'),
)

class Schedule(models.Model):
    """
    Model representing a scheduled event for a user application.

    Attributes:
        scheduled_on (datetime): The date and time when the event is scheduled.
        offset (int): Time offset in minutes to adjust the scheduled time, useful for timezone adjustments.
        user (ForeignKey): Reference to the user who created the schedule.
        status (str): Status of the schedule, can be 'Pending' or 'Completed'.
        application (ForeignKey): Reference to the associated application (Postulate).

    Methods:
        local_time(): Returns the scheduled time adjusted by the offset.
        local_time_only(): Returns only the time component of the adjusted scheduled time.
    """
    scheduled_on = models.DateTimeField(verbose_name='Scheduled On', null=True, blank=True)
    offset = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Scheduled By',on_delete=models.CASCADE)
    status = models.CharField('Status',choices=STATUS_CHOICES, max_length=2, default=None, null=True, blank=True)
    application = models.ForeignKey(Postulate, verbose_name='Scheduled with',on_delete=models.CASCADE)
    
    def local_time(self):
        """
        Calculate and return the scheduled time adjusted by the offset.

        Returns:
            datetime: Scheduled datetime minus the offset in minutes.
        """
        # return self.scheduled_on - timedelta(minutes = self.offset + 330)
        return self.scheduled_on - timedelta(minutes = self.offset)

    def local_time_only(self):
        """
        Return the time component of the adjusted scheduled datetime.

        Returns:
            time: Time component of the local_time.
        """
        return self.local_time().time()

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        """
        Return a readable string representation of the schedule.

        Returns:
            str: Status, local scheduled time, and user who scheduled.
        """
        return self.get_status_display() + ' on ' + str(self.local_time()) + ' by ' + str(self.user)
    