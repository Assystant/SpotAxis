from __future__ import absolute_import
from __future__ import print_function
from datetime import datetime, timedelta, date

from vacancies.models import Vacancy


# from .models import *


def PublishCronJob():
    print((str(datetime.now()) + ' --> Publish Cron start\n\n'))
    try:
        jobs = Vacancy.objects.filter(status__codename = 'open', pub_date = date.today())
        for job in jobs:
            job.publish()
            print((str(job) + ' --> Published'))
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> Publish Cron completed\n\n'))

def UnPublishCronJob():
    print((str(datetime.now()) + ' --> UnPublish Cron start\n\n'))
    try:
        jobs = Vacancy.objects.filter(status__codename='open', unpub_date= date.today() - timedelta(days=1))
        for job in jobs:
            job.unublish()
            print((str(job) + ' --> UnPublished'))
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> UnPublish Cron completed\n\n'))