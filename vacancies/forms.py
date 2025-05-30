# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
import unicodedata
from ckeditor.widgets import CKEditorWidget
from companies.models import Ban, Company_Industry as Industry
#from common.fields import MultiFileField
from common.forms import get_initial_country
from common.models import *
from customField.models import Template
from datetime import datetime, date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.widgets import SelectDateWidget
from django.utils.translation import gettext as _
from TRM.settings import days_default_search
from upload_logos.widgets import AjaxClearableFileInput
from vacancies.models import *


def diff_month(d1, d2):
    """
    Calculates the number of full months between two dates.

    Args:
        d1 (date): The more recent date.
        d2 (date): The earlier date.

    Returns:
        int: The number of months between d1 and d2.
    """
    return (d1.year - d2.year)*12 + d1.month - d2.month

select_text = _('Select' + '...')

def get_industries(search = False):
    """
    Retrieves a list of industry choices for use in forms or filters.

    Args:
        search (bool): If True, includes an 'All' option instead of the default 
                       'Select...' prompt. Defaults to False.

    Returns:
        list of tuple: A list of (value, label) pairs for industries.
                       Includes a default option followed by all available industries.
    """
    choices = [('0', _('No applications'))]
    try:
        industries = Industry.objects.all()
        if industries.count() > 0:
            if search:
                choices = [('-1', 'All')]
            else:
                choices = [('-1', select_text)]
            for industry in industries:
                choices.append([industry.id, industry.name])
    except:
        pass
    return choices

def get_notice_period():
    """
    Returns a predefined list of notice period options.

    Returns:
        list of tuple: A list of (value, label) pairs representing notice periods.
    """
    choices = [('0',"Any"),('1',"Immediate"),('2',"1 Week"),('3',"2 Weeks"),('4',"3 Weeks"),('5',"1 Month"),('6',"2 Months"),('7',"3 Months"),('8',"4 Months"),('9',"5 Months"),('10',"6 Months")]
    return choices

# def get_areas(industry=None, search=False):
#     """
#     Get industries selections based on the industry parameter.
#     """
#     if search:
#         choices = [('-1', _('All'))]
#     else:
#         if industry:
#             choices = [('-1', select_text)]
#         else:
#             choices = [('-1', _('Select an Industry first'))]
#     try:
#         if industry and industry > 0:
#             if type(industry) != Industry:
#                 industry = Industry.objects.get(pk=int(industry))
#             areas = industry.area_set.all()
#             if areas.count() > 0:
#                 for area in areas:
#                     choices.append([area.id, area.name])
#     except:
#         pass
#     return choices


def get_degrees():
    """
    Retrieves a list of available academic degrees.

    Returns:
        list of list: A list of [id, name] pairs for each degree.
                      If retrieval fails, returns an empty list.
    """
    choices = []
    try:
        degrees = Degree.objects.all()
        for degree in degrees:
            choices.append([degree.id, degree.name])
    except:
        pass
    return choices


def get_employment_types():
    """
    Retrieves a list of available employment types.

    Returns:
        list of list: A list of [id, name] pairs for each employment type.
                      If retrieval fails, returns an empty list.
    """
    # choices = [('-1', _('Anyone'))]
    choices = []
    try:
        employment_types = Employment_Type.objects.all()
        for employment_type in employment_types:
            choices.append([employment_type.id, employment_type.name])
    except:
        pass
    return choices


def get_email(email=None):
    """
    Returns a list of email choices for form selection.

    Args:
        email (str, optional): A default email address to include as the first option. Defaults to None.

    Returns:
        list of tuple: A list containing a tuple of the default email and a choice for "Other".
    """
    choices = [(False, email), (True, _('Other'))]
    return choices


