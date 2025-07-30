# -*- coding: utf-8 -*-

import hashlib
import random
import re
import urllib
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.db import models
from django.utils import timezone
from common import registration_settings as registration_settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.template import loader
from TRM.settings import logo_email, SITE_URL, PHOTO_USER_DEFAULT, NOTIFICATION_EMAILS, MEDIA_URL, SITE_SUFFIX, DEFAULT_FROM_EMAIL, ADMINS
from phonenumber_field.modelfields import PhoneNumberField
import types

Name = _('Name')


class Profile(models.Model):
    name = models.CharField(max_length=20)
    codename = models.CharField(max_length=20)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = u'Profile'
        verbose_name_plural = u'Profiles'


LOGIN_OPTIONS = (
    ('EL', 'Site'),
    ('FB', 'Facebook'),
    ('GO', 'Google'),
    ('LI', 'LinkedIn'),
    ('TW', 'Twitter')
)

from django.core.files import File
import os
class User(AbstractUser):
    """ Custom User """
    profile = models.ForeignKey(Profile, verbose_name=_('Profile'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    phone = PhoneNumberField(verbose_name=_(u'Phone'), null=True, blank=True, default=None)
    phone_ext = models.PositiveIntegerField(verbose_name=_(u'Extension'), null=True, blank=True, default=None)
    cellphone = PhoneNumberField(verbose_name=_('Celular'), null=True, blank=True, default=None)
    photo = models.ImageField(verbose_name=_('Photo'), upload_to='photos/', default=PHOTO_USER_DEFAULT, blank=True, null=True, max_length=200)
    logued_by = models.CharField(_('Loggin Method'), choices=LOGIN_OPTIONS, max_length=2, null=True, blank=True, default=None)

    USERNAME_FIELD = 'username'

    # def __getprofilename__(self):
    #     return u'%s' % self.profile.name

    def __str__(self):
        if self.first_name:
            return self.get_full_name()
        return str(self.username)

    class Meta:
        verbose_name = u'User'
        verbose_name_plural = u'Users'
        ordering = ['-date_joined']

    def get_remote_image(self,url):
        if url:
            try:
                result = urllib.urlretrieve(url)
                # raise ValueError(os.path.basename(result[0]))
                file = File(open(result[0]),'rb')
                self.photo.save(os.path.basename(result[0]),file)
                self.save()
                return True
            except:
                print('failed to retrieve from web')
                return False
# --------------- #
# Sending of Emails #
# --------------- #
def send_TRM_email(subject_template_name, email_template_name, context_email, to_user, from_email="SpotAxis <noreply@mail.spotaxis.com>", use_https=None, file= None, bcc=False):
    # Context using all emails sent
    try:
        base_context_email = {
            'site_url': SITE_URL,
            'logo_email': logo_email,
            'MEDIA_URL': MEDIA_URL,
        }
        # Ads additional content
        context_email = dict(context_email, **base_context_email)
        try:
            if context_email['href_url']:
                context_email['site_url'] = None
        except:
            pass
        subject = loader.render_to_string(subject_template_name, context_email)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        html_email = loader.render_to_string(email_template_name, context_email)
        email_template_name = ''.join(email_template_name)
        text_template_name = email_template_name.replace('.html','.txt')
        text_email = loader.render_to_string(text_template_name, context_email)
        # print(text_email)
        if not from_email:
            from_email = DEFAULT_FROM_EMAIL
        # html_email.encoding = "utf-8"
        if isinstance(to_user, str):
            to_user = [to_user]
        to_user = list(to_user)
        # try:
        if bcc:
            bcc = ["spotaxis@gmail.com"]
        else:
            bcc = []
        msg = EmailMultiAlternatives(subject, text_email, from_email, to_user , bcc = bcc)
        print(msg)
        msg.attach_alternative(html_email, "text/html" )
        # except:
        #     msg = EmailMessage(subject, html_email, from_email, to_user)
        #     msg.content_subtype = "html"
        if file:
            msg.attach_file(file)
        return msg.send()
    except Exception as e:
        print('%s (%s)' % (e, type(e)))#print '%s (%s)' % (e.message, type(e))
        return 0

def send_email_to_TRM(subject="No Subject", body_email=None, notify = False):
    try:
        if not notify:
            msg = EmailMessage(subject, body_email, "SpotAxis <noreply@mail.spotaxis.com>", NOTIFICATION_EMAILS)
        else:
            msg = EmailMessage(subject, body_email, "SpotAxis <noreply@mail.spotaxis.com>", ADMINS)
        msg.content_subtype = "html"
        msg.send()
    except:
        pass
# ------------------- #
# End sending of Emails #
# ------------------- #

# -------------------------- #
# Start AccountVerification #
# -------------------------- #
SHA1_RE = re.compile('^[a-f0-9]{40}$')


class AccountVerificationManager(models.Manager):
    def activate_user(self, activation_key):
        if SHA1_RE.search(activation_key):
            try:
                verification = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False

            if not verification.activation_key_expired():
                user = verification.user
                user.is_active = True
                user.save()

                verification.activation_key = self.model.ACTIVATED
                verification.save()

                return user

        return False

    def create_inactive_user(self, username, password, email):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        return new_user

    def send_verification_mail(self, new_user):
        account_verification = self.create_verification(new_user)
        context_email = {
            'activation_key': account_verification.activation_key,
            'expiration_days': registration_settings.ACCOUNT_VERIFICATION_DAYS,
            'account_activation': True,
        }
        subject_template_name='mails/activation_email_subject.html',
        email_template_name='mails/activation_email.html',

        send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=new_user.email, bcc=True)

    def create_verification(self, user):
        #salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        #activation_key = hashlib.sha1(salt + str(uuid.uuid4())).hexdigest()
        activation_key = hashlib.sha1((salt + str(uuid.uuid4())).encode('utf-8')).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        for verification in self.all():
            if verification.activation_key_expired():
                user = verification.user
                if not user.is_active:
                    user.delete()


class AccountVerification(models.Model):
    ACTIVATED = 'ALREADY_ACTIVATED'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True, default=None, on_delete=models.CASCADE)
    activation_key = models.CharField(_(u'Activation Key'), max_length=40, null=True, blank=True, default=None)

    objects = AccountVerificationManager()

    def activation_key_expired(self):
        expiration_date = timedelta(hours=registration_settings.ACCOUNT_VERIFICATION_DAYS)
        return (self.activation_key == self.ACTIVATED
            or (self.user.date_joined + expiration_date <= timezone.now()))
    activation_key_expired.boolean = True

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Checking Account')
        verbose_name_plural = _(u'Checking Accounts')
        ordering = ['-id']
