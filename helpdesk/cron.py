
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

"""
cron.py - Scheduled tasks for automated email processing in the TRM system.

Contains functions to be run as cron jobs, such as fetching and processing
incoming emails for ticket creation and updates.

Imports models and utilities from related apps, as well as Django management
commands and utilities for time/date operations.
"""
def EmailTicketCronJob():
    """
    Executes the 'get_email' Django management command to process incoming emails.

    Intended to be called as a cron job to fetch new emails and create or
    update tickets automatically.

    Logs start and completion times to the console, and catches exceptions to
    prevent cron job failures.

    Modules used:
        - datetime: for logging current time
        - django.core.management.call_command: to invoke management commands
    """
    print((str(datetime.now()) + ' --> Email Ticket Cron start'))
    try:
        call_command('get_email')
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> Email Ticket Cron completed'))