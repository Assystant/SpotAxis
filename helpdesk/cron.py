
from __future__ import absolute_import
from __future__ import print_function
from datetime import datetime, timedelta
# from .models import *
from django.db.models import Q
from common.models import send_TRM_email
from companies.models import Recruiter
from activities.utils import post_org_notification
from TRM.settings import ROOT_DOMAIN
from payments.models import Subscription, Transactions, PriceSlab
from django.urls import reverse
from django.core.management import call_command
def EmailTicketCronJob():
    print((str(datetime.now()) + ' --> Email Ticket Cron start'))
    try:
        call_command('get_email')
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> Email Ticket Cron completed'))