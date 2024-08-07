# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.translation import ugettext as _
from django import forms
from localflavor.us.forms import USPhoneNumberField
from common.forms import get_states, get_municipals, get_initial_country
from candidates.models import *
from companies.forms import get_company_industries#, get_company_areas
from common.fields import SingleFileField, MultiFileField
import unicodedata
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget



select_text = _(u'Select')
select_option = _(u"Select an option")
initial_country = get_initial_country()  # Automatic Country Selection

def get_initial_date():
    """
    Set a date 21 years younger than the current with month and date as 1
    """
    year = (date.today() - relativedelta(years=21)).year
    initial_date = date(year, 1, 1)
    return initial_date


class CandidateForm(forms.ModelForm):
    countries = Country.objects.filter(~Q(continent='AF') & ~Q(continent='AN') & ~Q(continent='AS') & ~Q(continent='OC'))
    countries = Country.objects.all().order_by('name')
    # states = State.objects.filter(country=initial_country)
    initial_year = (date.today() - relativedelta(years=74)).year
    end_year = (date.today() - relativedelta(years=18)).year
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name(s)'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=2,
        required=True,
        label=_(u'Name'),
        error_messages={'required': _(u"Enter your Name")},
    )
    public_email = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
        required = False,
        label=_(u'Email'),
        error_messages={'required': _(u"Enter your Email")},
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Surname'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=2,
        required=True,
        label=_(u'Surname'),
        error_messages={'required': _(u"Enter your Surname")},
    )
    birthday = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Birthdate'), 'class': "form-control"}),
        required=True,
        label=_(u'Birthdate'),
        error_messages={'required': _(u"Enter your Birthdate")},
    )
    gender = forms.ModelChoiceField(
        queryset=Gender.objects.filter(~Q(codename='indistinct')),
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=True,
        label=_(u'Gender'))
    maritalStatus = forms.ModelChoiceField(
        queryset=Marital_Status.objects.all(),
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=True,
        label=_(u'Marital Status'))
    
    # min_salary = forms.IntegerField(
     #     required=False,
     #     max_value=200000,
     #     min_value=1000,
     #     widget=forms.TextInput(attrs={'placeholder': _(u'Required (Do not include points or commas)'), 'class': 'form-control'}),
     #     label=_(u'Minimum required Salary'),
     #     error_messages={'invalid': _(u"Enter a valid number, withour commas or points"),
     #                     'min_value': _(u'Enter an amount greater than 1000'),
     #                     'max_value': _(u'Enter an amount less than 200000')},
     # )
     # max_salary = forms.IntegerField(
     #     required=False,
     #     max_value=200000,
     #     min_value=1000,
     #     widget=forms.TextInput(attrs={'placeholder': _(u'Requerido (No incluir punto ni comas)'), 'class': 'form-control'}),
     #     label=_(u'Sueldo deseado'),
     #     error_messages={'invalid': _(u"Ingrese una cantidad válida, sin comas ni punto"),
     #                     'min_value': _(u'Enter an amount greater than 1000'),
     #                     'max_value': _(u'Enter an amount less than 200000')},
     # )
     # travel = forms.BooleanField(
     #     label=_(u'Availability to Travel'),
     #     required=False,
     # )
     # residence = forms.BooleanField(
     #     label=_(u'Availability to change residence'),
     #     required=False,
     # )
    public_photo = forms.ImageField(widget=forms.FileInput(attrs={'class':"form-control text-center", 'accept':"image/*"}), required=False)

    def __init__(self, *args, **kwargs):
        # state_selected = kwargs.pop('state_selected', None)
        try:
            public = kwargs.pop('isPublic')
        except:
            public = False
        super(CandidateForm, self).__init__(*args, **kwargs)

        if public:
            self.fields['public_email'].required = True
        # self.fields['state'].choices = get_states(initial_country)
        # self.fields['municipal'].choices = get_municipals(state_selected)

    def clean_public_photo(self):
        default_photo = None
        from PIL import Image
        image = self.cleaned_data.get('public_photo', None)
        if image:
            img = Image.open(image)

            # Validate dimensions
            # w, h = img.size
            # max_width = max_height = 500
            # if w >= max_width or h >= max_height:
            #     raise forms.ValidationError(
            #         _('Please use an image that is smaller or equal to '
            #           '%s x %s pixels.' % (max_width, max_height)))

            # Validate extension (jpg or png)
            # print img.format
            # print img.format.lower()
            if img.format.lower() not in ['jpeg', 'pjpeg', 'png', 'jpg', 'mpo']:
                raise forms.ValidationError(_(u'You can only use images withextensions JPG, JPEG or PNG'))

            #validate file size
            if len(image) > (1 * 1024 * 1024):
                raise forms.ValidationError(_(u'The image selected is too large (Max 1MB)'))
        else:
            return default_photo
        return image

    # def clean_min_salary(self):
     #     try:
     #         min_salary = (None if self.data['min_salary'] == '' else int(self.data['min_salary']))
     #     except:
     #         min_salary = 0
     #     if not min_salary:
     #         # raise forms.ValidationError(_(u'You must enter a valid amount'))
     #         min_salary = 0
     #     if min_salary <= 999:
     #         raise forms.ValidationError(_(u'You must enter an amount greater than 60'))
     #     elif min_salary >= 200000:
     #         raise forms.ValidationError(_(u'You must enter an amount less than 500000'))
     #     return min_salary

    # def clean_max_salary(self):
     #     try:
     #         max_salary = (None if self.data['max_salary'] == '' else int(self.data['max_salary']))
     #     except:
     #         max_salary = 0
     #     if not max_salary:
     #         max_salary = 0
     #         # raise forms.ValidationError(_(u'You must enter a valid amount'))
     #     if max_salary <= 999:
     #         raise forms.ValidationError(_(u'You must enter an amount greater than 60'))
     #     elif max_salary >= 200000:
     #         raise forms.ValidationError(_(u'You must enter an amount less than 500000'))
     #     min_salary = self.cleaned_data.get('min_salary')
     #     if not min_salary ==max_salary == 0 and min_salary > max_salary:
     #         raise forms.ValidationError(_(u'The maximum salary can not be less than the minimum wage'))
     #     return max_salary
 

    class Meta:
        model = Candidate
        fields =('public_photo','maritalStatus','gender','birthday','last_name','public_email','first_name')
        # exclude = ('user', 'country', 'objective', 'courses', 'photo','')

