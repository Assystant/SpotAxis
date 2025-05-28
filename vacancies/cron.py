from __future__ import absolute_import
from __future__ import print_function
from datetime import datetime, timedelta, date

from vacancies.models import Vacancy


# from .models import *


def PublishCronJob():
    """
    Publishes all Vacancy entries scheduled for publication today.

    This function filters Vacancy objects with a status codename of 'open' and a 
    publication date equal to the current date. It then calls the `publish()` method 
    on each of these vacancies and logs the operation with timestamps.

    Exceptions during execution are caught and printed to the console.
    """
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
    """
    Unpublishes all Vacancy entries scheduled to be unpublished as of yesterday.

    This function filters Vacancy objects with a status codename of 'open' and an 
    unpublication date equal to one day before the current date. It then calls the 
    `unublish()` method on each of these vacancies and logs the operation with timestamps.

    Exceptions during execution are caught and printed to the console.
    """
    print((str(datetime.now()) + ' --> UnPublish Cron start\n\n'))
    try:
        jobs = Vacancy.objects.filter(status__codename='open', unpub_date= date.today() - timedelta(days=1))
        for job in jobs:
            job.unublish()
            print((str(job) + ' --> UnPublished'))
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> UnPublish Cron completed\n\n'))