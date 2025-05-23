

from __future__ import absolute_import
from django.db import models
from django.conf import settings

# Create your models here.
class socialmultishareoauth(models.Model):
    MEDIA_CHOICES=(
        ('FB','Facebook'),
        ('TW','Twitter'),
        ('LI','Linked In'),
    )
    oauth_token = models.TextField()
    oauth_secret = models.TextField()
    identifier = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    media = models.CharField(max_length=50,choices=MEDIA_CHOICES)
    class Meta:
        verbose_name = "socialmultishareoauth"
        verbose_name_plural = "socialmultishareoauths"
    def __str__(self):
        return self.media + ' - ' + self.identifier
    