class CandidateContactForm(forms.ModelForm):
    countries = Country.objects.all().order_by('name')
    initial_year = (date.today() - relativedelta(years=74)).year
    end_year = (date.today() - relativedelta(years=18)).year
    nationality = forms.ModelChoiceField(
        queryset=countries,
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=True,
        label=_(u'Country'),
        initial=initial_country)
    state = forms.CharField(
        # queryset=states,
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your State"}),
        # empty_label=select_text,
        max_length=30,
        min_length=2,
        required=True,
        label=_(u'State'),
        error_messages={
            'required': _(u"State is required")},
    )
    city = forms.CharField(
        # choices=get_municipals(None),
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your City"}),
        max_length=30,
        min_length=2,
        label=_(u'City'),
        required=True,
        error_messages={
            'required': _(u"City is required")},
    )
    phone = USPhoneNumberField(
        min_length=10,
        max_length=12,
        error_messages={
            'invalid': _(u"Enter a valid 10 digit phone"),
            'min_length': _(u"Enter a valid 10 digit phone"),
            'max_length': _(u"Enter a valid 10 digit phone"),
        },
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Local telephone number to 10 digits'), 'class': "form-control"}),
    )
    cellphone = USPhoneNumberField(
        min_length=10,
        max_length=12,
        error_messages={
            'invalid': _(u"Enter a valid 10 digit mobile phone"),
            'min_length': _(u"Enter a valid 10 digit mobile phone"),
            'max_length': _(u"Enter a valid 10 digit mobile phone"),
        },
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Cell number to 10 digits'), 'class': "form-control"}),
    )
    linkedin = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': _(u'http://linkedin.com/YourAccount'),
                                      'class': "form-control"}),
        max_length=150,
        required=False
    )
    facebook = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': _(u'www.facebook.com/YourAccount'),
                                      'class': "form-control"}),
        max_length=150,
        required=False
    )
    twitter = forms.RegexField(
        widget=forms.TextInput(attrs={'placeholder': _(u'@username'),
                                      'class': "form-control"}),
        regex=r'^[\w@]+$',
        max_length=16,
        min_length=3,
        error_messages={
            'invalid': _(u"Enter a valid Twitter user"),
        },
        required=False
    )
    google = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': _(u'https://plus.google.com/YourAccount'),
                                      'class': "form-control"}),
        max_length=150,
        required=False
    )
    def clean_linkedin(self):
        linkedin_error = _(u'Enter a valid Linkedin page.')
        if not self.cleaned_data.get('linkedin'):
            return None
        linkedin = self.cleaned_data.get('linkedin')
        if 'linkedin.com/' not in linkedin.lower():
            raise forms.ValidationError(linkedin_error)
        if len(linkedin) < 17:
            raise forms.ValidationError(linkedin_error)
        return linkedin

    def clean_facebook(self):
        facebook_error = _(u'Enter a valid Facebook page.')
        if not self.cleaned_data.get('facebook'):
            return None
        facebook = self.cleaned_data.get('facebook')
        if 'facebook.com/' not in facebook.lower():
            raise forms.ValidationError(facebook_error)
        if len(facebook) < 26:
            raise forms.ValidationError(facebook_error)
        return facebook

    def clean_twitter(self):
        twitter_error = _(u'Enter a valid Twitter user')
        if not self.cleaned_data.get('twitter'):
            return None
        twitter = self.cleaned_data.get('twitter')
        if twitter.count('@') > 1:
            raise forms.ValidationError(twitter_error)
        if twitter.count('@') > 0:
            if not twitter.startswith('@'):
                raise forms.ValidationError(twitter_error)
            twitter = twitter.replace('@', '')
            # raise forms.ValidationError(twitter_error)
        return twitter

    def clean_google(self):
        google_error = _(u'Enter a vlaid Google+ page')
        if not self.cleaned_data.get('google'):
            return None
        google = self.cleaned_data.get('google')
        if 'plus.google.com/' not in google.lower():
            raise forms.ValidationError(google_error)
        if len(google) < 29:
            raise forms.ValidationError(google_error)
        return google

    class Meta:
        model = Candidate
        fields = ('nationality', 'state', 'city', 'phone', 'cellphone', 'linkedin', 'facebook', 'twitter', 'google')

