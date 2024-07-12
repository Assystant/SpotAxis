from __future__ import unicode_literals
from datetime import timedelta
from django.db import models
from TRM import settings
from vacancies.models import Postulate
# Create your models here.


STATUS_CHOICES = (
    ('0', 'Pending'),
    ('1', 'Completed'),
)

class Schedule(models.Model):
    scheduled_on = models.DateTimeField(verbose_name='Scheduled On', null=True, blank=True)
    offset = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Scheduled By')
    status = models.CharField('Status',choices=STATUS_CHOICES, max_length=2, default=None, null=True, blank=True)
    application = models.ForeignKey(Postulate, verbose_name='Scheduled with')
    
    def local_time(self):
        # return self.scheduled_on - timedelta(minutes = self.offset + 330)
        return self.scheduled_on - timedelta(minutes = self.offset)

    def local_time_only(self):
        return self.local_time().time()

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        return self.get_status_display() + ' on ' + str(self.local_time()) + ' by ' + str(self.user)
    