# ----------------------- #
# Fin AccountVerification #
# ----------------------- #


# ------------------------- #
# Start Email Verification #
# ------------------------- #
def generate_token():
    return str(uuid.uuid4())


def generate_confirm_expire_date():
    return datetime.now() + timedelta(hours=registration_settings.EMAIL_VERIFICATION_DAYS)


class EmailVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=False, null=True, default=None, on_delete=models.SET_NULL)
    old_email = models.EmailField(_('Email Old'))
    new_email = models.EmailField(_('Email New'))
    token = models.CharField(_('Token'), max_length=40, default=generate_token)
    code = models.CharField(_(u'Code'), max_length=40, default=generate_token)
    is_approved = models.BooleanField(_('Approved'), default=False)
    is_expired = models.BooleanField(_('Expired'), default=False)
    expiration_date = models.DateTimeField(_(u'Date of Expiration'), default=generate_confirm_expire_date)

    def save(self, *args, **kwargs):
        if self.is_approved:
            EmailVerification.objects.filter(
                user=self.user, is_approved=False).update(is_expired=True)

            self.is_expired = True

            if self.user.email == self.old_email:
                self.user.email = self.new_email
                self.user.save()
        return super(EmailVerification, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = _(u'Verification of Email')
        verbose_name_plural = _(u'Verification of Emails')
        ordering = ['-id']
# ---------------------- #
# End Email Verification #
# ---------------------- #


# ---------------------------------- #
# Start Country - State - City #
# ---------------------------------- #
CONTINENTS = (
    ('AF', _('Africa')),
    ('NA', _('North America')),
    ('EU',  _('Europe')),
    ('AS', _('Asia')),
    ('OC',  _('Oceania')),
    ('SA', _('South America')),
    ('AN', _('Antarctica'))
)


class Country(models.Model):
    iso2_code = models.CharField('ISO alpha-2', max_length=2, unique=True, null=True, blank=True, default=None)
    name = models.CharField(Name, max_length=128, null=True, blank=True, default=None)
    continent = models.CharField(_(u'Continents'), choices=CONTINENTS, max_length=2, null=True, blank=True, default=None)
    order = models.PositiveSmallIntegerField(_(u'Order'), null=True, blank=True, default=1000)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')
        ordering = ['name']


class State(models.Model):
    country = models.ForeignKey(Country,verbose_name=_('Country'), null=True, blank=True, limit_choices_to={'pk__exact': 0}, on_delete=models.SET_NULL)
    name = models.CharField(Name, max_length=60, null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')
        ordering= ['country', 'name']


class Municipal(models.Model):
    state = models.ForeignKey(State, verbose_name=_(u'State'), null=True, blank=True, limit_choices_to={'pk__exact': 0}, on_delete=models.CASCADE)

    name = models.CharField(Name, max_length=80, null=True, blank=True, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'City')
        verbose_name_plural = _(u'Cities')
        ordering = ['state', 'name']


class Currency(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100, null=True, blank=True, default=None)
    symbol = models.CharField(verbose_name='Symbol', max_length=50, null=True, blank=True, default=None)
    symbol_native = models.CharField(verbose_name='Native Symbol', max_length=50, null=True, blank=True, default=None)
    decimal_digits = models.CharField(verbose_name='No of Decimal Digits', max_length=50, null=True, blank=True, default=None)
    rounding = models.CharField(verbose_name='Rounding', max_length=50, null=True, blank=True, default=None)
    code = models.CharField(verbose_name='Code', max_length=50, null=True, blank=True, default=None)
    name_plural = models.CharField(verbose_name='Plural Name', max_length=50, null=True, blank=True, default=None)

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name='Currency'
        verbose_name_plural='Currencies'
        ordering = ['code']
# ------------------------------- #
# Fin Country - State - Municipal #
# ------------------------------- #


class Address(models.Model):
    street = models.CharField(verbose_name=_(u'Street'), max_length=20, null=True, blank=True, default=None)
    postal_code = models.CharField(verbose_name=_('Postal Code'), max_length=13, null=True, blank=True, default=None)
    country = models.ForeignKey(Country, verbose_name=_(u'Country'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # state = models.ForeignKey(State, verbose_name=_(u'State'), null=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name=_(u'State'),max_length=20, null = True, blank=True, default=None)
    city = models.CharField(verbose_name=_(u'City'),max_length=20, null = True, blank=True, default=None)
    municipal = models.ForeignKey(Municipal, verbose_name=_(u'City'), null=True, default=None, on_delete=models.SET_NULL)
    last_modified = models.DateTimeField(verbose_name=_(u'Last Modified'), auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country.name}, {self.postal_code}"


    class Meta:
        verbose_name = _(u'Address')
        verbose_name_plural = _(u'Addresses')
        ordering = ['-last_modified']


# class Industry(models.Model):
#     name = models.CharField(verbose_name=Name, max_length=150, blank=True, null=True, default=None)

#     def __unicode__(self):
#         return u'%s' % self.name

#     class Meta:
#         verbose_name = _(u'Industry')
#         verbose_name_plural = _(u'Industries')
#         ordering = ['name']


# class Area(models.Model):
#     name = models.CharField(verbose_name=Name, max_length=150, blank=True, null=True, default=None)
#     industry = models.ForeignKey(Industry, verbose_name=_('Industry'), blank=True, null=True, default=None, on_delete=models.CASCADE)

#     def __unicode__(self):
#         return u'%s' % (self.name)

#     class Meta:
#         verbose_name = _(u'Area/Industry')
#         verbose_name_plural = _(u'Areas/Industry')
#         ordering = ['industry', 'name']


class Degree(models.Model):
    name = models.CharField(verbose_name=Name, max_length=50, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(null=True, blank=True, default=100)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'School Grade')
        verbose_name_plural = _(u'School Grades')
        ordering = ['order']


class Identification_Doc(models.Model):
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Type of Identification')
        verbose_name_plural = _(u'Type of Identification')
        ordering = ['name']


class Marital_Status(models.Model):
    name = models.CharField(verbose_name=Name, max_length=20, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Marital Status')
        verbose_name_plural = verbose_name
        ordering = ['name']


class Employment_Type(models.Model):
    name = models.CharField(verbose_name=Name, max_length=50, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)
    order = models.SmallIntegerField(blank=True, null=True, default=100)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Type of Employment')
        verbose_name_plural = _(u'Type of Employments')
        ordering = ['order']


class Gender(models.Model):
    name = models.CharField(verbose_name=Name, max_length=20, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _(u'Gender')
        verbose_name_plural = verbose_name
        ordering = ['id']


### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###


class Subdomain(models.Model):
    cname = models.CharField(verbose_name=_(u'Cname'), max_length=255, null=True, blank=True, default=None, unique=True)
    slug = models.CharField(verbose_name=_(u'Subdomain'), max_length=255, null=True, blank=True, default=True)

def __str__(self):
    if self.cname:
        return str(self.cname)
    else:
        return f"{self.slug}{SITE_SUFFIX}"
        # return u'%s.%s.%s' % (HOST,self.slug,SITE_URL)

    class Meta:
        verbose_name = _(u'Subdomain')
        verbose_name_plural = _(u'Subdomain') 

class SocialAuth(models.Model):
    MEDIA_CHOICES=(
        ('FB','Facebook'),
        ('TW','Twitter'),
        ('LI','Linked In'),
    )
    oauth_token = models.TextField()
    oauth_secret = models.TextField()
    identifier = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    social_code = models.CharField(max_length=50,choices=MEDIA_CHOICES)
    photo = models.ImageField(verbose_name=_('Photo'), upload_to='photos/', default=PHOTO_USER_DEFAULT, blank=True, null=True, max_length=200)
    social_name = models.CharField(max_length=100,null=True, blank=True, default="")
    remote_photo = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Social Authentication"
        verbose_name_plural = "Social Authentications"
    def __str__(self):
        return self.oauth_token

    def get_remote_image(self,url):
        if url:
            try:
                result = urllib.urlretrieve(url)
                # raise ValueError(os.path.basename(result[0]))
                file = File(open(result[0]),'rb')
                self.photo.save(os.path.basename(result[0]),file)
                self.save()
                return True
            except:
                print('failed to retrieve from web')
                return False