class ObjectiveForm(forms.ModelForm):
    objective = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _(u'Enter your professional objectives'),
                                      'class': "form-control"}),
        max_length=300,
        min_length=30,
        required=True,
        label=_(u'Professional Objectives'),
        error_messages={'required': _(u"Enter your professional objectives")},
    )
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':_(u'Skills'),
                                        'class': 'form-control no-dropdown text-left'}),
        label=_(u'Skills'),
    )
    class Meta:
        model = Candidate
        fields = ('objective','skills')


class InterestsForm(forms.ModelForm):
    interests = forms.CharField(
        widget=CKEditorWidget(attrs={'placeholder':_(u'Interests'),
                                        'class': 'form-control'}),
        label=_(u'Interests'),
        required=False
    )
    class Meta:
        model = Candidate
        fields = ('interests',)


class HobbiesForm(forms.ModelForm):
    hobbies = forms.CharField(
        widget = CKEditorWidget(attrs={'placeholder':_(u'Hobbies'),
                                        'class': 'form-control'}),
        label=_(u'Hobbies'),
        required=False
    )
    class Meta:
        model = Candidate
        fields = ('hobbies',)


class ExtraCurricularsForm(forms.ModelForm):
    extra_curriculars = forms.CharField(
        widget = CKEditorWidget(attrs={'placeholder':_(u'Extra Curriculars'),
                                        'class': 'form-control'}),
        # widget=forms.TextInput(attrs={'placeholder':_(u'Extra Curriculars'),
                                        # 'class': 'form-control no-dropdown text-left'}),
        label=_(u'Extra Curriculars'),
        required=False
    )
    class Meta:
        model = Candidate
        fields = ('extra_curriculars',)


class OthersForm(forms.ModelForm):
    others = forms.CharField(
        widget=CKEditorWidget(attrs={'placeholder':_(u'Others'),
                                        'class': 'form-control'}),
        label=_(u'Others'),
        required=False
    )
    class Meta:
        model = Candidate
        fields = ('others',)

# class CoursesForm(forms.ModelForm):
#     courses = forms.CharField(
#         widget=forms.Textarea(attrs={'placeholder': _(u'Enter diplomas, workshops and courses you have attended.'),
#                                       'class': "form-control"}),
#         max_length=700,
#         min_length=0,
#         required=False,
#         label=_(u'Diplomas, workshops and courses that you have attended'),
#     )
#     class Meta:
#         model = Candidate
#         fields = ('courses',)


