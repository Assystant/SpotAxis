from datetime import datetime, timedelta, date
# from .models import *
from django.db.models import Q
from common.models import send_TRM_email
from companies.models import Recruiter
from activities.utils import post_org_notification
from TRM.settings import ROOT_DOMAIN
from payments.models import Subscription, Transactions, PriceSlab
from django.core.urlresolvers import reverse
from django.core.management import call_command

def PublishCronJob():
    print(str(datetime.now()) + ' --> Publish Cron start\n\n')
    try:
    	jobs = Vacancy.objects.filter(status__codename = 'open', pub_date = date.today())
    	for job in jobs:
            job.publish()
    		print(str(job) + ' --> Published')
    except Exception as e:
        print(e)
    print(str(datetime.now()) + ' --> Publish Cron completed\n\n')

def UnPublishCronJob():
    print(str(datetime.now()) + ' --> UnPublish Cron start\n\n')
    try:
    	jobs = Vacancy.objects.filter(status__codename='open', unpub_date= date.today() - timedelta(days=1))
    	for job in jobs:
            job.unublish()
    		print(str(job) + ' --> UnPublished')
    except Exception as e:
        print(e)
    print(str(datetime.now()) + ' --> UnPublish Cron completed\n\n')