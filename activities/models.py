
from __future__ import absolute_import
from django.conf import settings
from django.db import models
from vacancies.models import *
# Create your models here.

class MessageChunk(models.Model):
    subject = models.CharField(max_length=200, null=True, blank=True)
    subject_action = models.CharField(max_length=200, null=True, blank=True)
    action_url = models.URLField(null=True, blank=True, default=None)
    order = models.PositiveSmallIntegerField(default = 0, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message Chunk"
        verbose_name_plural = "Message Chunks"
        ordering = ['-last_updated','order']

    def __str__(self):
        return str(self.subject) + str(self.subject_action)

class Activity(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,on_delete=models.SET_NULL)
    action = models.CharField(max_length=200, null=True, blank=True)
    target = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='target',on_delete=models.SET_NULL)
    target_action = models.CharField(max_length=200, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    subject_action = models.CharField(max_length=200, null=True, blank=True)
    action_url = models.URLField(null=True, blank=True, default=None)
    message = models.TextField(null=True, blank=True)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="subscribers")
    activity_type = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    postulate = models.ForeignKey(Postulate,null=True,default=None, blank=True,on_delete=models.SET_NULL)
    # public_postulate = models.ForeignKey(Public_Postulate,null=True,default=None, blank=True,on_delete=models.SET_NULL))
    comments = models.ManyToManyField(Comment)
    message_chunks = models.ManyToManyField(MessageChunk)
    spotters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='Spotters')

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ['-last_updated']

    def __str__(self):
        if self.message:
            return str(self.message)
        else:
            return ''

    def get_absolute_url(self):
        if self.action_url:
            return self.action_url
        else:
            return self.actor.recruiter.company.all()[0].geturl() + "/activities/" + str(self.id) + "/"

    """
    A model representing notifications sent to users.
    
    Notifications are used to alert users about various events, activities, and updates
    within the system. They can be marked as seen/unseen and contain various types of
    messages and actions.
    
    
    Attributes:
        user (User): The user receiving the notification.
        timestamp (datetime): When the notification was created.
        last_updated (datetime): When the notification was last modified.
        action (str): The type of action that triggered the notification. Optional.
        target_action (str): Action associated with the target. Optional.
        subject (str): The subject of the notification. Optional.
        subject_action (str): Action associated with the subject. Optional.
        seen (bool): Whether the notification has been seen by the user. Defaults to False.
        action_url (str): URL associated with the notification action. Optional.
        message (str): The complete notification message. Optional.
        actor (User): The user who triggered the notification. Optional.
        target (User): The user who is the target of the notification. Optional.
        actor_count (int): Count of actors involved. Defaults to 0.
        message_chunks (ManyToMany[MessageChunk]): Message chunks used in this notification.
        
    """

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    #template = models.ForeignKey(NotificationTemplate, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=200, null=True, blank=True)
    target_action = models.CharField(max_length=200, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    subject_action = models.CharField(max_length=200, null=True, blank=True)
    seen = models.BooleanField(default=False)

    action_url = models.URLField(default=None, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='actor', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    target = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='notification_target', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    actor_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    message_chunks = models.ManyToManyField(MessageChunk)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['seen','-last_updated']

    def __str__(self):
        return str(self.actor) + ' ' + str(self.message)
    