class VacancyForm(forms.ModelForm):
    """ Form creating vacancies """
    """
    This form handles the full set of fields required to publish a job vacancy,
    including job role, description, job type, salary, location, industry,
    qualifications, and various configurations related to publishing and applications.

    Fields:
        - employment (CharField): Job role title.
        - description (CharField): Description of the job role using a rich text editor.
        - employmentType (ChoiceField): Type of employment (e.g., full-time, part-time).
        - salaryType (ModelChoiceField): Type of salary.
        - min_salary / max_salary (CharField): Salary range.
        - nationality (ModelChoiceField): Required nationality for the position.
        - state / city (CharField): Location information.
        - currency (ModelChoiceField): Currency for salary.
        - gender (ModelChoiceField): Preferred gender, optional.
        - degree (ModelChoiceField): Minimum required degree, optional.
        - industry (ModelChoiceField): Related industry.
        - function (CharField): Department or functional area.
        - notice_period (ChoiceField): Maximum accepted notice period.
        - skills (CharField): Required skills, comma-separated.
        - minEmploymentExperience / maxEmploymentExperience (ModelChoiceField): Experience range.
        - confidential (BooleanField): Hide company contact details.
        - data_contact (BooleanField): Include contact details with candidate matches.
        - questions (BooleanField): Allow candidates to ask questions.
        - another_email (ChoiceField): Email field or option to use a different one.
        - email (EmailField): Email to contact.
        - postulate (BooleanField): Allow applications for this vacancy.
        - pub_after (BooleanField): Enable future publication date.
        - pub_date / unpub_date (CharField): Publish and unpublish dates.
        - min_age / max_age (ChoiceField): Age range for candidates.
        - hiring_date (DateField): Expected joining date.
        - vacancies_number (IntegerField): Number of openings.
        - public_cvs (BooleanField): Allow public CVs for applicants.
        - ban (BooleanField): Exclude archived candidates.
        - ban_period (ChoiceField): Duration for which banned candidates stay banned.
        - ban_all (ChoiceField): Whether to apply ban to all candidates or current.
        - has_custom_form (BooleanField): Attach a custom form to the vacancy.
        - form_template (ModelChoiceField): Template to use for custom form.
    """
    initial_country = get_initial_country()
    countries = Country.objects.filter(~Q(continent='AF') & ~Q(continent='AN') & ~Q(continent='AS') & ~Q(continent='OC'))
    countries = Country.objects.all()
    industries = Industry.objects.all()
    currencies = Currency.objects.all()
    jm_duration = False
    jm_template = False
    update = False
    employment = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Job Role'),
                                      'class': 'form-control'}),
        max_length=70,
        min_length=2,
        error_messages={'required': _("Enter the job role required")},
        label=_("Job Role")
    )
    description = forms.CharField(
        widget= CKEditorWidget(attrs={'placeholder': _('Description of post'),'class':"form-control"}),
        required=True,
        min_length=100,
        error_messages={'required': _("Enter the description of post")},
        label=_("Description")
    )
    employmentType = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=get_employment_types(),
        required=True,
        label=_('Job Type'),
    )
    salaryType = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Salary_Type.objects.all(),
        required=True,
        label=_('Salary'),
        empty_label=None,
    )
    min_salary = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Minimum Salary'),
                                      'class': 'form-control'}),
        label=_("Minimum Salary"),
        required=False,
        max_length=50,
        error_messages={
            'invalid': _('Enter a valid number, without commas or points')
        }
    )
    max_salary = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Maximum Salary'),
                                      'class': 'form-control'}),
        label=_("Maximum Salary"),
        required=False,
        max_length=50,
        error_messages={
            'invalid': _('Enter a valid number, without commas or points')
        }
    )
    nationality = forms.ModelChoiceField(
        queryset=countries,
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=True,
        label=_('Nationality'),
        initial=initial_country
    )
    state = forms.CharField(
        # queryset=states,
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your State"}),
        # empty_label=select_text,
        max_length=30,
        min_length=2,
        required=True,
        label=_('State'),
        error_messages={
            'required': _("State is required")},
    )
    city = forms.CharField(
        # choices=get_municipals(None),
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your City"}),
        max_length=30,
        min_length=2,
        label=_('City'),
        required=True,
        error_messages={
            'required': _("City is required")},
    )
    currency = forms.ModelChoiceField(
        queryset = currencies,
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=select_text,
        required=False,
        label=_('Currency'),
        error_messages={
            'required': _('Select a currency')
        }
    )
    gender = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Gender.objects.all(),
        required=False,
        label=_('Gender'),
        empty_label='Any',
    )
    degree = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Degree.objects.all(),
        required=False,
        label=_('Education'),
        empty_label='Any',
    )
    industry = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        # choices=get_industries(),
        queryset = industries,
        label=_('Industry'),
    )
    function = forms.CharField(
        # queryset=states,
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "e.g.: Software Development, Admin, Marketing"}),
        # empty_label=select_text,
        max_length=50,
        min_length=2,
        required=True,
        label=_('Function'),
        error_messages={
            'required': _("Function is required")},
    )
    notice_period = forms.ChoiceField(
        # queryset=states,
        widget=forms.Select(attrs={'class': "form-control",'placeholder': "Enter maximum accepted Notice Period"}),
        # empty_label=select_text,
        choices=get_notice_period(),
        required=True,
        label=_('Notice Period'),
        error_messages={'required': _("Notice Period is required")}
    )
    skills = forms.CharField(
        # queryset=states,
        widget=forms.TextInput(attrs={'class': "form-control no-dropdown",'placeholder': "Enter comma seperated skills"}),
        # empty_label=select_text,
        max_length=200,
        min_length=2,
        required=True,
        label=_('Skills'),
        error_messages={'required':_('Skills are required')}
    )
    # area = forms.ChoiceField(
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     choices=get_areas(industry=0),
    #     label=_(u'Area'),
    #     error_messages={'invalid_choice': _(u'Area invalid')}
    # )
    minEmploymentExperience = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Employment_Experience.objects.all(),
        required=False,
        label=_('Experience required'),
        empty_label=None,
    )
    maxEmploymentExperience = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Employment_Experience.objects.all(),
        required=False,
        label=_('Experience required'),
        empty_label=None,
    )
    confidential = forms.BooleanField(
        label=_('Show matches with Contact details?'),
        widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
        initial=False,
        required=False,
    )
    data_contact = forms.BooleanField(
        label=_('Show matches with Contact details?'),
        widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
        initial=True,
        required=False,
    )
    questions = forms.BooleanField(
        label=_('Allow Question?'),
        widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
        initial=True,
        required=False,
    )
    another_email = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=get_email(),
        label=_('E-mail'),
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _('Email'),
                                      'class': 'form-control'}),
        required=False,
        error_messages={'required': _("Enter a contact email")},
        label=_("E-mail to contact")
    )
    postulate = forms.BooleanField(
        label=_('Allow aplications?'),
        widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
        # widget=forms.CheckboxInput(attrs={'class': "flipswitch-cb"}),
        initial=True,
        required=False,
    )
    pub_after = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
        required=False,
        label=_('Post a future data?'),
        initial=False
    )
    pub_date = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Date of publication'), 'class': "form-control"}),
        label=None,
        required=False,
    )
    unpub_date = forms.CharField(
        required=False,
    )
    min_age = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=get_ages(),
        required=False,
        label=_('Minimum Age'),
        initial='1'
    )
    max_age = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=get_ages(),
        required=False,
        label=_('Maximum Age'),
        initial='1'
    )
    hiring_date = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': _('No date of joining'),
                                      'class': 'form-control'}),
        label=None,
        required=False,
    )
    vacancies_number = forms.IntegerField(
        widget=forms.TextInput(attrs={'placeholder': _('No. of vacancies'),
                                      'class': 'form-control'}),
        label=_("No. of vacancies"),
        required=True,
        initial='1',
        min_value=1,
        max_value=1000,
        error_messages={
            'invalid': _('Enter a valid amount'),
            'required': _('Enter the number of vacancies')
        }
    )
    public_cvs = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "js-switch"}),
                                   required=False,
                                   label=_('Allow public CVs?'),
                                   initial=True)
    ban = forms.BooleanField(
        label=_('Ban Archived Candidates?'),
        widget = forms.CheckboxInput(attrs={'class': "js-switch"}),
        initial = False,
        required = False    
    )

    ban_period = forms.ChoiceField(
        widget = forms.Select(attrs={'class':"ml5 mr5"}),
        choices=get_ban_period(),
        required = False,
        label = _('Ban for'),
        initial='1'
    )
    ban_all = forms.ChoiceField(
        widget = forms.RadioSelect(attrs={'class':'form-control'}),
        choices = [('0','All'),('1','this')],
        required = False,
        label=_('Ban All?'),
        initial = False
    )
    has_custom_form = forms.BooleanField(
        label=_('Add Custom Form?'),
        widget = forms.CheckboxInput(attrs={'class': "js-switch"}),
        initial = False,
        required = False    
    )
    form_template = forms.ModelChoiceField(
        label = "Template",
        widget = forms.Select(attrs={'class':"form-control"}),
        queryset = Template.objects.none(),
        empty_label = "No Template",
        error_messages={
            'required': _('Select a Template or Create a new one to use Custom Forms')
        }
    )


    def __init__(self, *args, **kwargs):
        """
        Initializes the form with dynamic behavior based on the provided kwargs.

        Keyword Args:
            industry_selected (int): ID of the selected industry.
            company_email (str): The company's email address.
            another_email (bool or str): Whether to require an alternative email.
            update (bool): Whether this is an update form.
            company (Company): The company object to check service features.
            industry (int): Initial value for the industry field.
            state (str): Initial value for the state field.
            city (str): Initial value for the city field.
            nationality (int): Initial value for the nationality field.
        """
        # state_selected = kwargs.pop('state_selected', None)
        industry_selected = kwargs.pop('industry_selected', None)
        company_email = kwargs.pop('company_email', None)
        another_email = kwargs.pop('another_email', False)
        update = kwargs.pop('update', None)
        company = kwargs.pop('company', None)
        initial_industry = kwargs.pop('industry', None)
        initial_state = kwargs.pop('state', '')
        initial_city = kwargs.pop('city', '')
        initial_nationality = kwargs.pop('nationality', None)

        # salaryType = kwargs.pop('data', None)

        super(VacancyForm, self).__init__(*args, **kwargs)

        if update:
            self.update = True
            # self.fields['municipal'].choices = get_municipals(state_selected)
            # self.fields['area'].choices = get_areas(industry_selected)
            # del self.fields['pub_after']
            # del self.fields['pub_date']
        if initial_industry:
            self.fields['industry'].initial = initial_industry

        if initial_city:
            self.fields['city'].initial = initial_city
        if initial_state:
            self.fields['state'].initial = initial_state
        if initial_nationality:
            self.fields['nationality'].initial = initial_nationality
        if self.is_bound:
            # self.fields['municipal'].choices = get_municipals(state_selected)
            # self.fields['area'].choices = get_areas(industry_selected)

            if another_email == 'True':
                self.fields['email'].required = True
            elif another_email == 'False':
                self.fields['email'].required = False
            self.fields['email'].required = False
            if self.data.get('has_custom_form', False):
                self.fields['form_template'].required = True
            else:
                self.fields['form_template'].required = False
        self.fields['another_email'].choices = get_email(company_email)
        if company and company.check_service('JM_DURATION'):
            self.jm_duration = True
        if company and company.check_service('JM_CUSTOM_APPLICATION_FORM'):
            self.fields['form_template'].required = False
            self.jm_template = True
            self.fields['form_template'].queryset = company.template_set.all()

    def clean_form_template(self):
        """
        Validates the custom form template field based on company service settings.

        Returns:
            form_template instance or None
        """

        if not self.data.get('has_custom_form') or not self.jm_template:
            return None
        return self.cleaned_data.get('form_template')

    def clean_maxEmploymentExperience(self):
        """
        Validates the maximum experience field ensuring it's greater than minimum experience.

        Raises:
            ValidationError: If maximum experience is not properly set.
        
        Returns:
            maxExperience instance
        """
        minExperience = self.cleaned_data.get('minEmploymentExperience',None)
        maxExperience = self.cleaned_data.get('maxEmploymentExperience',None)

        if minExperience:
            if maxExperience:
                if (maxExperience.id == 2 and minExperience.id==1) or (not maxExperience.id == 1 and maxExperience.id < minExperience.id):
                    raise forms.ValidationError('Please Enter a Higher Period than the minimum provided',code="invalid")
                else:
                    return maxExperience
            else:
                raise forms.ValidationError('Please enter the max range as well',code='required')
        else:
            return None


    def clean_employmentType(self):
        """
        Validates and returns the selected employment type.

        Raises:
            ValidationError: If employment type is invalid.

        Returns:
            Employment_Type instance
        """
        try:
            employmentType_id = int(self.cleaned_data.get('employmentType'))
            if employmentType_id == -1:
                return None
            employment_types = get_employment_types()
            choices = []
            for employment_type in employment_types:
                choices.append(int(employment_type[0]))
            if employmentType_id not in choices:
                raise forms.ValidationError(_('Select a valid type of employment'))
            employment_type = Employment_Type.objects.get(pk=employmentType_id)
        except:
            raise forms.ValidationError(_('Select a valid type of employment'))
        return employment_type

    # def clean_industry(self):
        #     industry_id = int(self.cleaned_data.get('industry'))
        #     invalid_industry = _(u'Industry invalid')
        #     if industry_id == -1:
        #         raise forms.ValidationError(_(u'Select a Industry'))
        #     if industry_id == 0:
        #         raise forms.ValidationError(invalid_industry)
        #     try:
        #         industries = get_industries()
        #         choices = []
        #         for industry in industries:
        #             choices.append(int(industry[0]))
        #         if industry_id not in choices:
        #             raise forms.ValidationError(invalid_industry)
        #         industry = None
        #         if industry_id > 0:
        #             industry = Industry.objects.get(pk = industry_id)
        #     except Industry.DoesNotExist:
        #         raise forms.ValidationError(invalid_industry)
        #     return industry

    def clean_area(self):
        """
        Validates the area based on the selected industry.

        Raises:
            ValidationError: If area is not selected or invalid.

        Returns:
            Area instance
        """
        industry = self.cleaned_data.get('industry')
        area_id = int(self.cleaned_data.get('area'))
        error = _('Area invalid')
        if not industry and area_id == -1:
            raise forms.ValidationError(_('You must first select an Industry'))
        if area_id == -1:
            raise forms.ValidationError(_('Select an Area'))
        try:
            choices = []
            try:
                areas = industry.area_set.all()
                for area in areas:
                    choices.append(area.id)
            except:
                raise forms.ValidationError(error)
            if area_id not in choices:
                raise forms.ValidationError(error)
            area = Area.objects.get(pk=area_id)
        except Area.DoesNotExist:
            raise forms.ValidationError(error)
        return area

    def clean_pub_date(self):
        """
        Validates the publication start date for job posting.

        Raises:
            ValidationError: If the date is not in the future or missing.

        Returns:
            datetime.date
        """
        import pdb
        pub_after = self.cleaned_data['pub_after']
        pub_date = date.today()
        if self.jm_duration and pub_after:
            if not self.data.get('pub_date'):
                raise forms.ValidationError(_('Select a publishing period'))
            pub_date = self.data.get('pub_date')
            pub_date, end_date = pub_date.split('-')
            pub_date = datetime.strptime(pub_date.strip(),'%m/%d/%Y').date()
            self.unpub_date = datetime.strptime(end_date.strip(),'%m/%d/%Y').date()
            if pub_date < date.today():
                raise forms.ValidationError(_('Select a future date'))
            return pub_date
        else:
            try:
                return self.instance.pub_date
            except:
                return None

    def clean_unpub_date(self):
        """
        Validates the publication end date for job posting.

        Raises:
            ValidationError: If unpublishing date is not valid.

        Returns:
            datetime.date
        """
        pub_after = self.cleaned_data['pub_after']
        unpub_date = date.today() + timedelta(days=29)
        if self.jm_duration and pub_after:
            if not self.data.get('pub_date'):
                raise forms.ValidationError(_('Select a publishing period'))
            pub_date = self.data.get('pub_date')
            pub_date, end_date = pub_date.split('-')
            unpub_date = datetime.strptime(end_date.strip(),'%m/%d/%Y').date()
            if unpub_date < self.cleaned_data.get('pub_date'):
                raise forms.ValidationError(_('Select a future date'))
            return unpub_date
        else:
            try:
                return self.instance.unpub_date
            except:
                return None

    # def clean_state(self):
        #     # state_id = int(self.cleaned_data.get('state'))
        #     error = _(u'The state you selected is invalid')
        #     if state_id < 0:
        #         raise forms.ValidationError(_(u'Select a State'))
        #     try:
        #         country = self.initial_country
        #         # try:
        #         #     states = country.state_set.all()
        #         # except:
        #         #     states = []
        #         choices = [0]
        #         # for state in states:
        #         #     choices.append(state.id)
        #         # if state_id not in choices:
        #         #     raise forms.ValidationError(error)
        #         # state = State.objects.get(pk = state_id)
        #     except State.DoesNotExist:
        #         raise forms.ValidationError(error)
        #     return state

    # def clean_municipal(self):
        #     municipal_id = int(self.cleaned_data.get('municipal'))
        #     if municipal_id < 0:
        #         raise forms.ValidationError(_(u'Select a City'))
        #     if municipal_id == 0:
        #         return None
        #     try:
        #         choices = [0]
        #         try:
        #             state = self.cleaned_data.get('state')
        #             state_id = state.pk
        #             state = State.objects.get(id=state_id)
        #             municipals = state.municipal_set.all()
        #             for municipal in municipals:
        #                 choices.append(municipal.id)
        #         except:
        #             return None
        #         if municipal_id not in choices:
        #             raise forms.ValidationError(_(u'Select a City'))
        #         municipal = Municipal.objects.get(pk = municipal_id)
        #     except Municipal.DoesNotExist:
        #         raise forms.ValidationError(_(u'The city you selected is invalid'))
        #     return municipal

    def clean_currency(self):
        """
        Validates the currency field if salary type requires it.

        Raises:
            ValidationError: If required currency is missing.

        Returns:
            Currency instance or None
        """
        salaryType = self.cleaned_data.get('salaryType')
        dsalaryType = self.data['salaryType']
        if salaryType and salaryType == '6':
            required = True
        elif dsalaryType and dsalaryType == '6':
            required = True
        else:
            required = False
        if required:
            currency_id = self.data['currency']
            try:
                currency = Currency.objects.get(pk = int(currency_id))
            except:
                raise forms.ValidationError('Select a Currency')
        else:
            return None
        return currency        

    def clean_min_salary(self):
        """
        Validates minimum salary if salary type is fixed.

        Raises:
            ValidationError: If minimum salary is required and missing.

        Returns:
            str or None
        """
        salaryType = self.cleaned_data.get('salaryType')
        #     print(salaryType.codename)
        try:
            min_salary = (None if self.data['min_salary'] == '' else self.data['min_salary'])
        except:
            min_salary = None
        if salaryType and salaryType.codename == 'fixed' and not min_salary:
            raise ValidationError('This field is required',code='required')
        return min_salary
        #         max_salary = self.data['max_salary']
        #         if not max_salary:
        #             max_salary = 0
        #         if not min_salary:
        #             raise forms.ValidationError(_(u'Enter a valid amount'))
        #         # if min_salary <= 60:
        #         #     raise forms.ValidationError(_(u'Enter an amount greater than 60'))
        #         # elif min_salary >= 500000:
        #         #     raise forms.ValidationError(_(u'Enter an amount less than 500000'))
        #         try:
        #             max_salary = int(max_salary)
        #         except:
        #             raise forms.ValidationError(_(u'Entry Invalid'))
        #         if int(min_salary) > int(max_salary):
        #             raise forms.ValidationError(_(u'The minimum wage is higher than the maximum'))
        #     else:
        #         min_salary = None

        #     return min_salary

    def clean_max_salary(self):
        """
        Returns the maximum salary value.

        Returns:
            str or None
        """
        #     salaryType = self.cleaned_data.get('salaryType')
        #     print(salaryType.codename)
        #     if salaryType and salaryType.codename == 'fixed':
        try:
            max_salary = (None if self.data['max_salary'] == '' else self.data['max_salary'])
        except:
            max_salary = None
        #         try:
        #             max_salary = int(max_salary)
        #         except:
        #             raise forms.ValidationError(_(u'Enter a valid amount'))
        #         if not max_salary:
        #             raise forms.ValidationError(_(u'Enter a valid amount'))
        #         # if max_salary <= 60:
        #         #     raise forms.ValidationError(_(u'Enter an amount greater than 60'))
        #         # elif max_salary >= 500000:
        #         #     raise forms.ValidationError(_(u'Enter an amount less than 500000'))
        #     else:
        #         max_salary = None

        return max_salary

    def clean_min_age(self):
        """
        Validates minimum age ensuring it's within accepted range and not greater than max age.

        Raises:
            ValidationError: If age is outside the range or inconsistent.

        Returns:
            int or None
        """

        # try:
        min_age = int(1 if self.cleaned_data.get('min_age') is None else self.cleaned_data.get('min_age'))
        # except:
            # min_age = 1
        # try:
        max_age = int(1 if self.data['max_age'] is None else self.data['max_age'])
        # except:
            # max_age = 1
        # if min_age == 0 and max_age == 0:
        #     return None
        if min_age == 1:
            return None
        # if min_age == 0 and max_age != 0:
        #     raise forms.ValidationError(_(u'Choose a minimum age'))
        if min_age < 18 or min_age > 65:
                raise forms.ValidationError(_('Choose an age within the range of 18 to 65 year'))
        if min_age > max_age:
            raise forms.ValidationError(_('The minimum age is older than the maximum age, please select a valid age.'))
        return self.cleaned_data.get('min_age')

    def clean_max_age(self):
        """
        Validates maximum age ensuring it's within accepted range and not less than min age.

        Raises:
            ValidationError: If age is outside the range.

        Returns:
            int or None
        """
        # try:
        min_age = int(1 if self.data['min_age'] is None else self.data['min_age'])
        # except:
        # min_age = 1
        # try:
        max_age = int(1 if self.cleaned_data.get('max_age') is None else self.cleaned_data.get('max_age'))
        # except:
            # max_age = 1
        if max_age == 1:
            return None
        # if min_age == 0 and max_age == 0:
        #     return None
        # if min_age != 0 and max_age == 0:
        #     raise forms.ValidationError(_(u'Choose a maximum age'))
        if max_age < 18 or max_age > 65:
                raise forms.ValidationError(_('Choose an age within the range of 18 to 65 years'))
        return max_age

    def clean_hiring_date(self):
        """
        Validates that the hiring date is in the future.

        Raises:
            ValidationError: If date is in the past or today.

        Returns:
            datetime.date or None
        """
        hiring_date = self.cleaned_data.get('hiring_date')
        if hiring_date:
            if hiring_date <= date.today():
                raise forms.ValidationError(_('Select a future date'))
        if not hiring_date or hiring_date == '':
            return None
        return hiring_date

    def clean_vacancies_number(self):
        """
        Validates the number of vacancies is a valid integer.

        Raises:
            ValidationError: If input is not a valid integer.

        Returns:
            int
        """
        try:
            vacancies_number = (None if self.data['vacancies_number'] == '' else int(self.data['vacancies_number']))
        except:
            raise forms.ValidationError(_('Enter a valid vacancies'))
        return vacancies_number

    class Meta:
        model = Vacancy
        exclude = ('company', 'user', 'active', 'add_date', 'end_date', 'last_modified', 'status', 'seen', 'editing_date', 'applications', 'recruiters')


