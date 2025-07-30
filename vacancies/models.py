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
    """
    Represents the status of a job vacancy.

    Attributes:
        name (CharField): The display name of the job status.
        codename (CharField): A short codename identifying the status.
            Predefined codenames: as stated above.
        public (BooleanField): Indicates whether the status is publicly visible.

    Methods:
        __unicode__():
            Returns the string representation of the Vacancy_Status instance (its name).

        count():
            Returns the number of Vacancy instances associated with this status.
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)
    public = models.BooleanField(verbose_name = _('Is Public?'), default = False)

    def __str__(self):
        """
        Return the string representation of the Vacancy_Status instance.

        Returns:
            str: The name of the status.
        """
        return str(self.name)

    def count(self):
        """
        Count the number of vacancies linked to this status.

        Returns:
            int: The number of Vacancy objects associated with this status.
        """
        return self.vacancy_set.count()

    class Meta:
        verbose_name = _('Job Status')
        verbose_name_plural = _('Job Statuses')
        ordering = ['id']

class PubDate_Search(models.Model):
    """
    It serves to search for jobs according to publication date
    """
    """
    Attributes:
        name (CharField): Display name of the publication date filter.
        days (PositiveIntegerField): Number of days representing the search range.
        codename (CharField): Short code identifier for the filter.
    Methods:
        __unicode__():
            Returns the string representation of the filter instance (its name).
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    days = models.PositiveIntegerField(verbose_name=_('Days'), blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)

    def __str__(self):
        """
        Return the string representation of the PubDate_Search instance.

        Returns:
            str: The name of the publication date filter.
        """
        return str(self.name)

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
    """
    Attributes:
        name (CharField): Name of the experience level.
        codename (CharField): Short code identifier for the experience.
        order (PositiveSmallIntegerField): Ordering index for display purposes.

    Methods:
        __unicode__():
            Returns the string representation of the experience instance (its name).
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=20, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(blank=True, null=True, default=100)

    def __str__(self):
        """
        Return the string representation of the Employment_Experience instance.

        Returns:
            str: The name of the employment experience.
        """
        return str(self.name)

    class Meta:
        verbose_name = _('Employment Experience')
        verbose_name_plural = _('Employment Experiences')
        ordering = ['id']

class Salary_Type(models.Model):
    """
    Wage rate offered for each job
    """
    """
    Attributes:
        name (CharField): Name of the salary type.
        codename (CharField): Short code identifier for the salary type.
        order (PositiveSmallIntegerField): Ordering index for display purposes.

    Methods:
        __unicode__():
            Returns the string representation of the salary type instance (its name).
    """
    name = models.CharField(verbose_name=Name, max_length=30, blank=True, null=True, default=None)
    codename = models.CharField(max_length=30, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(blank=True, null=True, default=100)

    def __str__(self):
        """
        Return the string representation of the Salary_Type instance.

        Returns:
            str: The name of the salary type.
        """
        return str(self.name)

    class Meta:
        verbose_name = _('Type of Salary')
        verbose_name_plural = _('Types of Salaries')
        ordering = ['order']

def get_ages(indistinct=True):
    """
    Generate a list of age options for use in forms or filters.

    Args:
        indistinct (bool): Optional parameter, not currently used.

    Returns:
        list: A list of tuples/lists where the first element is the age value as a string
              and the second is the display string. Includes an 'Any' option as the first item.
    """
    ages = [(1, _('Any'))]
    for age in range(18, 66, 1):
        ages.append([str(age), str(age)])
    return ages

def get_ban_period(indistinct=True):
    """
    Generate a list of ban period options measured in months.

    Args:
        indistinct (bool): Optional parameter, not currently used.

    Returns:
        list: A list of lists with each containing the ban period as a string and
              a formatted string showing the period in months.
    """
    b_period = []
    b_period.append([str(1),str(1) + ' month'])
    for period in range(2,12,1):
        b_period.append([str(period),str(period)+' months'])
    return b_period

class Expired(models.Manager):
    """
    Custom manager to filter job vacancies that are marked as expired and open.

    Methods:
        get_queryset():
            Returns a queryset filtered by status codename 'open' and expired=True.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Return queryset of open vacancies that are expired.

        Returns:
            QuerySet: Filtered queryset of expired open vacancies.
        """
        return super(Expired, self).get_queryset().filter(status__codename='open', expired=True)

class Scheduled(models.Manager):
    """
    Custom manager to filter job vacancies that are scheduled for publication in the future.

    Methods:
        get_queryset():
            Returns a queryset filtered by status codename 'open' and pub_date greater than today.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Return queryset of open vacancies with a publication date in the future.

        Returns:
            QuerySet: Filtered queryset of scheduled open vacancies.
        """
        return super(Scheduled, self).get_queryset().filter(status__codename='open', pub_date__gt=date.today())

class Closed(models.Manager):
    """
    Custom manager to filter job vacancies that are closed.

    Methods:
        get_queryset():
            Returns a queryset filtered by status codename 'closed'.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Return queryset of closed vacancies.

        Returns:
            QuerySet: Filtered queryset of closed vacancies.
        """
        return super(Closed, self).get_queryset().filter(status__codename='closed')

class Open(models.Manager):
    """
    Custom manager to filter job vacancies that have a status codename 'open'.

    Attributes:
        use_for_related_fields (bool): Enables use for related fields.

    Methods:
        get_queryset():
            Returns a queryset filtered by status codename 'open'.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Return queryset of vacancies with status codename 'open'.

        Returns:
            QuerySet: Filtered queryset of open vacancies.
        """
        return super(Open, self).get_queryset().filter(status__codename='open')

class OpentoPublic(models.Manager):
    """
    Custom manager to filter job vacancies that are open, not expired, and published on or before today.

    Attributes:
        use_for_related_fields (bool): Enables use for related fields.

    Methods:
        get_queryset():
            Returns a queryset filtered by status codename 'open', not expired, and pub_date less than or equal to today.
    """
    use_for_related_fields = True
    def get_queryset(self):
        """
        Return queryset of vacancies that are open, not expired, and already published.

        Returns:
            QuerySet: Filtered queryset of public open vacancies.
        """
        return super(OpentoPublic, self).get_queryset().filter(status__codename='open', expired=False, pub_date__lte=date.today())

def get_30_days_later():
    """
    Utility function to get the date 30 days from today (29 days ahead + today).

    Returns:
        datetime.date: Date object representing 30 days later from the current date.
    """
    return date.today() + timedelta(days = 29)

class Vacancy(models.Model):
    """ Jobs """
    """
    Represents a Job Vacancy with detailed attributes such as company, user, employment details,
    status, experience requirements, salary information, publication dates, and related recruiters.

    Attributes:
        company (ForeignKey): The company offering the job.
        user (ForeignKey): The user who created the vacancy.
        employment (CharField): Job role or title.
        status (ForeignKey): Current status of the vacancy (e.g., active, closed).
        description (RichTextField): Detailed job description.
        employmentType (ForeignKey): Type of employment (e.g., full-time, part-time).
        industry (ForeignKey): Industry sector of the job.
        function (CharField): Job function or department.
        skills (CharField): Required skills for the job, comma-separated.
        notice_period (CharField): Notice period expected from applicants.
        nationality (ForeignKey): Nationality preference for applicants.
        state (CharField): State location of the job.
        city (CharField): City location of the job.
        gender (ForeignKey): Gender preference, if any.
        minEmploymentExperience (ForeignKey): Minimum experience required.
        maxEmploymentExperience (ForeignKey): Maximum experience required.
        degree (ForeignKey): Educational degree required.
        min_age (CharField): Minimum age preference.
        max_age (CharField): Maximum age preference.
        currency (ForeignKey): Currency for the salary.
        salaryType (ForeignKey): Type of salary offered.
        min_salary (CharField): Minimum salary offered.
        max_salary (CharField): Maximum salary offered.
        seen (IntegerField): Number of times the vacancy was viewed.
        postulate (BooleanField): Whether applications are allowed.
        applications (PositiveIntegerField): Number of applications received.
        confidential (BooleanField): Whether the vacancy is confidential.
        data_contact (BooleanField): Whether contact data is shown.
        another_email (BooleanField): Whether nominations are sent to another email.
        email (EmailField): Alternative email for nominations.
        add_date (DateTimeField): Date vacancy was added.
        last_modified (DateTimeField): Date vacancy was last modified.
        pub_after (BooleanField): Whether the vacancy is scheduled for future publication.
        pub_date (DateField): Date the vacancy is published.
        unpub_date (DateField): Date the vacancy is unpublished.
        editing_date (DateField): Date editing was done.
        end_date (DateField): End date of the vacancy.
        expired (BooleanField): Whether the vacancy is expired.
        questions (BooleanField): Whether questions are allowed.
        hiring_date (DateField): Expected hiring date.
        vacancies_number (PositiveSmallIntegerField): Number of job openings.
        public_cvs (BooleanField): Whether public CVs are allowed.
        vacancy_reason (CharField): Reason for closing the vacancy.
        recruiters (ManyToManyField): Recruiters associated with the vacancy.
        ban (BooleanField): Whether the vacancy is banned.
        ban_period (CharField): Duration of the ban.
        ban_all (BooleanField): Whether all bans apply.
        has_custom_form (BooleanField): Whether a custom form is used.
        form_template (ForeignKey): Template for the custom form.

    Managers:
        objects: Default manager.
        openjobs: Manager for open vacancies.
        publishedjobs: Manager for published vacancies.
        unpublishedjobs: Manager for expired vacancies.
        scheduledjobs: Manager for scheduled vacancies.
        closedjobs: Manager for closed vacancies.

    Methods:
        __unicode__(): Returns the job employment title as string representation.
        non_members(): Returns recruiters from the company not associated with this vacancy.
        members(): Returns recruiters associated with this vacancy or with membership.
        skills_as_list(): Returns the skills as a list split by commas.
        get_absolute_url(): Returns the full URL to the vacancy details page.
        get_application_url(): Returns the full URL to the vacancy application page.
        get_url_block(): Returns a list of URLs related to the vacancy (details and apply links).
        finalized_count(): Returns count of finalized postulations.
        application_count(): Returns total number of postulations.
        employment_experience(): Returns formatted string of experience requirements.
        age_preference(): Returns formatted string of age preference.
        location(): Returns formatted location string of the vacancy.
        hasbeenPublished (property): Indicates if vacancy has any publication history.
        scheduled (property): Indicates if the vacancy is scheduled for future publication.
        hasUnseen (property): Returns count of unseen postulations.
        publish(): Publishes the vacancy, setting dates and history.
        unpublish(): Unpublishes the vacancy, setting expired flag and history.
        available_tags(): Returns tags associated with the vacancy.
        get_tag_cloud(): Returns tag cloud data for postulations.
        get_tag_cloud_html(): Returns HTML formatted tag cloud.

    Meta:
        verbose_name: Human-readable singular name "Job".
        verbose_name_plural: Human-readable plural name "Jobs".
        ordering: Default ordering by publication date descending, then ID descending.
    """
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

    def __str__(self):
        """
        Returns the string representation of the Vacancy instance.

        Returns:
            str: The employment/job title of the vacancy.
        """
        return str(self.employment)
        #return '%s' % self.employment

    def non_members(self):
        """
        Retrieves recruiters related to the vacancy's company who are active, 
        have membership level 1, and are NOT currently associated with this vacancy.

        Returns:
            QuerySet: Recruiters who are non-members for this vacancy.
        """
        employers = self.company.recruiter_set.all().filter(membership=1, user__is_active=True).exclude(id__in=[r.id for r in self.recruiters.all()])
        return employers

    def members(self):
        """
        Retrieves recruiters related to the vacancy's company who either 
        have membership level 2 or higher, or are associated with this vacancy.

        Returns:
            QuerySet: Recruiters who are members or linked to this vacancy.
        """
        employers = self.company.recruiter_set.all().filter(Q(membership__gte=2, user__is_active=True)|Q(id__in=[r.id for r in self.recruiters.all()]))
        return employers

    def skills_as_list(self):
        """
        Splits the skills string into a list of individual skills.

        Returns:
            list[str]: List of skills from the skills field.
        """
        return self.skills.split(',')

    def get_absolute_url(self):
        """
        Constructs and returns the absolute URL for the vacancy details page.

        Returns:
            str: Fully qualified URL string for the vacancy details.
        """
        if self.company.subdomain.cname:
            url = self.company.subdomain.cname
        else:
            url = self.company.subdomain.slug+settings.SITE_SUFFIX
        inurl = reverse('vacancies_get_vacancy_details',kwargs={'vacancy_id':self.id})
        url = url.strip('/') + '/' + inurl.strip('/')
        return 'http://%s/' % url.strip('/')

    def get_application_url(self):
        """
        Constructs and returns the absolute URL for the vacancy application page.

        Returns:
            str: Fully qualified URL string for the vacancy application form.
        """
        if self.company.subdomain.cname:
            url = self.company.subdomain.cname
        else:
            url = self.company.subdomain.slug + settings.SITE_SUFFIX
        inurl = reverse('vacancies_public_apply', kwargs={'vacancy_id':self.id})
        url = url.strip('/') + '/' + inurl.strip('/')
        return 'http://%s/' % url.strip('/')

    def get_url_block(self):
        """
        Provides a list of dictionaries containing the URLs for job details and application form.

        Returns:
            list[dict]: List containing dictionaries with 'head' and 'value' keys for URLs.
        """
        return [{
                'head':'Job Details Link',
                'value':self.get_absolute_url()
            },{
                'head':'Apply Form Link',
                'value':self.get_application_url()
            }]
            
    def finalized_count(self):
        """
        Counts the number of finalized postulations for this vacancy.

        Returns:
            int: Count of finalized postulations.
        """
        # return self.postulated.filter(finalize=True).count() + self.public_postulated.filter(finalize=True).count()
        return self.postulated.filter(finalize=True).count()

    def application_count(self):
        """
        Counts the total number of postulations (applications) for this vacancy.

        Returns:
            int: Total number of postulations.
        """
        # return self.postulated.count() + self.public_postulated.count()
        return self.postulated.count()

    def employment_experience(self):
        """
        Returns a formatted string describing the experience required for the vacancy.

        Returns:
            str: Experience requirement description.
        """
        experience = ""
        if not self.minEmploymentExperience or not self.maxEmploymentExperience or (self.minEmploymentExperience.id == 2 and self.maxEmploymentExperience == 2):
            experience = 'No Experience Required'
        elif self.maxEmploymentExperience.id == self.minEmploymentExperience.id:
            experience = self.minEmploymentExperience.name
        else:
            experience = self.minEmploymentExperience.name + ' - ' + self.maxEmploymentExperience.name            
        return '%s' % experience

    def age_preference(self):
        """
        Returns a formatted string showing the age preference range for the vacancy.

        Returns:
            str: Age preference range (e.g., "Any - Any", "25 - 40").
        """
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
        """
        Returns a formatted string describing the job location including city, state, and nationality.

        Returns:
            str: Job location formatted as "City, State, Country".
        """
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
        """
        Checks if the vacancy has any publication history.

        Returns:
            bool: True if publication history exists, False otherwise.
        """
        if self.publish_history_set.all():
            return True
        return False
    
    @property
    def scheduled(self):
        """
        Checks if the vacancy publication date is set in the future.

        Returns:
            bool: True if vacancy is scheduled for future publication, False otherwise.
        """
        if self.pub_date > date.today():
            return True
        return False

    @property
    def hasUnseen(self):
        """
        Counts the number of unseen applications (postulations) for this vacancy.

        Returns:
            int: Number of unseen postulations.
        """
        return self.postulated.filter(seen=False).count()

    def publish(self):
        """
        Publishes the vacancy by setting appropriate flags and dates,
        then saves the instance and logs the publish action in history.
        """
        self.expired = False
        self.pub_after = False
        self.pub_date = date.today()
        if self.unpub_date < self.pub_date:
            self.unpub_date = date.today() + timedelta(days = 29)
        self.save()
        Publish_History.objects.create(vacancy = self, action = 1)

    def unpublish(self):
        """
        Unpublishes the vacancy by marking it expired, updating the unpublication date,
        saving the instance, and logging the unpublish action in history.
        """
        self.expired = True
        self.unpub_date = date.today()
        self.save()
        Publish_History.objects.create(vacancy = self, action = 2)
    
    def available_tags(self):
        """
        Retrieves all tags associated with this vacancy.

        Returns:
            QuerySet: All vacancy tags related to this vacancy.
        """
        return self.vacancytags_set.all()

    def get_tag_cloud(self):
        """
        Generates a tag cloud data structure for tags related to postulations.

        Returns:
            list[dict]: List of tags with associated sizes for visualization.
        """
        return tagcloud(self.available_tags,'postulate_set', 1)

    def get_tag_cloud_html(self):
        """
        Generates an HTML snippet representing the tag cloud.

        Returns:
            str: HTML string of tags styled with font sizes for a tag cloud.
        """
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
    """
    Attributes:
        vacancy (ForeignKey): Reference to the Vacancy instance associated with this log.
        action (CharField): The type of action performed (e.g., publish, unpublish).
        action_date (DateField): Date when the action was performed (auto-set on creation).
   """
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    action = models.CharField(choices=ACTION_CHOICES, null=True, blank=True, default=None, max_length=2)
    action_date = models.DateField(verbose_name=_('On'), auto_now_add=True)
    

    class Meta:
        verbose_name = "Publish_History"
        verbose_name_plural = "Publish_Histories"

    def __str__(self):
        """
        String representation of the Publish_History instance.

        Returns:
            str: The string representation of the related vacancy.
        """
        return str(self.vacancy)
    

class Question(models.Model):
    """ Questions/Comments on the published jobs """
    """
    Attributes:
        vacancy (ForeignKey): The related Vacancy instance for the question.
        user (ForeignKey): The user who asked the question.
        question (CharField): The question text.
        answer (CharField): The answer text.
        question_date (DateTimeField): Timestamp when the question was created.
        answer_date (DateTimeField): Timestamp when the answer was provided.
    """

    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True, default=None, on_delete=models.SET_NULL)
    question = models.CharField(verbose_name=_('Question'), max_length=200, null=True, blank=True, default=None)
    answer = models.CharField(verbose_name=_('Answer'), max_length=200, null=True, blank=True, default=None)
    question_date = models.DateTimeField(verbose_name=_('Question date'), auto_now_add=True)
    answer_date = models.DateTimeField(verbose_name=_('Answer Date'), null=True, blank=True, default=None)

    def __str__(self):
        """
        String representation of the Question instance.

        Returns:
            str: The question text.
        """
        return str(self.question)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ('-question_date',)

class Candidate_Fav(models.Model):

    """
    Represents a candidate's favorite jobs.

    Attributes:
        vacancy (ForeignKey): The favorite Vacancy instance.
        candidate (ForeignKey): The Candidate who marked the vacancy as favorite.
        add_date (DateTimeField): Timestamp when the favorite was added.
    """

    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    candidate = models.ForeignKey(Candidate, verbose_name=_('Candidate'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    add_date = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)

    def __str__(self):
        """
        String representation of the Candidate_Fav instance.

        Returns:
            str: A formatted string with ID, candidate ID, and job ID.
        """
        return f'Id: {self.pk} - Candidate: {self.candidate.pk} - Job: {self.vacancy.pk}'

    class Meta:
        verbose_name = _('Favourite Job')
        verbose_name_plural = _('Favourite Jobs')
        ordering = ('-vacancy', '-add_date')

### Job_Files ###
def upload_files_to_vacancy_path(instance, filename):
    """
    Determines the upload path for files related to vacancies.

    The file path is structured based on whether the file is linked to a Vacancy instance
    or is associated with a temporary random number.

    Args:
        instance (Vacancy_Files): The Vacancy_Files instance uploading the file.
        filename (str): The original filename being uploaded.

    Returns:
        str: The full relative file path where the file should be stored.
    """
    folder = Vacancy_Files.default_path
    tmp_folder = Vacancy_Files.tmp_folder
    if instance.vacancy:
        folder = '%s/%s' % (folder, str(instance.vacancy.pk))
    elif instance.random_number:
        folder = '%s/%s/%s' % (folder, tmp_folder, str(instance.random_number))
    return '%s/%s' % (folder, filename)

class Vacancy_Files(models.Model):
    """
    Stores files related to vacancies, including temporary uploads and finalized files.

    Attributes:
        file (FileField): The uploaded file.
        vacancy (ForeignKey): The related Vacancy instance.
        random_number (IntegerField): Temporary identifier for files not yet associated with a vacancy.
        add_date (DateTimeField): Timestamp when the file was uploaded.
    """
    default_path = 'vacancies'
    tmp_folder = 'tmp-files'
    file = models.FileField(upload_to=upload_files_to_vacancy_path)
    vacancy = models.ForeignKey(Vacancy, verbose_name='Job', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    random_number = models.IntegerField(verbose_name='Identificador', blank=True, null=True, default=None)
    add_date = models.DateTimeField('Fecha de alta', auto_now_add=True)

    def filename(self):
        """
        Gets the base filename of the uploaded file.

        Returns:
            str: Filename without directory path.
        """
        return os.path.basename(self.file.name)

    def ext(self):
        """
        Gets the file extension of the uploaded file.

        Returns:
            str: The file extension including the dot (e.g., '.pdf').
        """
        return os.path.splitext(self.file.name)[1]

    def delete(self, *args, **kwargs):
        """
        Deletes the file from storage and removes the model instance.
        """
        self.file.delete(False)
        super(Vacancy_Files, self).delete(*args, **kwargs)

    def __str__(self):
        """
        String representation of the Vacancy_Files instance.

        Returns:
            str: A formatted string with ID, job ID, and file name.
        """
        return f'Id: {self.pk} - Job: {self.vacancy.pk} - File: {self.file.name}'

    class Meta:
        verbose_name = _('File for Job')
        verbose_name_plural = _('Files for Job')
        ordering = ('-vacancy', '-add_date', 'random_number')
### Job_Files ###

### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###
class VacancyStage(models.Model):
    """
    Represents a stage in a job vacancy's recruitment process.

    Attributes:
        stage (ForeignKey): Reference to the Stage model, representing the name of the stage.
        vacancy (ForeignKey): The associated Vacancy object.
        order (PositiveIntegerField): The order of this stage in the recruitment pipeline.
        locked (BooleanField): Flag indicating if the stage is locked.
        recruiters (ManyToManyField): Recruiters assigned to this vacancy stage.
        criteria (TextField): Optional criteria for the stage, stored as a delimited string.

    Methods:
        __unicode__():
            Returns the name of the stage as its string representation.

        isLocked():
            Determines if the stage is locked either explicitly or by related postulant counts.
            Returns True if locked, False otherwise.

        criteria_as_list():
            Parses the criteria string into a list of criteria.
            Returns None if no criteria exist.

        non_members():
            Returns active recruiters of the vacancy's company who are NOT assigned to this stage.

        members():
            Returns active recruiters of the vacancy's company who ARE assigned to this stage.

        active_count():
            Returns the count of active (non-discarded) postulants in this stage.

        fellow_recruiters():
            Returns active recruiters who are members of this stage or have a high membership level.

        get_absolute_url():
            Returns the absolute URL to the details page for this vacancy stage.
    """
    stage = models.ForeignKey(Stage, verbose_name=_('Stage Name'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    vacancy = models.ForeignKey(Vacancy, verbose_name=_('Job'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(verbose_name=_('Order'), null=True, blank=True, default=None)
    locked = models.BooleanField(verbose_name=_('Locked'), default=False)
    # candidates = models.ManyToManyField(Candidate, verbose_name=_(u'Candidate'), default=None)
    recruiters = models.ManyToManyField(Recruiter, default=None)
    criteria = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        """
        Returns the string representation of the VacancyStage.

        Returns:
            str: The name of the linked Stage.
        """
        return str(self.stage.name)

    def isLocked(self):
        """
        Checks if the VacancyStage is locked either by the locked flag or postulant activity.

        Returns:
            bool: True if locked, False otherwise.
        """

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
        """
        Converts the criteria text into a list of criteria strings.

        Returns:
            list[str] or None: List of criteria split by ';;' or None if criteria is empty.
        """
        if self.criteria:
            return [criterion for criterion in self.criteria.split(';;')]
        else:
            return None

    def non_members(self):
        """
        Fetches active recruiters of the vacancy's company not assigned to this stage.

        Returns:
            QuerySet: Recruiters not assigned to this VacancyStage.
        """

        employers = self.vacancy.company.recruiter_set.all().filter(user__is_active=True).exclude(id__in=[r.id for r in self.recruiters.all()])
        return employers

    def members(self):
        """
        Fetches active recruiters of the vacancy's company assigned to this stage.

        Returns:
            QuerySet: Recruiters assigned to this VacancyStage.
        """
        employers = self.vacancy.company.recruiter_set.all().filter(user__is_active=True, id__in=[r.id for r in self.recruiters.all()])
        return employers

    def active_count(self):
        """
        Counts active postulants (non-discarded) associated with this stage.

        Returns:
            int: Number of active postulants.
        """
        # return self.postulate_set.all().filter(discard=False).count() + self.public_postulate_set.all().filter(discard=False).count()
        return self.postulate_set.all().filter(discard=False).count()

    def fellow_recruiters(self):
        """
        Returns recruiters who are either assigned to this stage or have membership level >= 2.

        Returns:
            QuerySet: Relevant recruiters.
        """

        return self.vacancy.company.recruiter_set.all().filter(user__is_active=True).filter(Q(id__in=[r.id for r in self.recruiters.all()])|Q(membership__gte=2))

    def get_absolute_url(self):
        """
        Constructs and returns the absolute URL to the vacancy stage details.

        Returns:
            str: Absolute URL string.
        """
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
    """
    Represents a criterion associated with a VacancyStage.

    Attributes:
        vacancy_stage (ForeignKey): The VacancyStage this criterion belongs to.
        name (CharField): Name of the criterion.

    Methods:
        __unicode__():
            Returns the criterion's name as string representation.
    """
    vacancy_stage = models.ForeignKey(VacancyStage,verbose_name='Job Stage', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="Criteria Name", max_length=50)

    class Meta:
        verbose_name = "Stage Criterion"
        verbose_name_plural = "Stage Criterion"

    def __str__(self):
        return str(self.name)

class VacancyTags(models.Model):
    """
    Represents tags assigned to a Vacancy for categorization.

    Attributes:
        name (CharField): The tag name.
        added (DateTimeField): Date/time when the tag was added.
        vacancy (ForeignKey): The associated Vacancy.

    Methods:
        __unicode__():
            Returns the tag name as string representation.
    """
    name = models.CharField(verbose_name = 'Tag Name', max_length=50)
    added = models.DateTimeField(verbose_name=_('Add Date'), auto_now_add=True)
    vacancy = models.ForeignKey(Vacancy, null=True, default = None,on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)  
    
    class Meta:
        verbose_name = "Job Tag"
        verbose_name = "Job Tags"

class Medium(models.Model):
    """Model definition for Medium. Defines the external referral domain."""
    """
    Attributes:
        name (CharField): Name of the medium/referral source.

    Methods:
        __str__():
            Returns the name of the medium as string representation.
    """

    name = models.CharField(max_length=100)
    
    class Meta:
        """Meta definition for Medium."""
        verbose_name = 'Medium'
        verbose_name_plural = 'Mediums'

    def __str__(self):
        """Unicode representation of Medium."""
        return str(self.name)

class Postulate(models.Model):
    """ Indicates whether a candidate is running a Job and if the Company has already seen or not the CV of the candidate nominated """
    """
    Represents an application of a candidate to a job vacancy, tracking the candidate's progress and the company's interaction with their CV.

    Attributes:
        vacancy (ForeignKey): The job vacancy the candidate applied to.
        candidate (ForeignKey): The candidate applying.
        seen (BooleanField): Whether the CV has been viewed by the company.
        finalize (BooleanField): Whether the candidate has been selected.
        discard (BooleanField): Whether the application has been discarded.
        withdraw (BooleanField): Whether the candidate has withdrawn the application.
        add_date (DateTimeField): Date when the application was added.
        tag (CharField): An optional tag for the application.
        vacancy_stage (ForeignKey): Current stage of the application in the recruitment process.
        recruiter (ForeignKey): Recruiter responsible for this application.
        is_recruiter (BooleanField): Indicates if added by a recruiter.
        description (TextField): Optional description or notes.
        tags (ManyToManyField): Tags related to the vacancy.
        has_filled_custom_form (BooleanField): Whether the candidate filled a custom form.
        custom_form_application (ManyToManyField): Custom form field values.
        external_referer (ForeignKey): External referral source.
        medium (ForeignKey): External referral medium.

    Methods:
        __str__():
            Returns a string representation of the application.

        last_status():
            Returns the current status of the application as a human-readable string.

        stage_section():
            Returns a code representing the stage section based on discard, withdraw, or finalize status.

        avg_score():
            Calculates the average score across all stages associated with the application.

        avg_stars():
            Returns an HTML string showing the average score as star icons.

        get_absolute_url():
            Returns the absolute URL to view details of this candidate's application.

        file_content():
            Returns the content of the candidate's curriculum file.

        file_text():
            Returns the text extracted from the candidate's curriculum file.

        filename():
            Returns the filename of the candidate's curriculum file.

        fileext():
            Returns the file extension of the candidate's curriculum file.

        timeline():
            Returns comments of type timeline associated with this application.

        comments():
            Returns regular comments associated with this application.

        processes():
            Returns all recruitment process stages related to this application.

        full_name():
            Returns the candidate's full name.

        file():
            Returns the candidate's curriculum file.

        email():
            Returns the candidate's public email.

        filecontent():
            Returns the file content of the candidate's curriculum.

        schedule(user):
            Returns the schedule entries associated with this application filtered by a specific user and open status.
    """
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

    def __str__(self):
        return f'Id: {self.pk} - Job: {self.vacancy.pk} - Candidate: {self.candidate.pk} - Seen: {self.seen} - Discard: {self.discard}'

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Aplications')
        ordering = ('-vacancy', '-add_date', '-seen')

    def last_status(self):
        """
        Determines the human-readable status of the application.

        Returns:
            str: Status string such as 'Withdrawn by Candidate', 'Archived', 'Finalized', or 'In Process'.
        """
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
        """
        Determines the stage section code based on the application status.

        Returns:
            int or str: Returns 2 if the application is discarded, withdrawn, or finalized with the vacancy closed; otherwise returns '0'.
        """
        if self.discard or self.withdraw:
            return 2
        elif self.finalize and self.vacancy.status.codename=='closed':
            return 2
        else:
            return '0'
    def avg_score(self):
        """
        Calculates the average score across all stages linked to this application.

        Returns:
            float: The average score or 0 if no scores exist.
        """
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
        """
        Generates HTML representation of the average score as star icons.

        Returns:
            str: HTML string containing star icons (full, half, empty).
        """
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
        """
        Constructs the URL for viewing detailed information about this candidate's application.

        Returns:
            str: Fully qualified URL string.
        """
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
    """
    Generates a file upload path for storing candidate CV files related to a vacancy.

    Args:
        instance (Postulate): The Postulate instance the file is associated with.
        filename (str): The original filename of the uploaded file.

    Returns:
        str: A path string formatted as 'default_path/vacancy_id/cvs/filename'.
    """

    default_path = Postulate.default_path
    folder = instance.vacancy.pk
    folder_pub = 'cvs'
    return '%s/%s/%s/%s' % (default_path, folder, folder_pub, filename)

class Comment(models.Model):
    """
    Represents a comment made by a recruiter on a candidate's application stage.

    Methods:
        __unicode__(): Returns a string representation of the comment.
        stagesection(): Returns the section of the stage based on comment_type.
        stage_string(): Returns a descriptive string combining stage and section.
        get_scores(): Retrieves all Postulate_Score objects linked to this comment.
        avg_score(): Calculates the average score of all scores related to this comment.
        avg_stars(): Returns an HTML string displaying the average score as stars.
    """
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
        """
        Determines the stage section type based on the comment_type field.

        Returns:
            str: A string label representing the stage section.
        """
        if self.stage_section == 0:
            return 'In Process'
        elif self.stage_section == 1:
            return 'Moved to Next'
        elif self.stage_section == 2:
            return 'Archived'

    def stage_string(self):
        """
        Provides a descriptive string combining the stage's name/order and the section label.

        Returns:
            str: A string representing the stage and its section.
        """
        if self.stage.order == 100:
            return str(self.stage)
        else:
            return "%s - %s" % (str(self.stage),self.stagesection())

    def get_scores(self):
        """
        Retrieves all Postulate_Score instances associated with this comment's postulate stage and recruiter.

        Returns:
            QuerySet: A queryset of related Postulate_Score objects.
        """
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
        """
        Calculates the average score from all related Postulate_Score objects.

        Returns:
            float: The average score, or 0 if no scores exist.
        """
        scores = self.get_scores()
        total=0.0
        if scores:
            total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
            total = total / scores.count()
        return total
        # return total

    def avg_stars(self):
        """
        Generates an HTML snippet to visually represent the average score using star icons.

        Returns:
            str: An HTML string with full, half, and empty star icons.
        """
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
    """
    Represents a score given by a recruiter to a postulate on a specific criterion during a stage.

    Methods:
        __unicode__(): Returns a string representation of the score.
        get_stars(): Returns an HTML string of stars representing the score.
        get_comment(): Retrieves the comment related to this score, if any.
    """
    name = models.CharField(verbose_name="Criteria Name", max_length=50)
    score = models.PositiveIntegerField(default=0)
    recruiter = models.ForeignKey(Recruiter, default=None, null=True, blank=True,on_delete=models.SET_NULL)
    # comment = models.TextField()

    class Meta:
        verbose_name = "Applicant Stage"
        verbose_name_plural = "Applicant Stages"

    def __str__(self):
        """Returns a string describing the score, criterion, and recruiter."""
        return self.name  

    def get_stars(self):
        """
        Creates an HTML representation of the score using stars.

        Returns:
            str: An HTML string with star icons reflecting the score.
        """
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
        """
        Fetches the comment made by the recruiter on the postulate stage related to this score.

        Returns:
            Comment or None: The related Comment object if found, else None.
        """
        try:
            process = self.postulate_stage_set.all()[0]
        except:
            process= None
        if not process:
            return None
        return process.postulate.comment_set.all().filter(comment_type=2, recruiter=self.recruiter)[0]

class Postulate_Stage(models.Model):


    """
    Associates a candidate's application (Postulate) with a specific vacancy stage and holds related scores.

    Methods:
        __unicode__(): Returns a string representation of the postulate stage.
        avg_score(): Calculates the average score across all criteria for this stage.
        avg_stars(): Returns an HTML string visualizing the average score as stars.
        criteria_avg_scores(): Calculates average scores per criterion with star representations.
        get_comments(): Retrieves comments associated with this postulate stage, optionally filtering by type.
    """
    vacancy_stage = models.ForeignKey(VacancyStage,verbose_name='Job Stage', null=True, blank=True, default=None,on_delete=models.SET_NULL)
    postulate = models.ForeignKey(Postulate, verbose_name='Postulate Stage', default=None, null=True, blank=True,on_delete=models.SET_NULL)
    scores = models.ManyToManyField(Postulate_Score, default=None)
    
    class Meta:
        verbose_name = "Applicant Stage"
        verbose_name_plural = "Applicant Stages"

    def __str__(self):
        """Returns a string describing the postulate and vacancy stage."""
        return str(self.vacancy_stage)

    # def unique_scores:
    #     return self.scores.all().value_list

    def avg_score(self):
        """
        Computes the average score from all associated Postulate_Score objects.

        Returns:
            float: Average score or 0 if no scores exist.
        """
        scores = self.scores.all()
        total=0.0
        if scores:
            total = scores.aggregate(Sum('score'))['score__sum'] * 1.0
            total = total / scores.count()
        return total

    def avg_stars(self):
        """
        Produces an HTML representation of the average score with star icons.

        Returns:
            str: HTML string with stars.
        """
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
        """
        Calculates average scores for each criterion related to this postulate stage.

        Returns:
            list of tuples: Each tuple contains (criterion name, average score, HTML stars).
        """
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
        """
        Retrieves comments related to this postulate stage, optionally filtered by comment type.

        Args:
            comment_type (int or None): The comment_type to filter by.

        Returns:
            list: Comments enriched with their filtered scores.
        """
        comments = self.postulate.comment_set.all().filter(stage=self.vacancy_stage, comment_type=2)
        for comment in comments:
            comment.scores = self.scores.all().filter(recruiter=comment.recruiter)
        return comments
