# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from candidates.models import Candidate
from ckeditor.fields import RichTextField
from common.models import Degree, Gender, Employment_Type, Country, Currency
from companies.models import Company_Industry as Industry, Company, Stage, Recruiter, ExternalReferal
from customField.models import Template, FieldValue
from datetime import date, timedelta
from django.urls import reverse
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext as _
from TRM import settings
from utils import get_file_content, get_file_text, tagcloud
from six.moves import range

Name = _('Name')


class Vacancy_Status(models.Model):
    """
    Job's status
    id - codename´s:
        1 - active
        2 - inactive
        3 - programmed
        4 - finalized
        5 - removed
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)
    public = models.BooleanField(verbose_name = _('Is Public?'), default = False)

    def __unicode__(self):
        return '%s' % self.name

    def count(self):
        return self.vacancy_set.count()

    class Meta:
        verbose_name = _('Job Status')
        verbose_name_plural = _('Job Statuses')
        ordering = ['id']

class PubDate_Search(models.Model):
    """
    It serves to search for jobs according to publication date
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    days = models.PositiveIntegerField(verbose_name=_('Days'), blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('Day for Search')
        verbose_name_plural = _('Days for search')
        ordering = ['days']

# class Vacancy_Type(models.Model):
    #     """
    #     Type of job: Simple, Media , Featured and their prices
    #     """
    #     name = models.CharField(max_length=30)
    #     order = models.PositiveSmallIntegerField()
    #     codename = models.CharField(max_length=20)
    #     price = models.PositiveIntegerField()

class Employment_Experience(models.Model):
    """
    Experience required for a job
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(blank=True, null=True, default=100)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('Employment Experience')
        verbose_name_plural = _('Employment Experiences')
        ordering = ['id']

class Salary_Type(models.Model):
    """
    Wage rate offered for each job
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(blank=True, null=True, default=100)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = _('Type of Salary')
        verbose_name_plural = _('Types of Salaries')
        ordering = ['order']

def get_ages(indistinct=True):
    ages = [(1, _('Any'))]
    for age in range(18, 66, 1):
        ages.append([str(age), str(age)])
    return ages

def get_ban_period(indistinct=True):
    b_period = []
    b_period.append([str(1),str(1) + ' month'])
    for period in range(2,12,1):
        b_period.append([str(period),str(period)+' months'])
    return b_period

class Expired(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Expired, self).get_queryset().filter(status__codename='open', expired=True)

class Scheduled(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Scheduled, self).get_queryset().filter(status__codename='open', pub_date__gt=date.today())

class Closed(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Closed, self).get_queryset().filter(status__codename='closed')

class Open(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(Open, self).get_queryset().filter(status__codename='open')

class OpentoPublic(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(OpentoPublic, self).get_queryset().filter(status__codename='open', expired=False, pub_date__lte=date.today())

def get_30_days_later():
    return date.today() + timedelta(days = 29)

class Vacancy(models.Model):
    """ Jobs """
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    
    employment = models.CharField(verbose_name=_('Job Role'), max_length=70, blank=True, null=True, default=None)
    status = models.ForeignKey(Vacancy_Status, verbose_name=_('Status'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    description = RichTextField(verbose_name=_('Description of Post'), null=True, blank=True, default=None)
    employmentType = models.ForeignKey(Employment_Type, verbose_name=_('Type of employment'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # state = models.ForeignKey(State, verbose_name=_(u'State'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # municipal = models.ForeignKey(Municipal, verbose_name=_(u'City'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    
    industry = models.ForeignKey(Industry, verbose_name=_('Industry'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    function = models.CharField(verbose_name=_('Function'), null=True, blank=True, default=None, max_length=50)
    skills = models.CharField(verbose_name=_('Skills'), null=True, blank=True, default=None, max_length=200)
    
    notice_period = models.CharField(verbose_name=_('Notice Period'), null=True, blank=True, default=None, max_length=50)
    # area = models.ForeignKey(Area, verbose_name=_(u'Area'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    
    nationality = models.ForeignKey(Country, verbose_name=_('Nationality'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name=_('State'),null=True,blank=True,default=None, max_length=50)
    city = models.CharField(verbose_name=_('City'),null=True,blank=True,default=None, max_length=50)
    
    gender = models.ForeignKey(Gender, verbose_name=_('Gender'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    minEmploymentExperience = models.ForeignKey(Employment_Experience, verbose_name=_('Minimum Experience'), null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name = 'min_experience')
    maxEmploymentExperience = models.ForeignKey(Employment_Experience, verbose_name=_('Maximum Experience'), null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name = 'max_experience')
    degree = models.ForeignKey(Degree, verbose_name=_('Degree'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    min_age = models.CharField(choices=get_ages(), null=True, blank=True, default=None, max_length=2)
    max_age = models.CharField(choices=get_ages(), null=True, blank=True, default=None, max_length=2)
    
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), null=True, blank=True, default=None,on_delete=models.SET_NULL)
    salaryType = models.ForeignKey(Salary_Type, verbose_name=_('Type of Salary'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    min_salary = models.CharField(verbose_name=_('Minimum Salary'),max_length=50, null=True, blank=True, default=None)
    max_salary = models.CharField(verbose_name=_('Maximum Salary'),max_length=50, null=True, blank=True, default=None)
    
    seen = models.IntegerField(verbose_name=_('Seen'), blank=True, null=True, default=0)
    postulate = models.BooleanField(verbose_name=_('Applications allowed?'), default=True)
    applications = models.PositiveIntegerField(verbose_name=_('Number of applications'), blank=True, null=True, default=0)
    confidential = models.BooleanField(verbose_name=_('Confidential?'), default=False)
    data_contact = models.BooleanField(verbose_name=_('Contact data?'), default=True)
    another_email = models.BooleanField(verbose_name=_('Send nominatins to another email'), default=False)
    email = models.EmailField(verbose_name='E-mail', blank=True, null=True, default=None)
    
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_('Last Modified'), auto_now=True)
    
    pub_after = models.BooleanField(verbose_name=_('Post on a future date?'), default=False)
    pub_date = models.DateField(verbose_name=_('Date of publication'), default=date.today)
    unpub_date = models.DateField(verbose_name=_('Date of unpublication'), default = get_30_days_later)
    editing_date = models.DateField(verbose_name=_('Editing Date'), null=True, blank=True)
    end_date = models.DateField(verbose_name=_('End Date'), null=True, blank=True)
    expired = models.BooleanField(verbose_name=_('Is Expired?'), default=False)
    
    questions = models.BooleanField(verbose_name=_('Allow questions?'), default=True)
    hiring_date = models.DateField(verbose_name=_('Date of Joining'), null=True, blank=True)
    vacancies_number = models.PositiveSmallIntegerField(verbose_name=_('Number of Jobs'), null=True, blank=True, default=1)
    public_cvs = models.BooleanField(verbose_name=_('Allow public CV?'), default=False)
    vacancy_reason = models.CharField(verbose_name=('Job Reason for Closing'),max_length = 100, null=True, blank=True, default=None)
    
    recruiters = models.ManyToManyField(Recruiter, verbose_name='Recruiter',default=None)
    
    ban = models.BooleanField(verbose_name='Ban',default=False)
    ban_period = models.CharField(choices=get_ban_period(), null=True, blank=True, default=None, max_length=2)
    ban_all = models.BooleanField(verbose_name =' Ban All', default=False)

    has_custom_form = models.BooleanField(verbose_name='Has Custom Form?', blank=True, default=False)
    form_template = models.ForeignKey(Template, null=True, blank=True, default=None,on_delete=models.SET_NULL)


    objects = models.Manager()
    openjobs = Open()
    publishedjobs = OpentoPublic()
    unpublishedjobs = Expired()
    scheduledjobs = Scheduled()
    closedjobs = Closed()

    def __unicode__(self):
        return '%s' % self.employment

    def non_members(self):
        employers = self.company.recruiter_set.all().filter(membership=1, user__is_active=True).exclude(id__in=[r.id for r in self.recruiters.all()])
        return employers

    def members(self):
        employers = self.company.recruiter_set.all().filter(Q(membership__gte=2, user__is_active=True)|Q(id__in=[r.id for r in self.recruiters.all()]))
        return employers

    def skills_as_list(self):
        return self.skills.split(',')

    def get_absolute_url(self):
        if self.company.subdomain.cname:
            url = self.company.subdomain.cname
        else:
            url = self.company.subdomain.slug+settings.SITE_SUFFIX
        inurl = reverse('vacancies_get_vacancy_details',kwargs={'vacancy_id':self.id})
        url = url.strip('/') + '/' + inurl.strip('/')
        return 'http://%s/' % url.strip('/')

    def get_application_url(self):
        if self.company.subdomain.cname:
            url = self.company.subdomain.cname
        else:
            url = self.company.subdomain.slug + settings.SITE_SUFFIX
        inurl = reverse('vacancies_public_apply', kwargs={'vacancy_id':self.id})
        url = url.strip('/') + '/' + inurl.strip('/')
        return 'http://%s/' % url.strip('/')

    def get_url_block(self):
        return [{
                'head':'Job Details Link',
                'value':self.get_absolute_url()
            },{
                'head':'Apply Form Link',
                'value':self.get_application_url()
            }]
            
    def finalized_count(self):
        # return self.postulated.filter(finalize=True).count() + self.public_postulated.filter(finalize=True).count()
        return self.postulated.filter(finalize=True).count()

    def application_count(self):
        # return self.postulated.count() + self.public_postulated.count()
        return self.postulated.count()

    def employment_experience(self):
        experience = ""
        if not self.minEmploymentExperience or not self.maxEmploymentExperience or (self.minEmploymentExperience.id == 2 and self.maxEmploymentExperience == 2):
            experience = 'No Experience Required'
        elif self.maxEmploymentExperience.id == self.minEmploymentExperience.id:
            experience = self.minEmploymentExperience.name
        else:
            experience = self.minEmploymentExperience.name + ' - ' + self.maxEmploymentExperience.name            
        return '%s' % experience

    def age_preference(self):
        age = ""
        if not self.min_age:
            age = "Any"
        else:
            age = self.min_age
        if not self.max_age and self.min_age:
            age = age + ' - ' + "Any"
        elif self.max_age:
            age = age + ' - ' + self.max_age
        return age

    def location(self):
        joblocation = ""
        if self.city:
            joblocation += self.city.capitalize() + ', '
        if self.state:
            joblocation += self.state.capitalize() + ', '
        if self.nationality:
            joblocation += str(self.nationality).capitalize()
        return joblocation

    @property
    def hasbeenPublished(self):
        if self.publish_history_set.all():
            return True
        return False
    
    @property
    def scheduled(self):
        if self.pub_date > date.today():
            return True
        return False

    @property
    def hasUnseen(self):
        return self.postulated.filter(seen=False).count()

    def publish(self):
        self.expired = False
        self.pub_after = False
        self.pub_date = date.today()
        if self.unpub_date < self.pub_date:
            self.unpub_date = date.today() + timedelta(days = 29)
        self.save()
        Publish_History.objects.create(vacancy = self, action = 1)

    def unpublish(self):
        self.expired = True
        self.unpub_date = date.today()
        self.save()
        Publish_History.objects.create(vacancy = self, action = 2)
    
    def available_tags(self):
        return self.vacancytags_set.all()

    def get_tag_cloud(self):
        return tagcloud(self.available_tags,'postulate_set', 1)

    def get_tag_cloud_html(self):
        tag_cloud = self.get_tag_cloud()
        if not tag_cloud:
            return ""
        html = '<div class="bg-white border-bottom border-light br-2 mt20 pt5 pl5 pr5 pb5">'
        for tag in tag_cloud:
            html += '<span class="text-info mr5 tag-item clickable" data-value="' + str(tag['tag'].id) + '" style="font-size:' + str(tag['size']) + 'em">' + str(tag['tag']) + '</span>'
        html += '</div>'
        return html

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        ordering = ('-pub_date', '-id')

ACTION_CHOICES = (
    ('1', 'Published'),
    ('2', 'Un-Published'),
)

class Publish_History(models.Model):
    """ Log of the published jobs """
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    action = models.CharField(choices=ACTION_CHOICES, null=True, blank=True, default=None, max_length=2)
    action_date = models.DateField(verbose_name=_('On'), auto_now_add=True)
    

    class Meta:
        verbose_name = "Publish_History"
        verbose_name_plural = "Publish_Histories"

    def __str__(self):
        return str(self.vacancy)
    

class Question(models.Model):
    """ Questions/Comments on the published jobs """
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    question = models.CharField(verbose_name=_('Question'), max_length=200, null=True, blank=True, default=None)
    answer = models.CharField(verbose_name=_('Answer'), max_length=200, null=True, blank=True, default=None)
    question_date = models.DateTimeField(verbose_name=_('Question date'), auto_now_add=True)
    answer_date = models.DateTimeField(verbose_name=_('Answer Date'), null=True, blank=True, default=None)

    def __unicode__(self):
        return '%s' % self.question

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ('-question_date',)

class Candidate_Fav(models.Model):
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    candidate = models.ForeignKey(Candidate, verbose_name=_('Candidate'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)

    def __unicode__(self):
        return 'Id: %s - Candidate: %s - Job: %s' % (str(self.pk), str(self.candidate.pk), str(self.vacancy.pk))

    class Meta:
        verbose_name = _('Favourite Job')
        verbose_name_plural = _('Favourite Jobs')
        ordering = ('-vacancy', '-add_date')

### Job_Files ###
def upload_files_to_vacancy_path(instance, filename):
    folder = Vacancy_Files.default_path
    tmp_folder = Vacancy_Files.tmp_folder
    if instance.vacancy:
        folder = '%s/%s' % (folder, str(instance.vacancy.pk))
    elif instance.random_number:
        folder = '%s/%s/%s' % (folder, tmp_folder, str(instance.random_number))
    return '%s/%s' % (folder, filename)

class Vacancy_Files(models.Model):
    default_path = 'vacancies'
    tmp_folder = 'tmp-files'
    file = models.FileField(upload_to=upload_files_to_vacancy_path)
    vacancy = models.ForeignKey(Vacancy, verbose_name='Job', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    random_number = models.IntegerField(verbose_name='Identificador', blank=True, null=True, default=None)
    add_date = models.DateTimeField('Fecha de alta', auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def ext(self):
        return os.path.splitext(self.file.name)[1]

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(Vacancy_Files, self).delete(*args, **kwargs)

    def __unicode__(self):
        return 'Id: %s - Job: %s - File: %s' % (str(self.pk), str(self.vacancy.pk), self.file.name)

    class Meta:
        verbose_name = _('File for Job')
        verbose_name_plural = _('Files for Job')
        ordering = ('-vacancy', '-add_date', 'random_number')
### Job_Files ###

### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###
class VacancyStage(models.Model):
    stage = models.ForeignKey(Stage, verbose_name=_('Stage Name'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(verbose_name=_('Order'), null=True, blank=True, default=None)
    locked = models.BooleanField(verbose_name=_('Locked'), default=False)
    # candidates = models.ManyToManyField(Candidate, verbose_name=_(u'Candidate'), default=None)
    recruiters = models.ManyToManyField(Recruiter, default=None)
    criteria = models.TextField(default=None, null=True, blank=True)

    def __unicode__(self):
        return self.stage.name

    def isLocked(self):
        if self.locked:
            return True
        # count0 = int(self.postulate_set.all().filter(vacancy =self.vacancy).exclude(discard=True).count()) + int(self.public_postulate_set.all().filter(vacancy = self.vacancy).exclude(discard=True).count())
        # count1 = int(Postulate.objects.filter(vacancy=self.vacancy, vacancy_stage__order__gt=self.order).count()) + int(Public_Postulate.objects.filter(vacancy=self.vacancy, vacancy_stage__order__gt=self.order).count())
        # count2 = int(self.postulate_set.all().filter(vacancy=self.vacancy,discard=True).count()) + int(self.public_postulate_set.all().filter(vacancy=self.vacancy, discard = True).count())
        # count3 = int(Postulate.objects.filter(vacancy=self.vacancy,finalize=True).count()) + int(Public_Postulate.objects.filter(vacancy=self.vacancy,finalize=True).count())
        count0 = int(self.postulate_set.all().filter(vacancy =self.vacancy).exclude(discard=True).count())
        count1 = int(Postulate.objects.filter(vacancy=self.vacancy, vacancy_stage__order__gt=self.order).count())
        count2 = int(self.postulate_set.all().filter(vacancy=self.vacancy,discard=True).count())
        count3 = int(Postulate.objects.filter(vacancy=self.vacancy,finalize=True).count())
        total_count = count0 + count1 + count2
        if total_count > 0:
            return True
        else:
            return False

    def criteria_as_list(self):
        if self.criteria:
            return [criterion for criterion in self.criteria.split(';;')]
        else:
            return None

    def non_members(self):
        employers = self.vacancy.company.recruiter_set.all().filter(user__is_active=True).exclude(id__in=[r.id for r in self.recruiters.all()])
        return employers

    def members(self):
        employers = self.vacancy.company.recruiter_set.all().filter(user__is_active=True, id__in=[r.id for r in self.recruiters.all()])
        return employers

    def active_count(self):
        # return self.postulate_set.all().filter(discard=False).count() + self.public_postulate_set.all().filter(discard=False).count()
        return self.postulate_set.all().filter(discard=False).count()

    def fellow_recruiters(self):
        return self.vacancy.company.recruiter_set.all().filter(user__is_active=True).filter(Q(id__in=[r.id for r in self.recruiters.all()])|Q(membership__gte=2))

    def get_absolute_url(self):
        if self.vacancy.company.subdomain.cname:
            url = self.vacancy.company.subdomain.cname
        else:
            url = self.vacancy.company.subdomain.slug+settings.SITE_SUFFIX
        inurl = reverse('vacancies_get_vacancy_stage_details',kwargs={'vacancy_id':self.id, 'vacancy_stage': self.order})
        url = url.strip('/') + '/' + inurl.strip('/')
        return 'http://%s/' % url.strip('/')


    class Meta:
        verbose_name=_('Job Process')
        verbose_name_plural=_('Job Processes')
        ordering = ['order']

class StageCriterion(models.Model):
    vacancy_stage = models.ForeignKey(VacancyStage,verbose_name='Job Stage', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="Criteria Name", max_length=50)

    class Meta:
        verbose_name = "Stage Criterion"
        verbose_name_plural = "Stage Criterion"

    def __unicode__(self):
        return self.name  
    
class VacancyTags(models.Model):
    name = models.CharField(verbose_name = 'Tag Name', max_length=50)
    added = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)
    vacancy = models.ForeignKey(Vacancy, null=True, default = None,on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name  
    
    class Meta:
        verbose_name = "Job Tag"
        verbose_name = "Job Tags"

class Medium(models.Model):
    """Model definition for Medium. Defines the external referral domain."""

    name = models.CharField(max_length=100)
    
    class Meta:
        """Meta definition for Medium."""
        verbose_name = 'Medium'
        verbose_name_plural = 'Mediums'

    def __unicode__(self):
        """Unicode representation of Medium."""
        return self.name

class Postulate(models.Model):
    """ Indicates whether a candidate is running a Job and if the Company has already seen or not the CV of the candidate nominated """
    default_path = 'vacancies'

    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), related_name='postulated', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    candidate = models.ForeignKey(Candidate, verbose_name=_('Candidate'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    seen = models.BooleanField(verbose_name=_('Seen'), default=False)
    finalize = models.BooleanField(verbose_name="Selected", default=False)
    discard = models.BooleanField(verbose_name=_('Discarded'), default=False)
    withdraw = models.BooleanField(verbose_name=_('Wihdrawen'), default=False)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)
    tag = models.CharField(max_length=200, verbose_name=_('Application Tag'), default=None, null=True, blank=True)
    vacancy_stage = models.ForeignKey(VacancyStage, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    recruiter = models.ForeignKey(Recruiter, null=True, blank=True, default=None,on_delete=models.SET_NULL)
    is_recruiter = models.BooleanField(verbose_name = "Added by Recruiter?", blank=True, default=False)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True, default=None)
    tags = models.ManyToManyField(VacancyTags, default=None)
    has_filled_custom_form = models.BooleanField(verbose_name = 'Filled Custom Form?', default=False, blank= True)
    custom_form_application = models.ManyToManyField(FieldValue, default=None)
    external_referer = models.ForeignKey(ExternalReferal, null = True, blank=True,default=None, on_delete=models.SET_DEFAULT)
    medium = models.ForeignKey(Medium, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)

    def __unicode__(self):
        return 'Id: %s - Job: %s - Candidate: %s - Seen: %s - Discard: %s' % (str(self.pk), str(self.vacancy.pk), str(self.candidate.pk), self.seen, self.discard)

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Aplications')
        ordering = ('-vacancy', '-add_date', '-seen')

    def last_status(self):
        if self.discard:
            if self.withdraw:
                return 'Withdrawn by Candidate'
            else:
                return 'Archived'
        elif self.finalize and self.vacancy.status.codename=='closed':
            return 'Finalized'
        else:
            return 'In Process'
    def stage_section(self):
        if self.discard or self.withdraw:
            return 2
        elif self.finalize and self.vacancy.status.codename=='closed':
            return 2
        else:
            return '0'
    def avg_score(self):
        stages = self.postulate_stage_set.all()
        g_total=0.0
        count=0
        for stage in stages:
            scores = stage.scores.all()
            total = 0.0
            if scores:
                total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
                total = total / scores.count()
                g_total = g_total + total
                count = count+1
        if count:
            g_total = g_total/count
        return g_total

    def avg_stars(self):
        avg = self.avg_score()
        avg = avg*2
        count = 5
        html =""
        if int(avg)%2==0:
            stars = int(avg/2)
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-light pl5"></i>'
                    stars=stars-1
                else:
                    html= html + '<i class="fa fa-star-o text-light pl5"></i>'
                count = count-1
        else:
            stars = int(avg/2)
            halfstar=True
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-light pl5"></i>'
                    stars = stars -1
                else:
                    if halfstar:
                        html = html + '<i class="fa fa-star-half-o text-light pl5"></i>'
                        halfstar = False
                    else:
                        html= html + '<i class="fa fa-star-o text-light pl5"></i>'
                count = count-1
        return html      

    def get_absolute_url(self):
        if self.vacancy.company.subdomain.cname:
            url = self.vacancy.company.subdomain.cname
        else:
            url = self.vacancy.company.subdomain.slug+settings.SITE_SUFFIX
        inurl = reverse('companies_curriculum_detail',kwargs={'candidate_id':self.candidate.id,'vacancy_id':self.vacancy.id})
        url = url + inurl
        return 'http://%s/' % url.strip('/')

    def file_content(self):
        return get_file_content(self.candidate.curriculum.file.path)

    def file_text(self):
        return get_file_text(self.candidate.curiculum.file.path)
    def filename(self):
        return os.path.basename(self.candidate.curriculum.file.name)

    def fileext(self):
        return os.path.splitext(self.candidate.curriculum.file.name)[1]
    def timeline(self):
        return self.comment_set.all().filter(comment_type__gte=2)
    def comments(self):
        return self.comment_set.all().filter(comment_type__lt=2)
    def processes(self):
        return self.postulate_stage_set.all()
    def full_name(self):
        return str(self.candidate)
        
    def file(self):
        return self.candidate.curriculum.file

    def email(self):
        return self.candidate.public_email

    def filecontent(self):
        return self.candidate.curriculum.filecontent

    def schedule(self, user):
        return self.schedule_set.filter(user=user, status='0')

# ### Public_Application ###
def public_path(instance, filename):
    default_path = Postulate.default_path
    folder = instance.vacancy.pk
    folder_pub = 'cvs'
    return '%s/%s/%s/%s' % (default_path, folder, folder_pub, filename)

class Comment(models.Model):
    text = models.TextField()
    comment_type = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    recruiter = models.ForeignKey(Recruiter, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    logtime = models.DateTimeField(verbose_name='TimeStamp', auto_now_add=True)
    postulate = models.ForeignKey(Postulate, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    # public_postulate = models.ForeignKey(Public_Postulate, default=None, null=True, blank=True)
    stage = models.ForeignKey(VacancyStage, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    stage_section = models.PositiveSmallIntegerField(default=0, null= True, blank = True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ('logtime', 'stage')

    def __str__(self):
        return self.text

    def stagesection(self):
        if self.stage_section == 0:
            return 'In Process'
        elif self.stage_section == 1:
            return 'Moved to Next'
        elif self.stage_section == 2:
            return 'Archived'

    def stage_string(self):
        if self.stage.order == 100:
            return str(self.stage)
        else:
            return "%s - %s" % (str(self.stage),self.stagesection())

    def get_scores(self):
        if self.postulate:
            process = self.postulate.postulate_stage_set.all().filter(vacancy_stage=self.stage)[0]
        # else:
        #     process = self.public_postulate.public_postulate_stage_set.all().filter(vacancy_stage=self.stage)[0]
        # if self.postulate:
        #     application = Postulate_Stage.objects.get(vacancy_stage = self.stage, postulate = self.postulate)
        # else:
        #     application = Public_Postulate_Stage.objects.get(vacancy_stage = self.stage, postulate = self.public_postulate)
        
            return process.scores.all().filter(recruiter=self.recruiter)
        else:
            return None

    def avg_score(self):
        scores = self.get_scores()
        total=0.0
        if scores:
            total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
            total = total / scores.count()
        return total
        # return total

    def avg_stars(self):
        avg = self.avg_score()
        avg = avg*2
        count = 5
        html =""
        if self.get_scores().count() > 1:
            color = 'info'
        else:
            color = 'light'
        if int(avg)%2==0:
            stars = int(avg/2)
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-'+color+' pl5"></i>'
                    stars = stars - 1
                else:
                    html= html + '<i class="fa fa-star-o text-'+color+' pl5"></i>'
                count = count-1
        else:
            stars = int(avg/2)
            halfstar=True
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-'+color+' pl5"></i>'
                    stars = stars -1
                else:
                    if halfstar:
                        html = html + '<i class="fa fa-star-half-o text-'+color+' pl5"></i>'
                        halfstar = False
                    else:
                        html= html + '<i class="fa fa-star-o text-'+color+' pl5"></i>'
                count = count-1
        return html      


class Postulate_Score(models.Model):
    name = models.CharField(verbose_name="Criteria Name", max_length=50)
    score = models.PositiveIntegerField(default=0)
    recruiter = models.ForeignKey(Recruiter, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    # comment = models.TextField()

    class Meta:
        verbose_name = "Applicant Stage"
        verbose_name_plural = "Applicant Stages"

    def __unicode__(self):
        return self.name  

    def get_stars(self):
        stars = self.score
        html="";
        count=5
        while count>0:
            if stars>0:
                html = html + '<i class="fa fa-star text-light pl5"></i>'
                stars = stars -1
            else:
                html= html + '<i class="fa fa-star-o text-light pl5"></i>'

            count = count-1
        return html

    def get_comment(self):
        try:
            process = self.postulate_stage_set.all()[0]
        except:
            process= None
        if not process:
            return None
        return process.postulate.comment_set.all().filter(comment_type=2, recruiter=self.recruiter)[0]

class Postulate_Stage(models.Model):
    vacancy_stage = models.ForeignKey(VacancyStage,verbose_name='Job Stage', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    postulate = models.ForeignKey(Postulate, verbose_name='Postulate Stage', default=None, null=True, blank=True,on_delete=models.SET_NULL)
    scores = models.ManyToManyField(Postulate_Score, default=None)
    
    class Meta:
        verbose_name = "Applicant Stage"
        verbose_name_plural = "Applicant Stages"

    def __unicode__(self):
        return str(self.vacancy_stage)

    # def unique_scores:
    #     return self.scores.all().value_list

    def avg_score(self):
        scores = self.scores.all()
        total=0.0
        if scores:
            total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
            total = total / scores.count()
        return total

    def avg_stars(self):
        avg = self.avg_score()
        avg = avg*2
        count = 5
        html =""
        if int(avg)%2==0:
            stars = int(avg/2)
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-info pl5"></i>'
                    stars = stars -1
                else:
                    html= html + '<i class="fa fa-star-o text-info pl5"></i>'
                count = count-1
        else:
            stars = int(avg/2)
            halfstar=True
            while count>0:
                if stars>0:
                    html = html + '<i class="fa fa-star text-info pl5"></i>'
                    stars = stars -1
                else:
                    if halfstar:
                        html = html + '<i class="fa fa-star-half-o text-info pl5"></i>'
                        halfstar = False
                    else:
                        html= html + '<i class="fa fa-star-o text-info pl5"></i>'
                count = count-1
        return html      

    def criteria_avg_scores(self):
        criteria = self.scores.all().values_list('name').distinct()
        g_total = []
        for criterion in criteria:
            scores = self.scores.all().filter(name=criterion[0])
            total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
            total = total / scores.count()
            avg = total
            avg = avg*2
            count = 5
            html =""
            if int(avg)%2==0:
                stars = int(avg/2)
                while count>0:
                    if stars>0:
                        html = html + '<i class="fa fa-star text-light pl5"></i>'
                        stars = stars - 1
                    else:
                        html= html + '<i class="fa fa-star-o text-light pl5"></i>'
                    count = count-1
            else:
                stars = int(avg/2)
                halfstar=True
                while count>0:
                    if stars>0:
                        html = html + '<i class="fa fa-star text-light pl5"></i>'
                        stars = stars -1
                    else:
                        if halfstar:
                            html = html + '<i class="fa fa-star-half-o text-light pl5"></i>'
                            halfstar = False
                        else:
                            html= html + '<i class="fa fa-star-o text-light pl5"></i>'
                    count = count-1 
            g_total = g_total + [(criterion[0],total,html),]
        return g_total

    def get_comments(self):
        comments = self.postulate.comment_set.all().filter(stage=self.vacancy_stage, comment_type=2)
        for comment in comments:
            comment.scores = self.scores.all().filter(recruiter=comment.recruiter)
        return comments