# Start Search Vacancies Area
def get_vacancy_pubdates_search():
    """
    Returns a list of choices for publication date filtering in vacancy search.

    Returns:
    list of tuples: Each tuple represents a (value, label) pair for the form dropdown.
    """
    choices = [('0', 'No applications')]
    vacancy_pubdates = PubDate_Search.objects.all()
    if vacancy_pubdates.count() > 0:
        choices = [('-1', 'Anyone')]
        for vacancy_pubdate in vacancy_pubdates:
            choices.append([vacancy_pubdate.id, vacancy_pubdate.name])
    return choices


class BasicSearchVacancyForm(forms.Form):
    """
    Form for basic vacancy search by criteria like state, industry, publication date, etc.

    Fields:
        - state (ChoiceField): Selectable state, validated against the initial country.
        - industry (ChoiceField): Selectable industry list.
        - vacancyPubDateSearch (ModelChoiceField): Filter by publication date.
        - search (CharField): Keywords to filter vacancies.
        - gender (ModelChoiceField): Candidate's gender.
        - degree (ModelChoiceField): Candidate's level of education.

    Methods:
        - __init__: Handles dynamic behavior like selected industry.
        - clean_state: Validates that selected state exists in the initial country.
        - clean_industry: Validates selected industry.
        - clean_vacancyPubDateSearch: Validates publication date.
        - clean_gender: Validates gender.
        - clean_degree: Validates degree.
    """
    initial_country = get_initial_country()

    countries = Country.objects.filter(~Q(continent='AF') & ~Q(continent='AN') & ~Q(continent='AS') & ~Q(continent='OC'))
    countries = Country.objects.all()
    state = forms.ChoiceField(
        # choices= get_states(initial_country, search_vacancy=True),
        label=_('State'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    industry = forms.ChoiceField(
        choices=get_industries(search=True),
        label=_('Industry'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    # area = forms.ChoiceField(
    #     choices=get_areas(industry=0, search=True),
    #     label=_(u'Area'),
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    # )
    vacancyPubDateSearch = forms.ModelChoiceField(
        queryset=PubDate_Search.objects.all(),
        label=_('Publication Date'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None,
    )
    search = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Keywords: System Management, Assistant'),
                                      'class': 'form-control'}),
        max_length=10,
        min_length=3,
        required=False,
        label=_("Search words"),
    )
    gender = forms.ModelChoiceField(
        queryset=Gender.objects.all(),
        empty_label=None,
        required=False,
        label=_('Gender'),
    )
    degree = forms.ModelChoiceField(
        queryset=Degree.objects.all(),
        required=True,
        empty_label=None,
        label=_('Level of education'),
    )

    def __init__(self, vacancy=None, *args, **kwargs):
        """
        Initialize the form with optional vacancy and industry_selected parameters.

        Args:
            vacancy (Vacancy, optional): A Vacancy instance for context (default is None).
            *args: Variable length argument list for parent form.
            **kwargs: Keyword arguments; may include 'industry_selected' to preselect an industry.

        Notes:
            The 'industry_selected' kwarg is popped out and can be used to filter form fields.
            Calls the superclass initializer with remaining args and kwargs.
        """
        industry_selected = kwargs.pop('industry_selected', None)
        super(BasicSearchVacancyForm, self).__init__(*args, **kwargs)

        # if self.is_bound:
        #     self.fields['area'].choices = get_areas(industry_selected)

    def clean_state(self):
        """
        Validate the 'state' field to ensure the selected state belongs to the initial country.

        Returns:
            State instance or None if no state selected.

        Raises:
            forms.ValidationError: If the selected state is invalid or does not exist.
        """
        state_id = int(self.data['state'])
        if state_id < 0:
            return None
        try:
            country = self.initial_country
            try:
                states = country.state_set.all()
            except:
                states = []
            choices = [0]
            for state in states:
                choices.append(state.id)
            if state_id not in choices:
                raise forms.ValidationError(_('The state you selected is invalid'))
            state = State.objects.get(pk = state_id)
        except State.DoesNotExist:
            raise forms.ValidationError(_('The state you selected is invalid'))
        return state

    def clean_industry(self):
        """
        Validate the 'industry' field to ensure the selected industry exists in the choices.

        Returns:
            Industry instance or None if no industry selected.

        Raises:
            forms.ValidationError: If the selected industry is invalid or does not exist.
        """
        industry_id = int(self.data['industry'])
        error = ('Industry invalid')
        if industry_id == -1:
            return None
        try:
            industries = []
            try:
                industries = get_industries(search=True)
            except:
                pass
            choices = []
            industry = None
            for industry in industries:
                choices.append(int(industry[0]))
            if industry_id not in choices:
                raise forms.ValidationError(error)
            if industry_id > 0:
                industry = Industry.objects.get(pk = industry_id)
        except Industry.DoesNotExist:
            raise forms.ValidationError(error)
        return industry

    # def clean_area(self):
    #     industry = self.cleaned_data.get('industry')
    #     area_id = int(self.data['area'])
    #     error = _(u'Area invalid')
    #     if not industry:
    #         return None
    #     if area_id == -1:
    #         return None
    #     try:
    #         choices = []
    #         try:
    #             areas = industry.area_set.all()
    #             for area in areas:
    #                 choices.append(area.id)
    #         except:
    #             raise forms.ValidationError(error)
    #         if area_id not in choices:
    #             raise forms.ValidationError(error)
    #         area = Area.objects.get(pk=area_id)
    #     except Area.DoesNotExist:
    #         raise forms.ValidationError(error)
    #     return area

    def clean_vacancyPubDateSearch(self):
        """
        Validate the 'vacancyPubDateSearch' field to ensure the selected publication date is valid.

        Returns:
            PubDate_Search instance or None.

        Raises:
            forms.ValidationError: If the publication date is not valid.
        """
        try:
            pubDate = self.cleaned_data.get('vacancyPubDateSearch')
        except PubDate_Search.DoesNotExist:
            raise forms.ValidationError(_('The Publication Date is not valid'))
        return pubDate

    def clean_gender(self):
        """
        Validate the 'gender' field to ensure the selected gender exists.

        Returns:
            Gender instance or None.

        Raises:
            forms.ValidationError: If the selected gender is not valid.
        """
        try:
            gender = self.cleaned_data.get('gender')
        except Gender.DoesNotExist:
            raise forms.ValidationError(_('The Gender you selected is not valid'))
        return gender

    def clean_degree(self):
        """
        Validate the 'degree' field to ensure the selected education level exists.

        Returns:
            Degree instance or None.

        Raises:
            forms.ValidationError: If the selected degree is not valid.
        """
        try:
            degree = self.cleaned_data.get('degree')
        except Degree.DoesNotExist:
            raise forms.ValidationError(_('The Level of education you selected is not valid'))
        return degree


class QuestionVacancyForm(forms.ModelForm):
    """
    Form for users to submit a question or comment regarding a vacancy.

    Fields:
        - question (CharField): Textarea input for a user's question (min 20, max 200 chars).

    Methods:
        - save: Creates a Question instance linked to the vacancy and user.

    Meta:
        model: Question
        fields: ('question',)
    """
    question = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _('Enter your question or comment'),
                                     'class': "form-control",
                                     'rows': 3}),
        max_length=200,
        min_length=20,
        required=True,
        label=_('Question'),
    )

    def save(self, vacancy=None, user=None, question=None):
        """
        Create and save a new Question instance with the given vacancy, user, and question text.

        Args:
            vacancy (Vacancy, optional): The Vacancy instance related to the question.
            user (User, optional): The User instance who asked the question.
            question (str, optional): The text content of the question.

        Returns:
            Question: The newly created Question object.
        """
        Question.objects.create(vacancy=vacancy, user=user, question=question)

    class Meta:
        model = Question
        fields = ('question',)