class ExpertiseForm(forms.ModelForm):
    """ Work experience of a candidate """
    company = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the organisation'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=3,
        required=True,
        label=_(u'Empresa'),
        error_messages={'required': _(u"Enter name of the company")},
    )
    industry = forms.ChoiceField(
        choices=get_company_industries(),
        widget=forms.Select(attrs={'class': "form-control"}),
        label=_(u'Industry'),
    )
    # area = forms.ChoiceField(
    #     choices=get_company_areas(None),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    #     label=_(u'Area'),

    # )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label=select_text,
        required=True,
        initial=initial_country,
        label=_(u'Country'),
        widget=forms.Select(attrs={'class': "form-control"}),
    )
    employment = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Position held'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        required=True,
        label=_(u'Post'),
        error_messages={'required': _(u"Enter the name of your position")},
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'State'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        required=False,
        label=_(u'Post'),
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'City'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        required=False,
        label=_(u'Post'),
    )
    present = forms.BooleanField(
        label=_(u'Current job?'),
        required=False,
    )

    start_date = forms.DateField(
        widget = forms.TextInput(attrs={'class':"form-control"}),
        label=_(u'Start date'),
        required=True,
        error_messages={'required': _(u"Enter your start date")},
    )
    end_date = forms.DateField(
        widget = forms.TextInput(attrs={'class':"form-control"}),
        label=_(u'End date'),
        required=False,
        error_messages={'required': _(u"Enter your end date")},
    )
    tasks = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _(u'Describe the tasks performed.'),
                                      'class': "form-control input-sm",'rows':'5','columns':'40'}),
        max_length=1000,
        min_length=20,
        required=True,
        label=_(u'Tasks/Functions Performed'),
        error_messages={'required': _(u"Enter a description")},
    )

    def __init__(self, *args, **kwargs):
        update = False
        industry_selected = kwargs.pop('industry_selected', None)
        present = kwargs.pop('present', None)
        try:
            if kwargs.pop('update'):
                update = True
        except:
            pass
        super(ExpertiseForm, self).__init__(*args, **kwargs)

        if present:
                self.fields['end_date'].required = False

        if update:
            self.fields['industry'].choices = get_company_industries()
            # self.fields['area'].choices = get_company_areas(industry_selected)

        if self.is_bound:
            # self.fields['area'].choices = get_company_areas(industry_selected)
            if present:
                self.fields['end_date'].required = False

    def clean_industry(self):
        invalid_industry = _(u'The industry you selected is invalid')
        try:
            industry_id = int(self.cleaned_data.get('industry'))
        except:
            raise forms.ValidationError(invalid_industry)
        if industry_id <= 0:
            raise forms.ValidationError(_(u'Slect an industry'))
        try:
            industry = Company_Industry.objects.get(pk = industry_id)
        except Company_Industry.DoesNotExist:
            raise forms.ValidationError(invalid_industry)
        return industry

    # def clean_area(self):
    #     invalid_area = _(u'Invalid Area')
    #     try:
    #         area_id = int(self.cleaned_data.get('area'))
    #     except:
    #         raise forms.ValidationError(invalid_area)
    #     if area_id < 0:
    #         raise forms.ValidationError(invalid_area)
    #     if area_id == 0:
    #         raise forms.ValidationError(_(u'You must first select an industry'))
    #     try:
    #         industry = self.cleaned_data.get('industry')
    #         try:
    #             areas = industry.company_area_set.all()
    #         except:
    #             areas = []
    #         choices = [0]
    #         for area in areas:
    #             choices.append(area.id)
    #         if area_id not in choices:
    #             raise forms.ValidationError(invalid_area)
    #         area= Company_Area.objects.get(pk = area_id)
    #     except Company_Area.DoesNotExist:
    #         raise forms.ValidationError(invalid_area)
    #     return area

    def clean_start_date(self):
        import datetime
        start_date = self.cleaned_data.get('start_date')
        try:
            present = self.data['present']
            present = True
        except:
            present = False
        if not present:
            end_date = self.data['end_date']
            if end_date:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_date > end_date:
                    raise forms.ValidationError(_(u'The date of start can not be greater than the date of leaving'))
                if start_date == end_date:
                    raise forms.ValidationError(_(u'The date of start cannot be the same as date of leaving'))
        return start_date

    class Meta:
        model = Expertise
        exclude = ('candidate',)


