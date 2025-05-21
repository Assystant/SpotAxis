# -*- coding: utf-8 -*-

from __future__ import absolute_import
import re
from ckeditor.fields import RichTextField
from common.models import Address, Subdomain, Country, Currency
from django.core import validators
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import ugettext as _
from hashids import Hashids
from localflavor.us.models import PhoneNumberField
from TRM import settings
from TRM.settings import LOGO_COMPANY_DEFAULT, SITE_SUFFIX
external_referer_hash = Hashids(salt='Job External Referal', min_length=5)


# Companies
class Company_Industry(models.Model):
    """
    Model representing an industry category for companies.

    Fields:
        name (CharField): The name of the industry.
    """
    name = models.CharField(verbose_name=_('Name'), max_length=150, blank=True, null=True, default=None)

    def __unicode__(self):
        """
        Returns the string representation of the Company Industry, which is its name.
        """
        return '%s' % self.name

    class Meta:
        verbose_name = _('Company Industry')
        verbose_name_plural = _('Company Industries')
        ordering = ['name']

class Company(models.Model):
    """Model representing a company with its profile details."""
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
        """
        Returns the string representation of the company, which is its tradename.
        """
        return '%s' % self.name

    def geturl(self):
        """
        Constructs the full URL of the company based on its subdomain.

        Returns:
            str: URL string like "http://subdomain.example.com"
        """
        if self.subdomain.cname:
            url = "http://"+self.subdomain.cname
        else:
            url = "http://"+self.subdomain.slug+SITE_SUFFIX
        return url.strip('/')

    def getsubdomainurl(self):
        """
        Returns the URL for the subdomain of the company.

        Returns:
            str or None: URL string or None if no subdomain.
        """
        url=None
        if self.subdomain:
            url = "http://" + self.subdomain.slug + SITE_SUFFIX
        return url.strip('/')

    def get_absolute_url(self):
        """
        Returns the absolute URL to the company's profile page.

        Returns:
            str or None: Full URL to profile page or None if no subdomain.
        """
        url = self.geturl().strip('/')
        inurl = reverse('companies_company_profile',kwargs={})
        url = url + inurl
        return '%s' % url     

    def next_subscription(self):
        """
        Placeholder method for next subscription retrieval.

        Returns:
            None
        """
        return None

    def check_service(self,service):
        """
        Checks if the company has access to a given service.

        Args:
            service (str): Codename of the service.

        Returns:
            bool: True if service exists in subscription's package, False otherwise.
        """
        return self.subscription.price_slab.package.services.filter(codename=service).exists()

    def active_recruiter_count(self):
        """
        Counts active recruiters associated with the company.

        Returns:
            int: Number of active recruiters.
        """
        return self.recruiter_set.all().filter(user__is_active=True).count()

    def get_job_template(self):
        """
        Placeholder method for obtaining the job template.
        """
        site_template = self.self_template
        
    def company_functions(self):
        """
        Returns distinct job functions offered by the company.

        Returns:
            list: List of unique function names.
        """
        jobs = self.vacancy_set.all()
        functions = jobs.values('function').distinct()
        return list(set([function['function'] for function in functions]))

    def company_locations(self):
        """
        Returns distinct cities where the company's jobs are located.

        Returns:
            list: List of unique city names.
        """
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
    """
    Custom manager for Recruiters filtering only active users.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Returns queryset filtered to active users only.

        Returns:
            QuerySet: Filtered recruiters with active users.
        """
        return super(RecruiterManager, self).get_queryset().filter(user__is_active=True)

class Managers(models.Manager):
    """
    Custom manager filtering recruiters with membership = 2 (managers) and active users.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Returns queryset filtered by membership and active user status.

        Returns:
            QuerySet: Managers queryset.
        """
        return super(Managers, self).get_queryset().filter(membership=2, user__is_active=True)
        
class Admins(models.Manager):
    """
    Custom manager filtering recruiters with membership = 3 (admins) and active users.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Returns queryset filtered by membership and active user status.

        Returns:
            QuerySet: Admins queryset.
        """
        return super(Admins, self).get_queryset().filter(membership=3, user__is_active=True)
        
class Members(models.Manager):
    """
    Custom manager filtering recruiters with membership = 1 (members) and active users.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Returns queryset filtered by membership and active user status.

        Returns:
            QuerySet: Members queryset.
        """
        return super(Members, self).get_queryset().filter(membership=1, user__is_active=True)
        
