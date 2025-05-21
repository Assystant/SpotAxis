# -*- coding: utf-8 -*-

from __future__ import absolute_import
import re
from ckeditor.fields import RichTextField
from common.models import Address, Subdomain, Country, Currency
from django.core import validators
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext as _
from hashids import Hashids
from localflavor.us.models import PhoneNumberField
from TRM import settings
from TRM.settings import LOGO_COMPANY_DEFAULT, SITE_SUFFIX
external_referer_hash = Hashids(salt='Job External Referal', min_length=5)


# Companies
class Company_Industry(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=150, blank=True, null=True, default=None)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('Company Industry')
        verbose_name_plural = _('Company Industries')
        ordering = ['name']

class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='User', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    subdomain = models.OneToOneField(Subdomain,verbose_name=_('Subdomain'),null=True, blank=True, default=None, on_delete = models.SET_NULL)
    name = models.CharField(verbose_name=_('Tradename'), max_length=200, null=True, blank=True, default=None)
    social_name = models.CharField(verbose_name=_('Busness Name'), max_length=200, null=True, blank=True, default=None)
    # rfc = MXRFCField(verbose_name=_(u'RFC'), blank=True, null=True, default=None)
    industry = models.ForeignKey(Company_Industry, verbose_name='Industry', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # function = models.CharField(verbose_name=_(u'Function'), max_length=100, null=True, blank=True, default=None)
    no_of_employees = models.IntegerField(verbose_name=_('No of Employees'), null=True, blank=True, default=None)
    # area = models.ForeignKey(Company_Area, verbose_name=_(u'Area'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # address = models.OneToOneField(Address, verbose_name=_(u'Address'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    nationality = models.ForeignKey(Country, verbose_name=_('Nationality'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name=_('State'),null=True,blank=True,default=None, max_length=50)
    city = models.CharField(verbose_name=_('City'),null=True,blank=True,default=None, max_length=50)
    
    description = RichTextField(verbose_name=_('Short Description'), blank=True, null=True, default=None)
    phone = PhoneNumberField(verbose_name=_('Phone'), null=True, blank=True, default=None)
    url = models.URLField(verbose_name=_('Website'), blank=True, null=True, default=None)
    facebook = models.URLField(verbose_name=_('Facebook'), blank=True, null=True, default=None)
    twitter = models.CharField(verbose_name=_('Twitter'), max_length=16, blank=True, null=True, default=None,
                               validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'))])
    company_email = models.EmailField(verbose_name=_('E-mail'), null=True, blank=True, default=None)
    # contact_phone = PhoneNumberField(verbose_name=_(u'Phone'), null=True, blank=True, default=None)
    # contact_phone_ext = models.PositiveIntegerField(verbose_name='Ext', null=True, blank=True, default=None)
    logo = models.ImageField(upload_to='companies/logos/', default=LOGO_COMPANY_DEFAULT,
                             blank=True, null=True, max_length=200)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_('Last Modified'), auto_now=True)
    ban_list = models.TextField(default=None, null=True, blank=True)

    site_template = models.PositiveIntegerField(default=1, blank=True)
    above_jobs = models.TextField(default="", null=True, blank=True)
    below_jobs = models.TextField(default="", null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name

    def geturl(self):
        if self.subdomain.cname:
            url = "http://"+self.subdomain.cname
        else:
            url = "http://"+self.subdomain.slug+SITE_SUFFIX
        return url.strip('/')

    def getsubdomainurl(self):
        url=None
        if self.subdomain:
            url = "http://" + self.subdomain.slug + SITE_SUFFIX
        return url.strip('/')

    def get_absolute_url(self):
        url = self.geturl().strip('/')
        inurl = reverse('companies_company_profile',kwargs={})
        url = url + inurl
        return '%s' % url     

    def next_subscription(self):
        return None

    def check_service(self,service):
        return self.subscription.price_slab.package.services.filter(codename=service).exists()

    def active_recruiter_count(self):
        return self.recruiter_set.all().filter(user__is_active=True).count()

    def get_job_template(self):
        site_template = self.self_template
        
    def company_functions(self):
        jobs = self.vacancy_set.all()
        functions = jobs.values('function').distinct()
        return list(set([function['function'] for function in functions]))

    def company_locations(self):
        jobs = self.vacancy_set.all()
        cities = jobs.values('city').distinct()
        return list(set([city['city'] for city in cities]))

    # def get_publishedjobs_in_template_design(self):
    #     from vacancies.models import Vacancy
    #     from django.shortcuts import render
    #     template = self.site_template
    #     template = 'careers/base/t-' + str(template) + '/jobs.html'
    #     vacancies = Vacancy.published_jobs.filter(company = self)
    #     return render()
        

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ('name',)

class RecruiterManager(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(RecruiterManager, self).get_queryset().filter(user__is_active=True)

class Managers(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Managers, self).get_queryset().filter(membership=2, user__is_active=True)
        
class Admins(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Admins, self).get_queryset().filter(membership=3, user__is_active=True)
        
class Members(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Members, self).get_queryset().filter(membership=1, user__is_active=True)
        
class Recruiter(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name = 'user', null=True, blank=True, default=None, on_delete=models.CASCADE)
    company = models.ManyToManyField(Company,verbose_name=_('Company'), default=None)
    membership = models.PositiveSmallIntegerField(default=1) # 1-member 2-manager 3-admin

    # objects = RecruiterManager()
    objects = models.Manager()
    managers = Managers()
    members = Members()
    admins = Admins()

    def is_admin(self):
        if self.membership == 3:
            return True
        else:
            return False

    def is_owner(self):
        if self.is_admin() and self.company.all()[0].user == self.user:
            return True
        else:
            return False

    def is_manager(self):
        if self.membership >1:
            return True
        else:
            return False

    def roles(self):
        role =""
        if self.membership == 3:
            role="Admin"
        elif self.membership == 2:
            role="Manager"
        else:
            role = "Member"
        return role

    def fellow_recruiters(self):
        return self.company.all()[0].recruiter_set.all().filter(user__is_active=True).exclude(id=self.id)

    def schedules(self):
        from scheduler.models import Schedule
        import collections
        all_schedules = Schedule.objects.filter(status=0,user = self.user).order_by('scheduled_on')
        queryset = {}
        for schedule in all_schedules:
            try:
                queryset[schedule.local_time().date()].append(schedule)
            except:
                queryset[schedule.local_time().date()] = [schedule]
        return collections.OrderedDict(sorted(queryset.items()))


    def __unicode__(self):
        return '%s' % str(self.user)

    class Meta:
        verbose_name='Recruiter'
        verbose_name_plural='Recruiters'

class Ban(models.Model):
    email = models.EmailField(verbose_name = 'Email', null=True, blank=True, default=None)
    duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    add_date = models.DateTimeField(auto_now_add=True)
    ban_function = models.TextField(default=None)
    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = 'Ban'
        verbose_name_plural = 'Bans'

class RecruiterInvitation(models.Model):
    email = models.EmailField(verbose_name = 'email', null=True, blank=True, default=None)
    token = models.CharField(verbose_name='token', max_length=50, null=True, blank=True, default=None)
    invited_by  = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = 'Invited by', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    membership = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return str(self.token)

    class Meta:
        verbose_name='Recruiter Invitation'
        verbose_name_plural = 'Recruiter Invitations'

class Wallet(models.Model):
    company = models.OneToOneField(Company, verbose_name='Company', null=True, blank=True, default=None, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    available = models.DecimalField(verbose_name=_('Available'), max_digits=7, decimal_places=2, null=True, blank=True, default=0.00)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def set_available_amount(self):
        available_amount = self.adds - self.redeems
        self.available = available_amount

    def __unicode__(self):
        return '%s %s' % (str(self.currency),str(self.available))

    class Meta:
        verbose_name = _('Electronic Wallet')
        verbose_name_plural = _('Electronic Wallets')
        ordering = ['-available']

# Recomendations Companies #
class Recommendation_Status(models.Model):
    name = models.CharField(verbose_name=_('Status'), max_length=30, null=True, blank=True, default=None)
    codename = models.CharField(verbose_name=_('Codename'), max_length=30, null=True, blank=True, default=None)
    order = models.PositiveSmallIntegerField(verbose_name=_('Order'), null=True, blank=True, default=None)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('Status of Recommendation')
        verbose_name_plural = _('Status of Recommendations')
        ordering = ('-order',)

class Recommendations(models.Model):
    to_company = models.ForeignKey(Company, verbose_name=_('For'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    from_company = models.ForeignKey(Company, verbose_name=_('From'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    status = models.ForeignKey(Recommendation_Status, verbose_name='Status', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    start_date = models.DateField(verbose_name=_('Start Date'), null=True, blank=True, default=None)
    end_date = models.DateField(verbose_name=_('End Date'), null=True, blank=True, default=None)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)

    def __unicode__(self):
        return '%s -> %s / %s' % (self.from_company.name, self.to_company.name, self.status)

    class Meta:
        verbose_name = _('Recomendation')
        verbose_name_plural = _('Recomendations')
        ordering = ('status', 'end_date', 'add_date')

class Stage(models.Model):
    name = models.CharField(verbose_name=_('Stage Name'), max_length=50, null=True, blank=True, default=None)
    company = models.ForeignKey(Company, verbose_name=_('Company'), null=True,blank=True, default=None, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Stage')
        verbose_name = _('Stages')
        ordering = ['name']

REFERAL_TYPES = (
    ('JB', 'Job Board'),
    ('ER', 'External Referer'),
)

class ExternalReferal(models.Model):
    company = models.ForeignKey(Company, default=None, blank=True, null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length=50, default = "")
    active = models.BooleanField(default=True, blank=True)
    referal_type = models.CharField(choices=REFERAL_TYPES, max_length=2)

    class Meta:
        verbose_name = "External Referal"
        verbose_name_plural = "External Referals"

    def __str__(self):
        return self.name

    def refid(self):
        return external_referer_hash.encode(self.id)
    def ref_links(self, vacancy):
        referal_id = self.refid()
        return {'objects':[{
                        'head':'Job Details Link',
                        'value':vacancy.get_absolute_url() + 'eref-' + referal_id + '/',
                    },{
                        'head':'Apply Form Link',
                        'value':vacancy.get_application_url() + 'eref-' + referal_id + '/',
                    }],
                'hasCompany': True if self.company else False}
    def tag_name(self):
        tag = self.name
        return tag
    
### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###