class AcademicForm(forms.ModelForm):
    degree = forms.ChoiceField(
        choices=get_degrees(),
        required=True,
        widget=forms.Select(attrs={'class': "form-control"}),
        label=_(u'Level of Study'),
    )
    area = forms.CharField(
        # queryset=Academic_Area.objects.all(),
        # empty_label=select_text,
        required=True,
        label=_(u'Specialisation of Study'),
        widget=forms.TextInput(attrs={'class': "form-control"}),
        max_length = 100,
        min_length = 4,
        error_messages={'required': 'Specialisation is required'},
    )

    # career = forms.ChoiceField(
    #     choices=get_academic_careers(None),
    #     required=True,
    #     widget=forms.Select(attrs={'class': "form-control"}),
    #     label=_(u'Career'),
    # )
    course_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the Course'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=1,
        required=True,
        label=_(u'Course Name'),
        error_messages={'required': 'Enter your Course Name'},
    )
    status = forms.ModelChoiceField(
        queryset=Academic_Status.objects.all(),
        empty_label=select_text,
        required=True,
        label=_(u'Status'),
        widget=forms.Select(attrs={'class': "form-control"}),
        error_messages={'required': select_option},
    )
    school = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the Institution'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=3,
        required=True,
        label=_(u'Institution'),
        error_messages={'required': _(u"Enter the name of the Institution")},
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label=select_text,
        required=True,
        initial=initial_country,
        label=_(u'Country'),
        widget=forms.Select(attrs={'class': "form-control"}),
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the State'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=2,
        required=False,
        label=_(u'State'),
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the City'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=2,
        required=False,
        label=_(u'City'),
        error_messages={'required': _(u"Enter the name of the City")},
    )
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class':"form-control"}),
        label=_(u'Admission Date'),
        required=True,
        error_messages={'required': _(u"Enter you admission date")},
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class':"form-control"}),
        label=_(u'End Date'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        update = False
        # area_selected = kwargs.pop('area_selected', None)
        try:
            if kwargs.pop('update'):
                update = True
        except:
            pass
        super(AcademicForm, self).__init__(*args, **kwargs)

        if update:
            # self.fields['career'].choices = get_academic_careers(area_selected)
            pass
        if self.is_bound:
            try:
                degree = self.data.get('degree')
                if degree and int(degree) > 0:
                    degree = Degree.objects.get(id=degree)
                    if degree.codename == 'bachelor' or degree.codename == 'high_school' or degree.codename == 'elementary_school':
                        # If primary, secondary or high school is selected, turn the required fields to no
                        self.fields['area'].required = False
                        # self.fields['career'].required = False
                        # self.fields['other'].required = False
                    else:
                        self.fields['area'].required = True
                        # self.fields['career'].required = True
                        # self.fields['other'].required = True
                # career = self.data.get('career')
                # if career and int(career) > 0:
                #     # career = Academic_Career.objects.get(id=career)
                #     if career.codename == 'other':
                #         self.fields['other'].required = True
                #     else:
                #         self.fields['other'].required = False
                status = self.data.get('status')
                if status and int(status) > 0:
                    status = Academic_Status.objects.get(pk=status)
                    if status.codename == 'progress':
                        self.fields['end_date'].required = False
                    else:
                        self.fields['end_date'].required = True
            except:
                pass

            # if area_selected == -1:
                # area_selected = None
            # self.fields['career'].choices = get_academic_careers(area_selected)

    def clean_degree(self):
        invalid_degree = _(u'Level of Study is Invalid')
        try:
            degree_id = int(self.cleaned_data.get('degree'))
        except:
            raise forms.ValidationError(invalid_degree)
        if degree_id <= 0:
            raise forms.ValidationError(_(u'Select a Level of Study'))
        try:
            # degree = self.cleaned_data.get('degree')
            degree = Degree.objects.get(pk = degree_id)
        except Degree.DoesNotExist:
            raise forms.ValidationError(invalid_degree)
        return degree

    # def clean_career(self):
    #     invalid_career = _(u'Invalid Career')
    #     try:
    #         degree = int(self.data.get('degree'))
    #         if degree > 0:
    #             degree = Degree.objects.get(id=degree)
    #             if degree.codename == 'bachelor' or degree.codename == 'high_school' or degree.codename == 'elementary_school':
    #                 return None
    #     except:
    #         pass
    #     try:
    #         career_id = int(self.cleaned_data.get('career'))
    #     except:
    #         raise forms.ValidationError(invalid_career)
    #     if career_id < 0:
    #         raise forms.ValidationError(_(u'Select a Career'))
    #     try:
    #         area = self.cleaned_data.get('area')
    #         try:
    #             careers = area.careers.all()
    #         except:
    #             careers = []
    #         choices = []
    #         for career in careers:
    #             choices.append(career.id)
    #         if career_id not in choices:
    #             raise forms.ValidationError(invalid_career)
    #         career = Academic_Career.objects.get(pk = career_id)
    #     except Academic_Career.DoesNotExist:
    #         raise forms.ValidationError(invalid_career)
    #     return career

    # def clean_other(self):
    #     other = None
    #     try:
    #         career_id = int(self.data.get('career'))
    #         career = Academic_Career.objects.get(id=career_id)
    #         if career:
    #             if career.codename == 'other':
    #                 other = self.data.get('other')
    #             else:
    #                 other = None
    #     except:
    #         other = None
    #     return other

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        status = self.cleaned_data.get('status')
        validate = False
        if status and status.codename != 'progress':
            validate = True
        elif not status:
            end_date = self.data['end_date']
            if end_date:
                validate = True
        if validate:
            try:
                import datetime
                end_date = self.data['end_date']
                end_date = datetime.datetime.strptime(end_date, "%Y-%d-%m").date()
            except:
                end_date = None
            if end_date:
                if start_date > end_date:
                    raise forms.ValidationError(_(u'The start date can not be greater than the end date'))
                if start_date == end_date:
                    raise forms.ValidationError(_(u'The start date can not be the same as end date'))
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        status = self.cleaned_data.get('status')
        if status and status.codename == 'progress':
            end_date = None
        return end_date

    class Meta:
        model = Academic
        exclude = ('candidate', 'present')


class CvLanguageForm(forms.ModelForm):
    language = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        empty_label=_(u'Select')+'...',
        required=True,
        label=_(u'Language'),
        widget=forms.Select(attrs={'class': "form-control"}),
        error_messages={'required': _(u"Select a Language")},
    )
    read = forms.BooleanField(
        label=_(u'Availability to Read'),
        required=False,
    )
    write = forms.BooleanField(
        label=_(u'Availability to Write'),
        required=False,
    )
    speak = forms.BooleanField(
        label=_(u'Availability to Speak'),
        required=False,
    )
    # level = forms.ModelChoiceField(
    #     queryset=Language_Level.objects.all(),
    #     empty_label=None,
    #     required=True,
    #     label=_(u'Level'),
    #     widget=forms.RadioSelect,
    #     error_messages={'required': _(u"Select a Level")},
    # )

    class Meta:
        model = CV_Language
        exclude = ('candidate',)

class TrainingForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        min_length=2,
        max_length=50,
        label= _(u'Name'),
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}),
        error_messages={'required':_(u'Enter the name of Training taken')}
    )
    description = forms.CharField(
        required=True,
        min_length=50,
        max_length=300,
        label= _(u'Name'),
        widget=forms.Textarea(attrs={'class':'form-control input-sm','placeholder':'Description of the Training'}),
        error_messages={'required':_(u'Enter the description of the training taken')}
    )

    class Meta:
        model = Training
        fields = ('name','description')

class CertificateForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        min_length=4,
        max_length=50,
        label= _(u'Name'),
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}),
        error_messages={'required':_(u'Enter the name of Certification taken')}
    )
    description = forms.CharField(
        required=True,
        min_length=50,
        max_length=300,
        label= _(u'Description'),
        widget=forms.Textarea(attrs={'class':'form-control input-sm','placeholder':'Description of the Certification'}),
        error_messages={'required':_(u'Enter the description of the Certification taken')}
    )

    class Meta:
        model = Certificate
        fields = ('name','description')

class ProjectForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        min_length=4,
        max_length=50,
        label= _(u'Name'),
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}),
        error_messages={'required':_(u'Enter the name of Project taken')}
    )
    description = forms.CharField(
        required=True,
        min_length=50,
        max_length=300,
        label= _(u'Name'),
        widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Description of the Project'}),
        error_messages={'required':_(u'Enter the description f the Project taken')}
    )

    class Meta:
        model = Project
        fields = ('name','description')
    
class cv_FileForm(forms.ModelForm):
    max_megas = 5
    max_files = 1
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'multiple': False,
                'accept': 'application/pdf,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
            }
        ),
        required=False
    )

    def validate_number_files(self, files):
        if files > self.max_files:
            msg = _(u'You can only upload upto %s files') % self.max_files
            self.add_error('file', msg)
        pass

    def clean_file(self):
        file = self.cleaned_data['file']

        if file:
            if file.size > self.max_megas * 1024000:
                raise ValidationError(_(u'The filesize of %s is greater than %s MB') % (file.name, self.max_megas))

            valid_extensions = ['doc','docx','pdf']
            extension = os.path.splitext(file.name)[1]
            extension = extension[1:].lower()
            if extension not in valid_extensions:
                raise ValidationError(u'Only Word and Pdfs are allowed.')

            # Accents and other special charcters in the name of the file are removed
            name = ''.join((c for c in unicodedata.normalize('NFD', file.name) if unicodedata.category(c) != 'Mn'))
            file.name = name
            return file
        else:
            return None

    class Meta:
        model = Curriculum
        fields = ['file']


