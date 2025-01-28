from __future__ import absolute_import
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from vacancies.models import Question, Choice
import os.path
from activities.utils import *

