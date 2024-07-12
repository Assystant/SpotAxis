# -*- coding: utf-8 -*-

import os
import subprocess
from datetime import date, timedelta, datetime
from django.db import models
from django.db.models import Q
from common.models import Gender, Marital_Status, Country, State, Municipal, Degree, Address
from django.utils.translation import ugettext as _
from dateutil.relativedelta import relativedelta
from companies.models import *
from django.conf import settings
from ckeditor.fields import RichTextField
from utils import get_file_content, get_file_text
MEDIA_ROOT = settings.MEDIA_ROOT

candidate = _(u'Candidate')


def get_initial_date():
    """ Get date for 1/1 21 years ago """
    year = (date.today() - relativedelta(years=21)).year
    initial_date = date(year, 1, 1)
    return initial_date

PROFILE_SOURCE = (
    ('SA', 'Site'),
    ('PU', 'Public'),
    ('FB', 'Facebook'),
    ('GO', 'Google'),
    ('LI', 'LinkedIn'),
    ('TW', 'Twitter')
)

class Candidate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True, default=None, on_delete=models.CASCADE)
    public_email = models.EmailField(default=None, null=True, blank=True)
    public_photo = models.ImageField(verbose_name=_('Photo'), upload_to='photos/', default=None, blank=True, null=True, max_length=200)
    first_name = models.CharField(verbose_name=_(u'Name'), max_length=30, null=True, blank=True, default="")
    last_name = models.CharField(verbose_name=_(u'Surname'), max_length=30, null=True, blank=True, default="")
    birthday = models.DateField(verbose_name=_('Birthday'), null=True, blank=True, default=None)
    gender = models.ForeignKey(Gender, verbose_name=_(u'Gender'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    maritalStatus = models.ForeignKey(Marital_Status, verbose_name=_(u'Marital Status'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # address = models.ForeignKey(Address, verbose_name=_(u'Address'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    nationality = models.ForeignKey(Country, verbose_name=_('Nationality'), related_name='+', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # state = models.ForeignKey(State, verbose_name=_('Current State'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # municipal = models.ForeignKey(Municipal, verbose_name=_(u'City'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name=_('State'),null=True,blank=True,default=None, max_length=50)
    city = models.CharField(verbose_name=_('City'),null=True,blank=True,default=None, max_length=50)
    phone = PhoneNumberField(null=True, blank=True, default=None)
    cellphone = PhoneNumberField(null=True, blank=True, default=None)
    travel = models.BooleanField(verbose_name=_(u'Availability to Travel'), default=False)
    residence = models.BooleanField(verbose_name=_(u'Availability to change residence'), default=False)
    min_salary = models.PositiveIntegerField(verbose_name=_(u'Minimum Salary'), null=True, blank=True, default=None)
    max_salary = models.PositiveIntegerField(verbose_name=_(u'Desired Salary'), null=True, blank=True, default=None)
    linkedin = models.URLField(verbose_name=_(u'Linkedin'), blank=True, null=True, default=None)
    facebook = models.URLField(verbose_name=_(u'Facebook'), blank=True, null=True, default=None)
    twitter = models.CharField(verbose_name=_(u'Twitter'), max_length=16, blank=True, null=True, validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'))])
    google = models.URLField(verbose_name=_(u'Google +'), blank=True, null=True, default=None)
    objective = models.TextField(verbose_name=_(u'Profesional Objetive'), max_length=300, null=True, blank=True, default=None)
    interests = RichTextField(verbose_name=_(u'Interests'), null=True, blank=True, default=None)
    hobbies = RichTextField(verbose_name=_(u'Hobbies'), null=True, blank=True, default=None)
    extra_curriculars = RichTextField(verbose_name=_(u'Extra Curriculars'), null=True, blank=True, default=None)
    others = RichTextField(verbose_name=_(u'Others'), null=True, blank=True, default=None)
    skills = models.TextField(verbose_name=_(u'Skills'), null=True, blank=True, default=None)
    add_date = models.DateTimeField(verbose_name=_(u'Add Date'), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_(u'Last Modified'), auto_now=True)
    parent_profile = models.ForeignKey("self", related_name="conflicted_profiles", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    profile_source = models.CharField(_('Profile Source'), choices=PROFILE_SOURCE, max_length=2, null=True, blank=True, default=None)

    def get_fullname(self):
        if not self.first_name and not self.last_name:
            return self.user
        return u'%s %s' % (self.first_name,self.last_name)

    def full_name(self):
        name=""
        if self.first_name.strip():
            name = name + self.first_name.strip()
        if self.last_name.strip():
            name = name + " " + self.last_name.strip()
        return name.strip()

    def get_address(self):
        address=""
        if self.city:
            address = self.city + ', '
        if self.state:
            address += self.state + ','
        if self.nationality:
            address += str(self.nationality)
        address = address.replace(',,',',')
        address = address.strip(',')
        return u'%s' % (address)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def role(self):
        expertises = self.expertise_set.all()
        current_role=""
        for expertise in expertises:
            if expertise.present:
                current_role = current_role + expertise.employment + ", "
        current_role = current_role.strip(', ')
        return current_role

    def total_experience(self):
        expertises = self.expertise_set.all()
        total = timedelta(0)
        for expertise in expertises:
            if expertise.start_date:
                if not expertise.present:
                    total = total + (expertise.end_date - expertise.start_date)
                else:
                    total = total + (date.today() - expertise.start_date)
        if total == timedelta(0):
            return 'Fresher'
        else:
            return str(round(total.days/365.245,2)) + ' years'

    def education(self):
        academics = self.academic_set.all()
        academic_history = ""
        for academic in academics:
            if academic.course_name:
                academic_history = academic_history + academic.course_name + ', '
        academic_history = academic_history.strip(', ')
        return academic_history

    def get_profile_form(self):
        from candidates.forms import CandidateForm
        return CandidateForm(instance = self)
      
    def get_photo_form(self):
        from common.forms import UserPhotoForm
        return UserPhotoForm(instance = self.user)
        
    def get_contact_form(self):
        from candidates.forms import CandidateContactForm
        return CandidateContactForm(instance = self)
        
    def get_objective_form(self):
        from candidates.forms import ObjectiveForm
        return ObjectiveForm(instance = self)
        
    def get_interest_form(self):
        from candidates.forms import InterestsForm
        return InterestsForm(instance = self)
        
    def get_hobby_form(self):
        from candidates.forms import HobbiesForm
        return HobbiesForm(instance = self)
        
    def get_extracurricular_form(self):
        from candidates.forms import ExtraCurricularsForm
        return ExtraCurricularsForm(instance = self)
        
    def get_other_form(self):
        from candidates.forms import OthersForm
        return OthersForm(instance = self)
        
    def get_expertise_form(self):
        from candidates.forms import ExpertiseForm
        return ExpertiseForm()

    def get_academic_form(self):
        from candidates.forms import AcademicForm
        return AcademicForm()

    def get_language_form(self):
        from candidates.forms import CvLanguageForm
        return CvLanguageForm()

    def get_training_form(self):
        from candidates.forms import TrainingForm
        return TrainingForm()

    def get_certificate_form(self):
        from candidates.forms import CertificateForm
        return CertificateForm()

    def get_project_form(self):
        from candidates.forms import ProjectForm
        return ProjectForm()

    def all_academic_with_conflicts(self):
        from candidates.models import Academic
        profiles = self.conflicted_profiles.all()
        return Academic.objects.filter(Q(candidate__in=profiles) | Q(candidate=self))

    def all_expertise_with_conflicts(self):
        from candidates.models import Expertise
        profiles = self.conflicted_profiles.all()
        return Expertise.objects.filter(Q(candidate__in=profiles) | Q(candidate=self))

    def find_conflicts(self):
        conflicts = {}
        from resume_parser.conflict_management_system import get_conflicts
        conflicted_profiles = self.conflicted_profiles.all()
        for profile in conflicted_profiles:
            # return get_conflicts(self, profile)
            profile_conflicts = get_conflicts(self, profile)
            for key in profile_conflicts.keys():
                # if conflicts.has_key(key):
                #     conflicts[key].append(profile_conflicts[key])
                # else:
                #     conflicts[key] = profile_conflicts[key]
                if key == 'education' or key == 'experience':
                    if not conflicts.has_key(key):
                        conflicts[key] = {}
                    for conflict in profile_conflicts[key]:
                        conflicts[key][conflict['id']] = conflict
                else:
                    if conflicts.has_key(key):
                        conflicts[key] = conflicts[key] + profile_conflicts[key]
                    else:
                        conflicts[key] = profile_conflicts[key]
        return conflicts            

    class Meta:
        verbose_name = _(u'Candidate')
        verbose_name_plural = _(u'Candidates')
        ordering = ['-id']

###################################
## Start of Section Curriculums ##
###################################

MONTHS = (
    ('1', _('January')),
    ('2', _('February')),
    ('3', _('March')),
    ('4', _('April')),
    ('5', _('May')),
    ('6', _('June')),
    ('7', _('July')),
    ('8', _('August')),
    ('9', _('September')),
    ('10', _('October')),
    ('11', _('November')),
    ('12', _('December')),
)


def get_last_50_years():
    """ Gets a list of the last 50 years """
    years = []
    year = (date.today() - relativedelta(years=50)).year
    now = date.today().year
    for y in range(now, year, -1):
        years.append([str(y), str(y)])
    return years


## Professional Experience ##

class Expertise(models.Model):
    """ Professional Experience of a candidate, Relationship: Expertise-Curriculum """
    candidate = models.ForeignKey(Candidate, verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    company = models.CharField(verbose_name=_(u'Company'), max_length=30, null=True, blank=True, default=None)
    industry = models.ForeignKey(Company_Industry, verbose_name='Industry', null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # area = models.ForeignKey(Company_Area, verbose_name=_(u'Area'), null=True, blank=True, default=None, related_name='+', on_delete=models.SET_NULL)
    # address = models.ForeignKey(Address, verbose_name=_(u'Address'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, verbose_name=_(u'Country'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name= _(u'State'), null=True, blank=True, default=None, max_length=50)
    city = models.CharField(verbose_name= _(u'City'), null=True, blank=True, default=None, max_length=50)
    employment = models.CharField(verbose_name=_(u'Post'), max_length=50, null=True, blank=True, default=None)
    start_date = models.DateField(verbose_name=_(u'Start Date'), null=True, blank=True, default=None)
    end_date = models.DateField(verbose_name=_(u'End Date'), null=True, blank=True, default=None)
    present = models.BooleanField(verbose_name=_(u'Present?'), default=False)
    tasks = models.TextField(verbose_name=_(u'Tasks or Functions'), max_length=1000, null=True, blank=True, default=None)

    def __unicode__(self):
        return u'%s' % self.employment

    def get_form(self):
        from candidates.forms import ExpertiseForm
        return ExpertiseForm(instance=self)

    class Meta:
        verbose_name = _(u'Work Experience')
        verbose_name_plural = _(u'Work Experiences')
        ordering = ["-present", "-end_date", "-start_date", "employment"]

## End of Section Professional Experience ##


## Start of Section Academic ##

def get_degrees(select=True):
    """ Levels of Study """
    if select:
        choices = [['-1', _(u'Select') + '...']]
    else:
        choices = []
    try:
        degrees = Degree.objects.exclude(codename__iexact='indistinct')
        for degree in degrees:
            choices.append([degree.id, degree.name])
    except:
        print "Error in getting degrees(select=True)"
    return choices

class Academic_Area(models.Model):
    """ Area of study """
    name = models.CharField(verbose_name=_(u'Area'), max_length=100, null=True, blank=True, default=None)
    order = models.PositiveSmallIntegerField(null=True, blank=True, default=100)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'Academice Area')
        verbose_name_plural = _(u'Academice Areas')
        ordering = ['order', 'name']


# class Academic_Career(models.Model):
#     """ Technical and University Courses """
#     area = models.ForeignKey(Academic_Area, verbose_name=_(u'Academice Area'), related_name='careers', null=True, blank=True, default=None, on_delete=models.SET_NULL)
#     name = models.CharField(verbose_name=_(u'Career'), max_length=100, null=True, blank=True, default=None)
#     codename = models.CharField(max_length=20, null=True, blank=True, default=None)
#     order = models.PositiveSmallIntegerField(null=True, blank=True, default=100)

#     def __unicode__(self):
#         return u'%s' % self.name

#     class Meta:
#         verbose_name = _(u'Career')
#         verbose_name_plural = _(u'Careers')
#         ordering = ["order", "name"]


class Academic_Status(models.Model):
    """ Status of studying (graduate, truncate, ongoing) """
    name = models.CharField(verbose_name=_(u'Status'), max_length=30, null=True, blank=True, default=None)
    codename = models.CharField(max_length=15, null=True, blank=True, default=None)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'Status/Academic Status')
        verbose_name_plural = verbose_name
        ordering = ["name"]

# class School_Type(models.Model):
#     """ Type of Institution (Public or Private) """
#     name = models.CharField(verbose_name=_(u'Tipo'), max_length=15, null=True, blank=True, default=None)
#     codename = models.CharField(max_length=15, null=True, blank=True, default=None)

#     def __unicode__(self):
#         return u'%s' % self.name

#     class Meta:
#         verbose_name = _(u'Type of School')
#         verbose_name_plural = _(u'Types of School')


class Academic(models.Model):
    """ Academic background of a candidate, Relation Academic - Curriculum """
    candidate = models.ForeignKey(Candidate, verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, verbose_name=_(u'Level of Study'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # area = models.ForeignKey(Academic_Area, verbose_name=_(u'Academic Area'), null=True, blank=True, related_name='+', default=None, on_delete=models.SET_NULL)
    area = models.CharField(verbose_name=_(u'Specialisation'),null=True, blank=True, default=None, max_length=100)
    # career = models.ForeignKey(Academic_Career, verbose_name=_(u'Career'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    status = models.ForeignKey(Academic_Status, verbose_name=_(u'Status'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    course_name = models.CharField(verbose_name=_(u'Course Name'), max_length=100, null=True, blank=True, default=None)
    school = models.CharField(verbose_name=_(u'Institution'), max_length=100, null=True, blank=True, default=None)
    # address = models.ForeignKey(Address, verbose_name=_(u'Address'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, verbose_name=_(u'Country'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    state = models.CharField(verbose_name= _(u'State'), null=True, blank=True, default=None, max_length=50)
    city = models.CharField(verbose_name= _(u'City'), null=True, blank=True, default=None, max_length=50)
    # school_type = models.ForeignKey(School_Type, verbose_name=_(u'Type of Institution'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    start_date = models.DateField(verbose_name=_(u'Start Date'), null=True, blank=True, default=None)
    end_date = models.DateField(verbose_name=_(u'End Date'), null=True, blank=True, default=None)
    # present = models.BooleanField(verbose_name=_(u'Present?'), default=False)

    # def get_html_academic_name(self):
            # academic_name = ''
            # if self.degree:
            #     academic_name += self.degree.name
            # if self.area:
            #     academic_name += '<br><br>' + self.area.name
            # # if self.career:
            # #     academic_name += ' - ' + self.career.name
            # # if self.other:
            # #     academic_name += ' - ' + self.other
            # return academic_name

    def period(self):
        result = ""
        if self.start_date:
            result = str(self.start_date)
            if self.status.codename == 'progress':
                result += " - Ongoing"
            elif self.end_date:
                result += " - " + str(self.end_date)
            else:
                result += " - Ongoing"
        elif self.end_date and not self.status.codename == 'progress':
            result = str(self.end_date.year)
        return result

    def course_title(self):
        title=""
        if self.course_name:
            title = self.course_name
        elif self.degree:
            title = str(self.degree)
        else:
            title="No Course Title"
        if self.area:
            title += ', ' + self.area
        return title

    def get_form(self):
        from candidates.forms import AcademicForm
        return AcademicForm(instance=self)

    def __unicode__(self):
        return self.course_name
        # academic_name = ''
        # if self.degree:
        #     academic_name += self.degree.name
        # if self.area:
        #     academic_name += ' - ' + self.area.name
        # if self.career:
        #     academic_name += ' - ' + self.career.name
        # if self.other:
        #     academic_name += ' - ' + self.other
        # return u'%s' % academic_name

    class Meta:
        verbose_name = _(u'Education')
        verbose_name_plural = _(u'Educations')
        ordering = ["-end_date", "-start_date", "course_name"]

## End Section Academic ##


## Start of Section Languages ##

class Language(models.Model):
    """ Catalogue of Languages """
    name = models.CharField(verbose_name=_(u'Language'), max_length=20, blank=True, null=True, default=True)
    codename = models.CharField(max_length=10, blank=True, null=True, default=None)
    order = models.PositiveSmallIntegerField(null=True, blank=True, default=100)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'Language')
        verbose_name_plural = _(u'Languages')
        ordering = ['order']


class Language_Level(models.Model):
    """ Language level management (Basic, Medium, Advanced, Native) """
    name = models.CharField(verbose_name=_(u'Level'), max_length=15, blank=True, null=True, default=True)
    codename = models.CharField(max_length=15, blank=True, null=True, default=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'Language Proficiency')
        verbose_name_plural = verbose_name


class CV_Language(models.Model):
    """ Language proficiency of a candidate, Relatiom Language - Curriculum """
    candidate = models.ForeignKey(Candidate, verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, verbose_name=_(u'Language'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    # level = models.ForeignKey(Language_Level, verbose_name=_(u'Level'), null=True, blank=True, default=None, on_delete=models.SET_NULL)
    read = models.BooleanField(verbose_name=_(u'Can Read?'), default=False)
    write = models.BooleanField(verbose_name=_(u'Can Write?'), default=False)
    speak = models.BooleanField(verbose_name=_(u'Can Speak?'), default=False)

    def get_form(self):
        from candidates.forms import CvLanguageForm
        return CvLanguageForm(instance=self)

    def level(self):
        lvl = ""
        # count=0
        if self.read:
            lvl+='Read, '
        #     count = count+1
        if self.write:
            lvl+='Write, '
        #     count = count+1
        if self.speak:
            lvl+='Speak'
        #     count = count+1
        # if count>1:
        #     return ','.join(lvl)
        # elif count==1:
        return lvl.strip(', ')
        # else:
        #     return "Not Mentioned"

    def __unicode__(self):
        return u'%s' % self.language

    class Meta:
        verbose_name = _(u'Language')
        verbose_name_plural = _(u'Languages')
        ordering = ["language"]


## End of Section Lnaguages ""


## Start of Section Training ##

class Training(models.Model):
    candidate = models.ForeignKey(Candidate,verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    name = models.CharField(_(u'Name'), max_length=50)
    description = models.TextField()

    def get_form(self):
        from candidates.forms import TrainingForm
        return TrainingForm(instance=self)

    class Meta:
        verbose_name = "Training"
        verbose_name_plural = "Trainings"

    def __str__(self):
        return self.name
    
## End of Section Training ""

## Start of Section Certificate ##

class Certificate(models.Model):
    candidate = models.ForeignKey(Candidate,verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    name = models.CharField(_(u'Name'), max_length=50)
    description = models.TextField()

    class Meta:
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def get_form(self):
        from candidates.forms import CertificateForm
        return CertificateForm(instance=self)

    def __str__(self):
        return self.name
    
## End of Section Certificate ""

## Start of Section Project ##

class Project(models.Model):
    candidate = models.ForeignKey(Candidate,verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    name = models.CharField(_(u'Name'), max_length=50)
    description = models.TextField()

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def get_form(self):
        from candidates.forms import ProjectForm
        return ProjectForm(instance=self)

    def __str__(self):
        return self.name
    
## End of Section Project ""


## Section start Curriculum ""
def upload_cv_file_path(instance, filename):
    default_path = Curriculum.default_path
    # default_cv = ''
    return 'candidates/%s/cv-file/%s' % (str(instance.candidate.id), filename)

class Curriculum(models.Model):
    """ Indicates Curriculum Information recorded by a candiate """
    default_path = 'candidates'
    candidate = models.ForeignKey(Candidate, verbose_name=candidate, blank=True, null=True, default=None, on_delete=models.CASCADE)
    personal_info = models.BooleanField(verbose_name=_(u'Personal Information?'), default=False)
    objective = models.BooleanField(verbose_name=_(u'Professional Objective?'), default=False)
    expertise = models.BooleanField(verbose_name=_(u'Profesional Experience?'), default=False)
    academic = models.BooleanField(verbose_name=_(u'Academic Information?'), default=False)
    language = models.BooleanField(verbose_name=_(u'Languages?'), default=False)
    training = models.BooleanField(verbose_name=_(u'Trainings?'), default=False)
    certificate = models.BooleanField(verbose_name=_(u'Certificates?'), default=False)
    project = models.BooleanField(verbose_name=_(u'Projects?'), default=False)
    # software = models.BooleanField(verbose_name=_(u'Softwares?'), default=False)
    file = models.FileField(upload_to=upload_cv_file_path, blank=True, null=True)
    pdf_file = models.FileField(upload_to=upload_cv_file_path, blank=True, null=True)
    advance = models.IntegerField(verbose_name=_(u'Percent Complete'), blank=True, null=True, default=0)
    add_date = models.DateTimeField(verbose_name=_(u'Add Date'), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_(u'Last Modified'), auto_now=True)
    filecontent = models.TextField(default="", null=True, blank=True)


    def get_form(self):
        from candidates.forms import cv_FileForm
        return cv_FileForm(instance = self)

    def save(self, *args, **kw):
        print('saving')
        updatecontent = False
        if self.pk is not None:
            orig = Curriculum.objects.get(pk=self.pk)
            if orig.file != self.file:
                updatecontent = True
        else:
            updatecontent = True
        super(Curriculum, self).save(*args, **kw)
        if updatecontent and self.file:
            updatecontent = False
            content = get_file_content(self.file.path)
            try:
                self.filecontent = content
            except:
                try:
                    self.filecontent = content.encode('ascii')
                except:
                    self.filecontent = content.encode('utf8').decode('ascii','ignore')
            file_name = self.file.name.split("/")[-1]
            name = file_name.split(".")[0]
            ext = file_name.split(".")[-1]
            dir_path = os.path.dirname(self.file.path)
            if ext != 'pdf':
                subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', MEDIA_ROOT + "/" + self.file.name, '--outdir', dir_path])
            pdf_name = dir_path + "/" + name + ".pdf"
            self.pdf_file = pdf_name.replace(MEDIA_ROOT, '').strip('\\/')
            self.save()
#             self.filecontent = str(get_file_content(self.file.path))
#             self.save()


    def set_advance(self):
        percent = 0
        if self.personal_info:
            percent += 20
        if self.expertise:
            percent += 20
        if self.academic:
            percent += 20
        if self.language:
            percent += 5
        if self.training:
            percent += 5
        if self.certificate:
            percent += 5
        if self.project:
            percent += 5
        # if self.software:
        #     percent += 15
        if self.objective:
            percent += 10
        if self.file:
            percent += 80

        self.advance = percent

    def filename(self):
        return os.path.basename(self.file.name)

    def ext(self):
        ext = os.path.splitext(self.file.name)[1]
        ext = ext[1:].lower()
        return ext

    def file_content(self):
        return get_file_content(self.file.path)

    def file_text(self):
        return get_file_text(self.file.path)

    def __unicode__(self):
        return u'%s %s - Id: %s' % (self.candidate.first_name, self.candidate.last_name, str(self.candidate.id))

    class Meta:
        verbose_name = _(u'Curriculum')
        verbose_name_plural = _(u'Curricula')
        ordering = ['-advance']

## End of Section Curriculum ""


### IF YOU ADD ADDITIONAL MODELS, DO NOT FORGET TO REGISTER THEM IN ADMIN ###