class CandidateMiniForm(forms.ModelForm):
    # countries = Country.objects.filter(~Q(continent='AF') & ~Q(continent='AN') & ~Q(continent='AS') & ~Q(continent='OC'))
    countries = Country.objects.all().order_by('name')
    # states = State.objects.filter(country=initial_country)
    initial_year = (date.today() - relativedelta(years=74)).year
    end_year = (date.today() - relativedelta(years=18)).year
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name(s)'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=2,
        required=True,
        label=_(u'Name'),
        error_messages={'required': _(u"Enter your Name")},
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Surname'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=2,
        required=True,
        label=_(u'Surname'),
        error_messages={'required': _(u"Enter your Surname")},
    )
    public_email = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
        required = True,
        label=_(u'Email'),
        error_messages={'required': _(u"Enter your Email")},
    )
    phone = USPhoneNumberField(
        min_length=10,
        max_length=12,
        error_messages={
            'invalid': _(u"Enter a valid 10 digit phone"),
            'min_length': _(u"Enter a valid 10 digit phone"),
            'max_length': _(u"Enter a valid 10 digit phone"),
        },
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Local telephone number to 10 digits'), 'class': "form-control"}),
    )
    nationality = forms.ModelChoiceField(
        queryset=countries,
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=False,
        label=_(u'Country'),
        initial=initial_country)
    state = forms.CharField(
        # queryset=states,
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your State"}),
        # empty_label=select_text,
        max_length=30,
        min_length=2,
        required=False,
        label=_(u'State'),
        error_messages={
            'required': _(u"State is required")},
    )
    city = forms.CharField(
        # choices=get_municipals(None),
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your City"}),
        max_length=30,
        min_length=2,
        label=_(u'City'),
        required=False,
        error_messages={
            'required': _(u"City is required")},
    )
    public_photo = forms.ImageField(
        widget=forms.FileInput(attrs={'class':"form-control text-center", 'accept':"image/*"}), 
        required=False
    )

    def __init__(self, *args, **kwargs):
        # state_selected = kwargs.pop('state_selected', None)
        try:
            public = kwargs.pop('isPublic')
        except:
            public = False
        instance = kwargs.get('instance', None)
        if instance and instance.user:
            kwargs.update(initial={'public_email': instance.user.email})

        super(CandidateMiniForm, self).__init__(*args, **kwargs)
        if instance and instance.user:
            self.fields['public_email'].required = False
            self.fields['public_email'].disabled = True

        if public:
            self.fields['public_email'].required = True
        # self.fields['state'].choices = get_states(initial_country)
        # self.fields['municipal'].choices = get_municipals(state_selected)

    def clean_public_photo(self):
        default_photo = None
        from PIL import Image
        image = self.cleaned_data.get('public_photo', None)
        if image:
            img = Image.open(image)

            # Validate dimensions
            # w, h = img.size
            # max_width = max_height = 500
            # if w >= max_width or h >= max_height:
            #     raise forms.ValidationError(
            #         _('Please use an image that is smaller or equal to '
            #           '%s x %s pixels.' % (max_width, max_height)))

            # Validate extension (jpg or png)
            # print img.format
            # print img.format.lower()
            if img.format.lower() not in ['jpeg', 'pjpeg', 'png', 'jpg', 'mpo']:
                raise forms.ValidationError(_(u'You can only use images withextensions JPG, JPEG or PNG'))

            #validate file size
            if len(image) > (1 * 1024 * 1024):
                raise forms.ValidationError(_(u'The image selected is too large (Max 1MB)'))
        else:
            return default_photo
        return image

    def clean_public_email(self):
        if self.instance.user:
            return ''
        return self.cleaned_data.get('public_email','')

    class Meta:
        model = Candidate
        fields =('public_photo','last_name','public_email','first_name', 'nationality', 'state', 'city', 'phone')
        # exclude = ('user', 'country', 'objective', 'courses', 'photo','')

class ExpertiseMiniForm(forms.ModelForm):
    
    """ Work experience of a candidate """
    company = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the organisation'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=3,
        required=True,
        label=_(u'Empresa'),
        error_messages={'required': _(u"Enter name of the company")},
    )
    employment = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Position held'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        required=True,
        label=_(u'Post'),
        error_messages={'required': _(u"Enter the name of your position")},
    )
    present = forms.BooleanField(
        label=_(u'Current job?'),
        required=False,
    )

    employment_start_date = forms.DateField(
        widget = forms.TextInput(attrs={'class':"form-control", 'placeholder':'Start Date'}),
        label=_(u'Start date'),
        required=True,
        error_messages={'required': _(u"Enter your start date")},
    )
    employment_end_date = forms.DateField(
        widget = forms.TextInput(attrs={'class':"form-control", 'placeholder':'End Date'}),
        label=_(u'End date'),
        required=False,
        error_messages={'required': _(u"Enter your end date")},
    )

    def __init__(self, *args, **kwargs):
        update = False
        present = kwargs.pop('present', None)
        try:
            if kwargs.pop('update'):
                update = True
        except:
            pass
        super(ExpertiseMiniForm, self).__init__(*args, **kwargs)

        if present:
            self.fields['employment_end_date'].required = False

        if self.is_bound:
            if present:
                self.fields['employment_end_date'].required = False

        instance = kwargs.get('instance', None)
        if instance:
            self.fields['employment_start_date'].initial = instance.start_date
            self.fields['employment_end_date'].initial = instance.end_date
            # self.fields['employment_country'].initial = instance.country
            # self.fields['employment_state'].initial = instance.state
            # self.fields['employment_city'].initial = instance.city

    def add_prefix(self, field_name):
        FIELD_NAME_MAPPING = {
            'start_date': 'employment_start_date',
            'end_date': 'employment_end_date'
        }
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(ExpertiseMiniForm, self).add_prefix(field_name)

    def clean_employment_start_date(self):
        import datetime
        start_date = self.cleaned_data.get('employment_start_date')
        try:
            present = self.cleaned_data['present']
            present = True
        except:
            present = False
        if not present:
            end_date = self.cleaned_data['employment_end_date']
            if end_date:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_date > end_date:
                    raise forms.ValidationError(_(u'The date of start can not be greater than the date of leaving'))
                if start_date == end_date:
                    raise forms.ValidationError(_(u'The date of start cannot be the same as date of leaving'))
        return start_date

    class Meta:
        model = Expertise
        # exclude = ('candidate',)
        fields = ('company', 'employment', 'present', 'start_date', 'end_date')