class Recruiter(models.Model):
    """
    Model representing a recruiter profile.

    Fields:
        user (OneToOneField): User linked to the recruiter.
        company (ManyToManyField): Companies the recruiter belongs to.
        membership (PositiveSmallIntegerField): Role membership (1-member, 2-manager, 3-admin).
    
    Managers:
        objects: Default manager.
        managers: Custom manager for membership=2.
        members: Custom manager for membership=1.
        admins: Custom manager for membership=3.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name = 'user', null=True, blank=True, default=None, on_delete=models.CASCADE)
    company = models.ManyToManyField(Company,verbose_name=_('Company'), default=None)
    membership = models.PositiveSmallIntegerField(default=1) # 1-member 2-manager 3-admin

    # objects = RecruiterManager()
    objects = models.Manager()
    managers = Managers()
    members = Members()
    admins = Admins()

    def is_admin(self):
        """
        Checks if recruiter has admin membership.

        Returns:
            bool: True if admin, False otherwise.
        """
        if self.membership == 3:
            return True
        else:
            return False

    def is_owner(self):
        """
        Checks if recruiter is the owner (admin and user matches company user).

        Returns:
            bool: True if owner, False otherwise.
        """
        if self.is_admin() and self.company.all()[0].user == self.user:
            return True
        else:
            return False

    def is_manager(self):
        """
        Checks if recruiter has manager or admin membership.

        Returns:
            bool: True if manager or admin, False otherwise.
        """
        if self.membership >1:
            return True
        else:
            return False

    def roles(self):
        """
        Returns the string role of the recruiter based on membership.

        Returns:
            str: Role name ('Admin', 'Manager', or 'Member').
        """
        role =""
        if self.membership == 3:
            role="Admin"
        elif self.membership == 2:
            role="Manager"
        else:
            role = "Member"
        return role

    def fellow_recruiters(self):
        """
        Returns other active recruiters from the same company excluding self.

        Returns:
            QuerySet: Fellow recruiters queryset.
        """
        return self.company.all()[0].recruiter_set.all().filter(user__is_active=True).exclude(id=self.id)

    def schedules(self):
        """
        Retrieve and group all active schedules for the user by their local date.

        Imports:
            - Schedule model from scheduler.models
            - collections module

        Returns:
            collections.OrderedDict: An ordered dictionary where keys are dates
            and values are lists of Schedule instances scheduled on those dates.
        """
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
        """
        Return a string representation of the Recruiter instance.

        Returns:
            str: String representation of the user associated with the Recruiter.
        """
        return '%s' % str(self.user)

    class Meta:
        verbose_name='Recruiter'
        verbose_name_plural='Recruiters'

class Ban(models.Model):
    """
    Represents an email ban record, optionally linked to a company.

    Attributes:
        email (EmailField): Email address subject to ban.
        duration (PositiveIntegerField): Duration of the ban.
        company (ForeignKey): Company associated with the ban.
        add_date (DateTimeField): Timestamp when the ban was added.
        ban_function (TextField): Description or reason for the ban.
    """
    email = models.EmailField(verbose_name = 'Email', null=True, blank=True, default=None)
    duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    add_date = models.DateTimeField(auto_now_add=True)
    ban_function = models.TextField(default=None)
    def __unicode__(self):
        """
        Return the email address as the string representation of the Ban instance.

        Returns:
            str: The banned email address.
        """
        return self.email

    class Meta:
        verbose_name = 'Ban'
        verbose_name_plural = 'Bans'

class RecruiterInvitation(models.Model):
    """
    Invitation record for a recruiter to join the platform.

    Attributes:
        email (EmailField): Email of the invited recruiter.
        token (CharField): Unique token for invitation validation.
        invited_by (ForeignKey): User who sent the invitation.
        membership (PositiveSmallIntegerField): Membership level assigned.
    """
    email = models.EmailField(verbose_name = 'email', null=True, blank=True, default=None)
    token = models.CharField(verbose_name='token', max_length=50, null=True, blank=True, default=None)
    invited_by  = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = 'Invited by', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    membership = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        """
        Return the invitation token as the string representation.

        Returns:
            str: Invitation token.
        """
        return str(self.token)

    class Meta:
        verbose_name='Recruiter Invitation'
        verbose_name_plural = 'Recruiter Invitations'

class Wallet(models.Model):
    """
    Represents a company's electronic wallet with available balance and currency.

    Attributes:
        company (OneToOneField): The company owning the wallet.
        currency (ForeignKey): Currency used in the wallet.
        available (DecimalField): Available balance.
        last_updated (DateTimeField): Last updated timestamp.
    """
    company = models.OneToOneField(Company, verbose_name='Company', null=True, blank=True, default=None, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    available = models.DecimalField(verbose_name=_('Available'), max_digits=7, decimal_places=2, null=True, blank=True, default=0.00)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def set_available_amount(self):
        """
        Calculate and update the available balance based on adds and redeems.

        Note:
            The attributes 'adds' and 'redeems' are expected to be defined elsewhere.
        """
        available_amount = self.adds - self.redeems
        self.available = available_amount

    def __unicode__(self):
        """
        Return a string showing the currency and available balance.

        Returns:
            str: String representation in the format "Currency AvailableAmount".
        """
        return '%s %s' % (str(self.currency),str(self.available))

    class Meta:
        verbose_name = _('Electronic Wallet')
        verbose_name_plural = _('Electronic Wallets')
        ordering = ['-available']

# Recomendations Companies #
class Recommendation_Status(models.Model):
    """
    Status of a recommendation with a name, codename, and order.

    Attributes:
        name (CharField): Status name.
        codename (CharField): Internal codename.
        order (PositiveSmallIntegerField): Ordering priority.
    """
    name = models.CharField(verbose_name=_('Status'), max_length=30, null=True, blank=True, default=None)
    codename = models.CharField(verbose_name=_('Codename'), max_length=30, null=True, blank=True, default=None)
    order = models.PositiveSmallIntegerField(verbose_name=_('Order'), null=True, blank=True, default=None)

    def __unicode__(self):
        """
        Return the name of the recommendation status.

        Returns:
            str: Status name.
        """
        return '%s' % self.name

    class Meta:
        verbose_name = _('Status of Recommendation')
        verbose_name_plural = _('Status of Recommendations')
        ordering = ('-order',)

class Recommendations(models.Model):
    """
    Represents a recommendation from one company to another with status and dates.

    Attributes:
        to_company (ForeignKey): Company receiving the recommendation.
        from_company (ForeignKey): Company sending the recommendation.
        status (ForeignKey): Current status of the recommendation.
        start_date (DateField): When the recommendation starts.
        end_date (DateField): When the recommendation ends.
        add_date (DateTimeField): Timestamp when added.
    """
    to_company = models.ForeignKey(Company, verbose_name=_('For'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    from_company = models.ForeignKey(Company, verbose_name=_('From'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    status = models.ForeignKey(Recommendation_Status, verbose_name='Status', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    start_date = models.DateField(verbose_name=_('Start Date'), null=True, blank=True, default=None)
    end_date = models.DateField(verbose_name=_('End Date'), null=True, blank=True, default=None)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)

    def __unicode__(self):
        """
        Return a string summarizing the recommendation.

        Returns:
            str: Format "FromCompany -> ToCompany / Status".
        """
        return '%s -> %s / %s' % (self.from_company.name, self.to_company.name, self.status)

    class Meta:
        verbose_name = _('Recomendation')
        verbose_name_plural = _('Recomendations')
        ordering = ('status', 'end_date', 'add_date')

class Stage(models.Model):
    """
    Represents a stage within a company (e.g., hiring or project stages).

    Attributes:
        name (CharField): Name of the stage.
        company (ForeignKey): Company this stage belongs to.
    """
    name = models.CharField(verbose_name=_('Stage Name'), max_length=50, null=True, blank=True, default=None)
    company = models.ForeignKey(Company, verbose_name=_('Company'), null=True,blank=True, default=None, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        """
        Return the stage name.

        Returns:
            str: Stage name.
        """
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
    """
    Represents an external referral source linked to a company.

    Attributes:
        company (ForeignKey): Linked company.
        name (CharField): Name of the referral.
        active (BooleanField): Whether the referral is active.
        referal_type (CharField): Type of referral, e.g., Job Board or External Referer.
    """
    company = models.ForeignKey(Company, default=None, blank=True, null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length=50, default = "")
    active = models.BooleanField(default=True, blank=True)
    referal_type = models.CharField(choices=REFERAL_TYPES, max_length=2)

    class Meta:
        verbose_name = "External Referal"
        verbose_name_plural = "External Referals"

    def __str__(self):
        """
        Return the name of the external referral.

        Returns:
            str: Referral name.
        """
        return self.name

    def refid(self):
        """
        Encode and return the referral's unique ID.

        Returns:
            str: Encoded referral ID.
        """
        return external_referer_hash.encode(self.id)
    def ref_links(self, vacancy):
        """
        Generate referral links for a given vacancy.

        Args:
            vacancy (Vacancy): The vacancy instance for which links are generated.

        Returns:
            dict: Contains a list of link objects and a boolean indicating if company exists.
        """
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
        """
        Return the referral's name as a tag.

        Returns:
            str: Referral tag name.
        """
        tag = self.name
        return tag
    
### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###
