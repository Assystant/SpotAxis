
from __future__ import absolute_import
from __future__ import print_function
from datetime import datetime, timedelta
# from .models import *
from django.db.models import Q
from common.models import send_TRM_email
from companies.models import Recruiter
from activities.utils import post_org_notification
from TRM.settings import ROOT_DOMAIN, protocol
from payments.models import Subscription, Transactions, PriceSlab
from django.urls import reverse
"""
Modules Used:
    - `datetime`: For time comparisons with subscription expiry.
    - `django.db.models.Q`: Used for advanced filtering (not directly used here).
    - `send_TRM_email`: Sends transactional email to recruiters.
    - `Recruiter`: To fetch company admins.
    - `post_org_notification`: Sends in-app notifications.
    - `reverse`: To resolve named URL patterns.
    - `Subscription`, `Transactions`, `PriceSlab`: Subscription and billing models.
"""
def SubscriptionCronJob():
    """
    Executes a scheduled cron job to manage subscription lifecycles.

    This function performs several tasks to ensure that subscriptions are 
    appropriately renewed, downgraded, or expired based on their current status 
    and billing information. It sends notifications and emails to company admins 
    depending on whether:
      - the subscription has expired
      - it's about to expire in 7 days
      - it's expiring today
    and handles auto-renewal logic.

    """
    print((str(datetime.now()) + ' --> Subscription Cron start'))
    try:
        subscriptions = Subscription.objects.all()
        expired_subscriptions = [subscription for subscription in subscriptions if subscription.expiry and subscription.expired()]
        for subscription in expired_subscriptions:

            admins = Recruiter.admins.filter(company = subscription.company)
            admin_emails = [recruiter.user.email for recruiter in admins]
            if subscription.last_week or subscription.last_day:
                subscription.last_week = False
                subscription.last_day = False
                subscription.save()
            if subscription.auto_renew:
                if subscription.bill_amount() < subscription.company.wallet.available:
                    transaction = Transactions.objects.create(user = subscription.company.user, company = subscription.company, type = 'P', reason = 'Plan Auto Renewal', amount = subscription.bill_amount(), balance = subscription.company.wallet.available - subscription.bill_amount())
                    print(transaction)
                    transaction.save()
                    wallet = subscription.company.wallet
                    wallet.available = wallet.available - subscription.bill_amount()
                    wallet.save()
                    print(wallet)
                    #email plan auto renewed
                    print('pre if email')
                    context_email = {
                        'subject': 'Auto Renewal Successful',
                        'message': 'Your plan has been successfuly renewed. Your available credit balance is '+ str(wallet),
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    print('line20')
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)
                    post_org_notification(user = [admin.user for admin in admins], action = "'Your plan has been successfuly renewed. Your available credit balance is "+ str(wallet), url = reverse('companies_billing'))
                else:
                    #email insufficient credits and degrade notification
                    context_email = {
                        'subject': 'Action Required: Plan Expired',
                        'message': 'Due to insufficient credits your auto renewal has failed. Kindly add credits to continue the current plan.',
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    sent = send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)
                    post_org_notification(user = [admin.user for admin in admins], action = "Due to insufficient credits your auto renewal has failed. Kindly add credits to continue the current plan.", url = reverse('companies_billing'))
                    subscription.expiry = None
                    subscription.price_slab = PriceSlab.objects.first()
                    subscription.added_users = 0
                    subscription.last_week = False
                    subscription.last_day = False
                    subscription.save()
            else:
                # email degrade notification
                context_email = {
                    'subject': 'Action Required: Plan Expired',
                    'message': 'Your current plan has expired. Kindly add credits to continue the current plan.',
                    'href_url': subscription.company.geturl() + '/billing/'
                }
                subject_template_name = 'mails/billing_reminder_subject.html'
                email_template_name = 'mails/billing_reminder.html'
                send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)

                post_org_notification(user = [admin.user for admin in admins], action = "Your current plan has expired. Kindly add credits to continue the current plan.", url = reverse('companies_billing'))
                #plan degrade
                subscription.expiry = None
                subscription.price_slab = PriceSlab.objects.first()
                subscription.added_users = 0
                subscription.last_week = False
                subscription.last_day = False
                subscription.save()
        about_to_expire_subscriptions = [subscription for subscription in subscriptions if subscription.expiry and subscription.ends_in() > timedelta(days = 1) and subscription.ends_in() < timedelta(days = 7)]
        for subscription in about_to_expire_subscriptions:
            admins = Recruiter.admins.all().filter(company = subscription.company)
            admin_emails = [recruiter.user.email for recruiter in admins]
            if not subscription.last_week:
                if not subscription.auto_renew:
                    # notify to update status to continue current plan
                    context_email = {
                        'subject': 'Action Required: Billing Reminder',
                        'message': 'Your current plan expires in a week. Kindly set "Auto Renew" and have sufficient credits to continue using the current plan.',
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)

                    post_org_notification(user = [admin.user for admin in admins], action = 'Your current plan expires in a week. Kindly set "Auto Renew" and have sufficient credits to continue using the current plan.', url = reverse('companies_billing'))

                elif subscription.company.wallet.available < subscription.bill_amount():
                    # notify to add more credits
                    context_email = {
                        'subject': 'Action Required: Billing Reminder',
                        'message': 'Your current plan expires in a week. You have insufficient credits to renew. Please top up now.',
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)
                    post_org_notification(user = [admin.user for admin in admins], action = "Your current plan expires in a week. You have insufficient credits to renew. Please top up now.", url = reverse('companies_billing'))
                subscription.last_week = True
                subscription.save()
        subscriptions_expiring_today = [subscription for subscription in subscriptions if subscription.expiry and not subscription.expired() and subscription.ends_in() < timedelta(days = 1)]
        for subscription in subscriptions_expiring_today:
            admins = Recruiter.admins.all().filter(company = subscription.company)
            admin_emails = [recruiter.user.email for recruiter in admins]
            if not subscription.last_day:
                if not subscription.auto_renew:
                    # notify to update status to continue current plan
                    context_email = {
                        'subject': 'Action Required: Billing Reminder',
                        'message': 'Your current plan expires today. Kindly set "Auto Renew" and have sufficient credits to continue using the current plan.',
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)
                    post_org_notification(user = [admin.user for admin in admins], action = 'Your current plan expires today. Kindly set "Auto Renew" and have sufficient credits to continue using the current plan.', url = reverse('companies_billing'))
                elif subscription.company.wallet.available < subscription.bill_amount():
                    # notify to add more credits
                    context_email = {
                        'subject': 'Action Required: Billing Reminder',
                        'message': 'Your current plan expires today. You have insufficient credits to renew. Please top up now.',
                        'href_url': subscription.company.geturl() + '/billing/'
                    }
                    subject_template_name = 'mails/billing_reminder_subject.html'
                    email_template_name = 'mails/billing_reminder.html'
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=admin_emails)
                    post_org_notification(user = [admin.user for admin in admins], action = "Your current plan expires today. You have insufficient credits to renew. Please top up now.", url = reverse('companies_billing'))
                subscription.last_week = False
                subscription.last_day = True
                subscription.save()
        active_subscriptions_with_flags = [subscription for subscription in subscriptions.filter(last_day = True) if not subscription.expiry or subscription.ends_in() > timedelta(days = 7)]+[subscription for subscription in subscriptions.filter(last_week = True) if not subscription.expiry or subscription.ends_in() > timedelta(days = 7)]
        for subscription in active_subscriptions_with_flags:
            subscription.last_week = False
            subscription.last_day = False
            subscription.save()
    except Exception as e:
        print(e)
    print((str(datetime.now()) + ' --> Subscription Cron completed'))