class AcademicMiniForm(forms.ModelForm):

    course_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the Course'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=1,
        required=True,
        label=_(u'Course Name'),
        error_messages={'required': 'Enter your Course Name'},
    )
    status = forms.ModelChoiceField(
        queryset=Academic_Status.objects.all(),
        empty_label=select_text,
        required=True,
        label=_(u'Status'),
        widget=forms.Select(attrs={'class': "form-control"}),
        error_messages={'required': select_option},
    )
    school = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the Institution'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=3,
        required=True,
        label=_(u'Institution'),
        error_messages={'required': _(u"Enter the name of the Institution")},
    )
    academic_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label=select_text,
        required=False,
        # initial=initial_country,
        label=_(u'Country'),
        widget=forms.Select(attrs={'class': "form-control"}),
    )
    academic_state = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the State'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=2,
        required=False,
        label=_(u'State'),
    )
    academic_city = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the City'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=2,
        required=False,
        label=_(u'City'),
        error_messages={'required': _(u"Enter the name of the City")},
    )
    academic_start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class':"form-control", 'placeholder':'Start Date'}),
        label=_(u'Admission Date'),
        required=False,
        error_messages={'required': _(u"Enter you admission date")},
    )
    academic_end_date = forms.DateField(
        widget=forms.TextInput(attrs={'class':"form-control", 'placeholder':'End Date'}),
        label=_(u'End Date'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        update = False
        # area_selected = kwargs.pop('area_selected', None)
        try:
            if kwargs.pop('update'):
                update = True
        except:
            pass
        super(AcademicMiniForm, self).__init__(*args, **kwargs)

        if update:
            # self.fields['career'].choices = get_academic_careers(area_selected)
            pass
        if self.is_bound:
            try:
                status = self.data.get('status')
                if status and int(status) > 0:
                    status = Academic_Status.objects.get(pk=status)
                    if status.codename == 'progress':
                        self.fields['academic_end_date'].required = False
                    else:
                        self.fields['academic_end_date'].required = True
            except:
                pass
        instance = kwargs.get('instance', None)
        if instance:
            self.fields['academic_start_date'].initial = instance.start_date
            self.fields['academic_end_date'].initial = instance.end_date
            self.fields['academic_country'].initial = instance.country
            self.fields['academic_state'].initial = instance.state
            self.fields['academic_city'].initial = instance.city

    def add_prefix(self, field_name):
        FIELD_NAME_MAPPING = {
            'start_date': 'academic_start_date',
            'end_date': 'academic_end_date',
            'country': 'academic_country',
            'state': 'academic_state',
            'city': 'academic_city'
        }
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(AcademicMiniForm, self).add_prefix(field_name)

    def clean_academic_start_date(self):
        start_date = self.cleaned_data.get('academic_start_date')
        status = self.cleaned_data.get('status')
        validate = False
        if status and status.codename != 'progress':
            validate = True
        elif not status:
            end_date = self.cleaned_data.get('academic_end_date')
            if end_date:
                validate = True
        if validate:
            try:
                import datetime
                end_date = self.cleaned_data['academic_end_date']
                end_date = datetime.datetime.strptime(end_date, "%Y-%d-%m").date()
            except:
                end_date = None
            if end_date:
                if start_date > end_date:
                    raise forms.ValidationError(_(u'The start date can not be greater than the end date'))
                if start_date == end_date:
                    raise forms.ValidationError(_(u'The start date can not be the same as end date'))
        return start_date

    def clean_academic_end_date(self):
        end_date = self.cleaned_data.get('academic_end_date')
        status = self.cleaned_data.get('status')
        if status and status.codename == 'progress':
            end_date = None
        return end_date

    class Meta:
        model = Academic
        # exclude = ('candidate', 'present')
        fields = ('course_name', 'status', 'school', 'country', 'state', 'city', 'start_date', 'end_date')


ExpertiseFormset = forms.modelformset_factory(Expertise, form=ExpertiseMiniForm, extra=0)
AcademicFormset = forms.modelformset_factory(Academic, form=AcademicMiniForm, extra=0)