class VacancyFileForm(forms.ModelForm):
    """
    Form for uploading multiple supporting files to a vacancy application.

    Fields:
        - file (FileField): Allows upload of up to 3 files with specific formats.

    Methods:
        - validate_number_files(files): Ensures file count does not exceed maximum.
        - clean_file: Validates size, extension, and sanitizes filename.
        - save: Saves file instance and associates it with the vacancy and random number.

    Meta:
        model: Vacancy_Files
        fields: ['file']
    """
    max_megas = 5
    max_files = 3
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                #'multiple': True,
                'accept': 'image/jpeg,'
                          'image/bmp,'
                          'image/png,'
                          'application/pdf,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
        ),
        required=False
    )

    def validate_number_files(self, files):
        """
        Validate that the number of uploaded files does not exceed the allowed maximum.

        Args:
            files (int): The number of files being uploaded.

        Adds a form error if the number of files exceeds the maximum allowed.
        """
        if files > self.max_files:
            msg = _('You can only upload upto %s files') % self.max_files
            self.add_error('file', msg)
        pass

    def clean_file(self):
        """
        Clean and validate the uploaded file.

        Checks file size against the maximum allowed size,
        validates the file extension,
        and normalizes the filename by removing accents and special characters.

        Returns:
            File: The cleaned file object if valid, otherwise None.

        Raises:
            ValidationError: If the file size exceeds the allowed limit or
                            if the file extension is not supported.
        """
        file = self.cleaned_data['file']

        if file:
            if file.size > self.max_megas * 1024000:
                raise ValidationError(_('The filesie of %s is greater than %s MB') % (file.name, self.max_megas))

            valid_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'doc', 'docx', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']
            extension = os.path.splitext(file.name)[1]
            extension = extension[1:].lower()
            if extension not in valid_extensions:
                raise ValidationError('Tipo de archivo no soportado.')

            # Accentsand other special characters of the name of the image are removed
            name = ''.join((c for c in unicodedata.normalize('NFD', file.name) if unicodedata.category(c) != 'Mn'))
            file.name = name

            return file

        else:
            return None

    def save(self, vacancy=None, random_number=None, commit=True):
        """
        Save the VacancyFileForm instance with optional vacancy and random number assignments.

        Args:
            vacancy (Vacancy, optional): The Vacancy instance to associate with the file.
            random_number (int or str, optional): A random number to assign to the file instance.
            commit (bool): Whether to commit the save operation immediately.

        Returns:
            Vacancy_Files: The saved Vacancy_Files model instance.
        """
        instance = super(VacancyFileForm, self).save(commit=False)
        instance.vacancy = vacancy
        instance.random_number = random_number
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Vacancy_Files
        fields = ['file']


class Public_FilesForm(forms.Form):
    """
    Public form for job applicants to submit their name, email, brief description, and CV.

    Fields:
        - full_name (CharField): Applicant's full name.
        - email (EmailField): Email, checked for existing account or company bans.
        - description (CharField): Optional candidate introduction (max 500 chars).
        - file (FileField): Required CV upload (PDF/DOC/DOCX).

    Methods:
        - __init__: Accepts vacancy ID for use in validation.
        - validate_number_files(files): Ensures file count within allowed limit.
        - clean_file: Validates file size, extension, and sanitizes filename.
        - clean_email: Validates against existing users and ban logic.
        - save: Raises error; saving is handled externally.
    """
    max_megas = 5
    max_files = 1
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Full name'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        required=True,
        label=_('Full name'),
        error_messages={'required': _("Enter your name")},
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _('Email'),
                                      'class': "form-control"}),
        max_length=75,
        required=True,
        label=_('Email'),
        error_messages={'required': _("Enter your Email")},
    )
    # salary = forms.IntegerField(
    #     widget=forms.TextInput(attrs={'placeholder': _(u'salary'),
    #                                   'class': 'form-control'}),
    #     required=False,
    #     max_value=200000,
    #     min_value=1000,
    #     label=_(u'salary '),
    #     error_messages={'required': _(u"Enter your desired salary"),
    #                     'invalid': _(u"Enter a valid number, without commas and points"),
    #                     'min_value': _(u'Enter a valid amount greater than 1000'),
    #                     'max_value': _(u'Enter a valid amount less than 200000')},
    # )
    # age = forms.IntegerField(
    #     widget=forms.TextInput(attrs={'placeholder': _(u'Age'),
    #                                   'class': 'form-control'}),
    #     required=False,
    #     max_value=65,
    #     min_value=18,
    #     label=_(u'Age'),
    #     error_messages={'required': _(u"Enter your Age"),
    #                     'invalid': _(u'Enter a valid age between 18 and 65 years'),
    #                     'min_value': _(u'The minimum age to apply is 18 years'),
    #                     'max_value': _(u'The maximum age to apply is 65 years')},
    # )
    description = forms.CharField(
        widget= forms.Textarea(attrs={'placeholder': _('Description. (Max 500 caracters)'),
                                     'class': 'form-control',
                                     'rows': 3}),
        required=False,
        min_length=0,
        max_length=500,
        label=_("Briefly explain to the recruiter why you are interested in this job opening, as well as your level of education, "
                "experience in the field and your outstanding qualities and skills for this work"),
        error_messages={'required': _("Make the recruiter interested in you")}
    )
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept':
                      'application/pdf,'
                      'application/msword,'
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
            }
        ),
        required=True,
        label=_('Upload your CV/Portfolio in Word or PDF format (max %sMB)' % str(max_megas)),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the Public_FilesForm.

        Extracts 'v_id' from kwargs to set the vacancy ID associated with the form.

        Args:
            *args: Variable length argument list.
            **kwargs: Keyword arguments containing 'v_id' for vacancy ID.
        """
        self.vacancy_id = kwargs.pop('v_id', None)
        super(Public_FilesForm, self).__init__(*args, **kwargs)

    def validate_number_files(self, files):
        """
        Validate the number of files uploaded against the maximum allowed.

        Args:
            files (int): The number of files being uploaded.

        Adds an error to the form if the file count exceeds the maximum allowed.
        """
        if files > self.max_files:
            msg = _('You can only upload upto %s files') % self.max_files
            self.add_error('file', msg)
        pass

    def clean_file(self):
        """
        Clean and validate the uploaded file.

        Checks if the file size exceeds the maximum allowed size.
        Validates the file extension against allowed types (doc, docx, pdf).
        Normalizes the file name by removing accents and special characters.

        Returns:
            File: The cleaned file object if valid, otherwise None.

        Raises:
            ValidationError: If the file size is too large or if the file type is unsupported.
        """
        file = self.cleaned_data['file']
        if file:
            if file.size > self.max_megas * 1024000:
                raise ValidationError(_('The filesize of %s is greater than %s MB') % (file.name, self.max_megas))

            valid_extensions = ['doc', 'docx', 'pdf']
            extension = os.path.splitext(file.name)[1]
            extension = extension[1:].lower()
            if extension not in valid_extensions:
                raise ValidationError('Only Word or PDF files are supported')

            # Accents and other special charcaters in the filename are removed
            name = ''.join((c for c in unicodedata.normalize('NFD', file.name) if unicodedata.category(c) != 'Mn'))
            file.name = name

            return file

        else:
            return None

    def clean_email(self):
        """
        Validate the email field.

        Checks if an account with the email already exists.
        Verifies if the email is banned from applying to the company or specific vacancy functions.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If the email belongs to an existing account or is banned by the company.
        """
        e_mail = self.cleaned_data['email']
        user = User.objects.filter(email = e_mail)
        if user:
            raise ValidationError('An account with this email exists. Please use the account to avail 1 click login and other features such as tracking your Application Status and Withdraw Application.')
        else:
            vacancy = Vacancy.objects.get(id=self.vacancy_id)
            company = vacancy.company
            ban1 = Ban.objects.filter(email__iexact = e_mail, company = company, ban_function = None)
            ban2 = Ban.objects.filter(email__iexact = e_mail, company = company, ban_function__iexact = vacancy.function)
            if e_mail in company.ban_list.split(','):
                raise ValidationError('You have been prohibited from appying to this company\'s job openings')
            elif ban1:
                ban1 = ban1[0]
                if diff_month(datetime.now(), ban1.add_date) < ban1.duration:
                    raise ValidationError('You have been restricted from applying to this company\'s open positions within %s months of your last application' % ban1.duration)
            elif ban2:
                ban2 = ban2[0]
                if diff_month(datetime.now(), ban2.add_date) < ban2.duration:
                    raise ValidationError('You have been restricted from applying to this company\'s open positions within %s months of your last application' % ban2.duration)
            return e_mail
    # class Meta:
    #     model = Postulate
    #     fields = ['vacancy','first_name','candidate.public_email','description','file']

    def save(self):
        """
        Raise an error to prevent saving via this method.

        Raises:
            ValueError: Always raised to indicate saving is not supported through this form method.
        """
        raise ValueError()


class Public_Files_OnlyForm(forms.Form):
    """
    Form for uploading a CV/portfolio file without requiring other applicant details.

    Fields:
        - file (FileField): Required upload in Word or PDF format.

    Methods:
        - __init__: Accepts vacancy ID.
        - validate_number_files(files): Ensures file count does not exceed maximum.
        - clean_file: Validates file size, extension, and filename sanitization.
        - save: Raises error; intended to be overridden or handled externally.
    """
    max_megas = 5
    max_files = 1
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept':
                      'application/pdf,'
                      'application/msword,'
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
            }
        ),
        required=True,
        label=_('Upload your CV/Portfolio in Word or PDF format (max %sMB)' % str(max_megas)),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the Public_Files_OnlyForm.

        Extracts 'v_id' from kwargs to set the vacancy ID associated with the form.

        Args:
            *args: Variable length argument list.
            **kwargs: Keyword arguments containing 'v_id' for vacancy ID.
        """
        self.vacancy_id = kwargs.pop('v_id', None)
        super(Public_Files_OnlyForm, self).__init__(*args, **kwargs)

    def validate_number_files(self, files):
        """
        Validate the number of files uploaded against the maximum allowed.

        Args:
            files (int): The number of files being uploaded.

        Adds an error to the form if the file count exceeds the maximum allowed.
        """
        if files > self.max_files:
            msg = _('You can only upload upto %s files') % self.max_files
            self.add_error('file', msg)
        pass

    def clean_file(self):
        """
        Clean and validate the uploaded file.

        Checks if the file size exceeds the maximum allowed size.
        Validates the file extension against allowed types (doc, docx, pdf).
        Normalizes the file name by removing accents and special characters.

        Returns:
            File: The cleaned file object if valid, otherwise None.

        Raises:
            ValidationError: If the file size is too large or if the file type is unsupported.
        """
        file = self.cleaned_data['file']
        if file:
            if file.size > self.max_megas * 1024000:
                raise ValidationError(_('The filesize of %s is greater than %s MB') % (file.name, self.max_megas))

            valid_extensions = ['doc', 'docx', 'pdf']
            extension = os.path.splitext(file.name)[1]
            extension = extension[1:].lower()
            if extension not in valid_extensions:
                raise ValidationError('Only Word or PDF files are supported')

            # Accents and other special charcaters in the filename are removed
            name = ''.join((c for c in unicodedata.normalize('NFD', file.name) if unicodedata.category(c) != 'Mn'))
            file.name = name

            return file

        else:
            return None

    def save(self):
        """
        Prevent saving of the form instance through this method.

        Raises:
            ValueError: Always raised to indicate saving is not supported via this form.
        """
        raise ValueError()

