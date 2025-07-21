# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from django import forms
from django.db.models import Q
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField as PNF
from candidates.models import Academic_Area, Academic_Status, get_degrees, Language
from common.forms import get_states, get_initial_country
from common.models import Country, User, Gender, Degree
# from companies.custom_fields import MXRFCField_Custom
from companies.models import Company_Industry, Company, RecruiterInvitation
from upload_logos.widgets import AjaxClearableFileInput
from vacancies.models import get_ages
from TRM.settings import LOGO_COMPANY_DEFAULT
from ckeditor.widgets import CKEditorWidget

select_text = _('Select' + '...')
select_option = _("Select an option")
initial_country = get_initial_country()  


def get_company_industries():
    """
    Fetch a list of company industries for use as form choices.

    Returns:
        list: A list of tuples representing industry choices with id and name.
              Returns [('0', 'No options')] if no industries are found or on error.
    """
    choices = [('0', 'No options')]
    try:
        industries = Company_Industry.objects.all()
        if industries.count() > 0:
            choices = [('-1', 'Select...')]
            for industry in industries:
                choices.append([industry.id, industry.name])
    except:
        print("Error in get_company_industries()")
    return choices


# def get_company_areas(industry=None):
#     choices = [('0', 'Select an Industry first')]
#     if industry:
#         if type(industry) == long:
#             industry = Company_Industry.objects.get(pk= int(industry))
#         areas = industry.company_area_set.all()
#         if areas.count() > 0:
#             choices = [('-1', 'Select...')]
#             for area in areas:
#                 choices.append([area.id, area.name])
#     return choices
class CompanyLogoForm(forms.ModelForm):
    """
    Form for uploading and validating a company's logo image.

    Attributes:
        default_logo (str): Path or URL of the default company logo.

    Fields:
        logo (ImageField): Image upload field accepting various image formats.
    """
    default_logo = LOGO_COMPANY_DEFAULT

    logo = forms.ImageField(widget=forms.FileInput(attrs={'class': "form-control text-center", "accept": "image/*"}), required=True)

    def __init__(self, *args, **kwargs):
        """
        Initialize the CompanyLogoForm.
        """
        super(CompanyLogoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Company
        fields = ('logo',)

    def clean_logo(self):
        """
        Validate the uploaded logo image for format and size constraints.

        Returns:
            Uploaded image if valid, else the default logo.

        Raises:
            forms.ValidationError: If image format is unsupported or size exceeds 5MB.
        """
        from PIL import Image
        image = self.cleaned_data.get('logo', None)
        if image:
            img = Image.open(image)
            if img.format.lower() not in ['jpeg', 'pjpeg', 'png', 'jpg', 'gif', 'mpo']:
                # raise ValueError()
                raise forms.ValidationError(_('You can only use images with extensions JPG, JPEG, PNG or GIF'))
            #validate file size
            if len(image) > (5 * 1024 * 1024):
                raise forms.ValidationError(_('The selected image is too large (Max 5MB)'))
        else:
            return self.default_logo
        return image


class CompanyForm(forms.ModelForm):
    """
    Form for creating and updating Company details.

    Fields include company name, social/legal name, industry, employee count, description,
    phone, URLs, social media, email, logo, nationality, state, and city.

    Includes custom validation methods for Facebook, Twitter, logo, and related fields.
    """
    default_logo = LOGO_COMPANY_DEFAULT
    # countries = Country.objects.filter(~Q(continent='AF') & ~Q(continent='AN') & ~Q(continent='AS') & ~Q(continent='OC'))
    countries = Country.objects.all()
    industries = Company_Industry.objects.all()
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Brandname of your Company'),
                                      'class': "form-control"}),
        max_length=50,
        min_length=2,
        error_messages={'required': _("Enter the name of your company")},
    )
    social_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Legal name of your Company'),
                                      'class': "form-control"}),
        max_length=100,
        min_length=4,
        error_messages={'required': _("Enter the company's Legal name")},
    )
    # rfc = MXRFCField_Custom(
    #     widget=forms.TextInput(attrs={'placeholder': 'RFC',
    #                                   'class': "form-control"}),
    # )
    industry = forms.ModelChoiceField(
        # choices=get_company_industries(),
        queryset = industries,
        widget=forms.Select(attrs={'class': "form-control"}),
        required=True,
    )
    # function = forms.CharField(
    #     widget = forms.TextInput(attrs={'placeholder':_(u'Industry Function'), 'class':"form-control"}),
    #     max_length=100,
    #     min_length=4,
    #     required=True,
    #     error_messages={'required':_(u"Enter the Company's Function")},
    # )
    no_of_employees = forms.IntegerField(
        widget=forms.TextInput(attrs={'placeholder': _('No of Employees'),
                                      'class': "form-control"},
                               ),
        min_value=1,
        max_value=9999,
        required=False,
    )
    # area = forms.ChoiceField(
    #     choices=get_company_areas(None),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    # )
    description = forms.CharField(
        widget= CKEditorWidget(attrs={'placeholder': _('Enter a description of the company\'s activities.'),'class':"form-control"}),
        # max_length=500,
        min_length=30,
        label=_("Description"),
        error_messages={
            'required': _("Enter a description of the activities in your company."),
        },
    )
    phone = PNF(
        max_length=16,
        min_length=10,
        error_messages={
            'invalid': _("Enter a valid 10 dg=igit phone"),
            'required': _('Enter your business phone'),
            'min_length': _("Enter a valid 10 digit phone"),
            'max_length': _("Enter a valid 10 digit phone"),
        },
        widget=forms.TextInput(attrs={'placeholder': _('10 digit business phone'),
                                      'class': "form-control"}),
    )
    url = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': _('Website of the Company'),
                                      'class': "form-control"}),
        max_length=150,
        min_length=9,
        required=False
    )
    facebook = forms.URLField(
        widget=forms.TextInput(attrs={'placeholder': _('www.facebook.com/account'),
                                      'class': "form-control"}),
        max_length=150,
        required=False
    )
    twitter = forms.RegexField(
        widget=forms.TextInput(attrs={'placeholder': _('@username'),
                                      'class': "form-control"}),
        regex=r'^[\w@]+$',
        max_length=16,
        min_length=3,
        error_messages={
            'invalid': _("Enter a valid Twitter user."),
        },
        required=False
    )
    company_email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _('General Business Email'),
                                      'class': "form-control"}),
        required=True,
    )
    # contact_phone = PhoneNumberField(
    #     min_length=10,
    #     max_length=12,
    #     error_messages={
    #         'invalid': _(u"Enter a valid 10 digit phone"),
    #         'required': _(u'Enter your pone number'),
    #         'min_length': _(u"Enter a valid 10 digit phone"),
    #         'max_length': _(u"Enter a valid 10 digit phone"),
    #     },
    #     widget=forms.TextInput(attrs={'placeholder': _(u'10 digit Phone'),
    #                                   'class': "form-control"})
    # )
    # contact_phone_ext = forms.IntegerField(
    #     widget=forms.TextInput(attrs={'placeholder': _(u'Ext'),
    #                                   'class': "form-control"},
    #                            ),
    #     min_value=1,
    #     max_value=9999,
    #     required=False,
    # )
    logo = forms.ImageField(widget=forms.FileInput(attrs={'class': "form-control text-center", "accept": "image/bmp, image/gif, image/png, image/jpeg"}), required=False)
    # to_company = forms.CharField(
    #     widget=forms.TextInput(attrs={'placeholder': _(u'User recommendation'),
    #                                   'class': "form-control"}),
    #     max_length=30,
    #     required=False,
    # )
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
        min_length=4,
        required=True,
        label=_('State'),
        error_messages={
            'required': _("State is required")},
    )
    city = forms.CharField(
        # choices=get_municipals(None),
        widget=forms.TextInput(attrs={'class': "form-control",'placeholder': "Enter your City"}),
        max_length=30,
        min_length=4,
        label=_('City'),
        required=True,
        error_messages={
            'required': _("City is required")},
    )

    def __init__(self, *args, **kwargs):
        """Initialize the CompanyForm."""
        change_profile = False
        area_selected = kwargs.pop('area_selected', None)
        industry_selected = kwargs.pop('industry_selected', None)
        country_selected = kwargs.pop('country_selected', None)
        try:
            if kwargs.pop('change_profile'):
                change_profile = True
        except:
            pass
        super(CompanyForm, self).__init__(*args, **kwargs)

        # if change_profile:
        #     self.fields['industry'].choices = get_company_industries()
            # self.fields['country'].choices = get_company_countries()
            # self.fields['area'].choices = get_company_areas(industry_selected)

        # if self.is_bound:
            # if area_selected == -1:
                # industry_selected = None
            # self.fields['area'].choices = get_company_areas(industry_selected)

    # def clean_industry(self):
    #     invalid_industry = _(u'The industry you selected is invalid')
    #     try:
    #         industry_id = int(self.cleaned_data.get('industry').id)
    #     except:
    #         raise forms.ValidationError(invalid_industry)
        # if industry_id <= 0:
        #     raise forms.ValidationError(_(u'Select an Industry'))
        # try:
        #     try:
        #         industry = Company_Industry.objects.get(pk = industry_id)
        #     except:
        #         industry = None
        # except Company_Industry.DoesNotExist:
        #     raise forms.ValidationError(invalid_industry)
        # return industry

    # def clean_area(self):
    #     invalid_area = _(u'Invalid Area')
    #     try:
    #         area_id = int(self.cleaned_data.get('area'))
    #     except:
    #         raise forms.ValidationError(invalid_area)
    #     if area_id < 0:
    #         raise forms.ValidationError(invalid_area)
    #     if area_id == 0:
    #         raise forms.ValidationError(_(u'You must first select an Industry'))
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

    # def clean_rfc(self):
    #     if not self.cleaned_data.get('rfc'):
    #         raise forms.ValidationError(_(u'Enter your RFC'))
    #     return self.cleaned_data['rfc']

    def clean_facebook(self):
        """Validate the Facebook URL field."""
        facebook_error = _('Enter a valid Facebook page')
        if not self.cleaned_data.get('facebook'):
            return None
        facebook = self.cleaned_data.get('facebook')
        if 'facebook.com/' not in facebook.lower():
            raise forms.ValidationError(facebook_error)
        if len(facebook) < 26:
            raise forms.ValidationError(facebook_error)
        return facebook

    def clean_twitter(self):
        """Validate the Twitter username field."""
        twitter_error = _('Enter a valid Twitter user')
        if not self.cleaned_data.get('twitter'):
            return None
        twitter = self.cleaned_data.get('twitter')
        if twitter.count('@') > 1:
            raise forms.ValidationError(twitter_error)
        if twitter.count('@') > 0:
            if not twitter.startswith('@'):
                raise forms.ValidationError(twitter_error)
            twitter = twitter.replace('@', '')
        return twitter

    def clean_logo(self):
        """Validate the uploaded company logo image."""
        from PIL import Image
        image = self.cleaned_data.get('logo', None)
        if image:
            img = Image.open(image)
            if img.format.lower() not in ['jpeg', 'pjpeg', 'png', 'jpg', 'gif', 'mpo']:
                raise forms.ValidationError(_('You can only use images with extensions JPG, JPEG, PNG or GIF'))
            #validate file size
            if len(image) > (5 * 1024 * 1024):
                raise forms.ValidationError(_('The selected image is too large (Max 5MB)'))
        else:
            return self.default_logo
        return image

    def clean_to_company(self):
        to_company_user = self.cleaned_data['to_company']
        if to_company_user:
            try:
                user = User.objects.get(username__iexact=to_company_user)
                to_company = Company.objects.get(user=user)
            except:
                to_company = None
            if not to_company:
                raise forms.ValidationError(_("Incorrect username, please check"))
        else:
            return None
        return to_company

    class Meta:
        model = Company
        exclude = ('user', 'address', 'subdomain', 'site_template', 'above_jobs', 'below_jobs')

class MemberInviteForm(forms.ModelForm):
    """
    Form for inviting a new member via email.

    Fields:
        email (EmailField): Email address to invite.

    Validates that the email is not already registered or previously invited.
    """
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control no-br", 'placeholder': "Email"}), required=True)
    def __init__(self, *args, **kwargs):
        """Initialize the MemberInviteForm."""
        super(MemberInviteForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Validate that the email is unique and not already invited.

        Returns:
            str: Validated email.

        Raises:
            forms.ValidationError: If email is already registered or invited.
        """
        email = self.cleaned_data.get('email',None)
        if email:
            users = User.objects.filter(email = email)
            if users:
                raise forms.ValidationError('A user with the same email already exists','Invalid')
        else:
            return None
        return email

    class Meta:
        model = RecruiterInvitation
        fields = ('email',)

# def get_academic_careers(area=None):
#     choices = []
#     if area:
#         if type(area) == long:
#             area = Academic_Area.objects.get(pk= int(area))
#         areas = area.careers.all()
#         if areas.count() > 0:
#             for area in areas:
#                 choices.append([area.id, area.name])
#     return choices


def get_academic_status():
    """
    Retrieve a list of academic status choices from the database.

    Returns:
        list: A list of [id, name] pairs for each Academic_Status entry.
              Returns an empty list if none found or on error.
    """
    choices = []
    try:
        status = Academic_Status.objects.all()
        if status.count() > 0:
            for stat in status:
                choices.append([stat.id, stat.name])
    except:
        print("Error in get_academic_status()")
    return choices


# def get_municipals(state=None):
#     """
#     Get municipal selections based on the state parameter.
#     """
#     choices = []
#     if state:
#         if type(state) == long or type(state) == int:
#             state = State.objects.get(pk= int(state))
#         municipals = state.municipal_set.all()
#         if municipals.count() > 0:
#             for municipal in municipals:
#                 choices.append([municipal.id, municipal.name])
#     return choices


class SearchCvForm(forms.Form):
    """ Formulario para busqueda de Curricula """
    """Form for searching CVs with various filters including degree, status, area,
    gender, age range, travel availability, and residence availability."""
    degree = forms.MultipleChoiceField(
        choices=get_degrees(select=False),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
        label=_('Level of Study'),
    )
    status = forms.MultipleChoiceField(
        choices=get_academic_status(),
        required=False,
        label=_('Status'),
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    )
    area = forms.ModelChoiceField(
        queryset=Academic_Area.objects.all(),
        empty_label=select_text,
        required=False,
        label=_('Area'),
        widget=forms.Select(attrs={'class': "form-control"}),
        error_messages={'required': select_option},
    )
    # career = forms.MultipleChoiceField(
    #     choices=get_academic_careers(None),
    #     required=False,
    #     widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    #     label=_(u'Career'),
    # )
    # state = forms.ChoiceField(
    #     choices= get_states(initial_country, search_vacancy=True),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    #     label=_(u'State')
    # )
    # municipal = forms.MultipleChoiceField(
    #     choices=get_municipals(None),
    #     required=False,
    #     label=_(u'City'),
    #     widget=forms.SelectMultiple(),
    # )
    gender = forms.ModelChoiceField(
        queryset=Gender.objects.all(),
        widget=forms.Select(attrs={'class': "form-control"}),
        empty_label=None,
        required=False,
        label=_('gender')
    )
    min_age = forms.ChoiceField(
        choices=get_ages(indistinct=False),
        required=True,
        label=_('Min Age'),
    )
    max_age = forms.ChoiceField(
        choices=get_ages(indistinct=False),
        required=True,
        label=_('Max Age'),
        initial='65',
    )
    # language_1 = forms.ModelChoiceField(
    #     queryset=Language.objects.all(),
    #     empty_label=select_text,
    #     required=False,
    #     label=_(u'Language 1'),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    # )
    # level_1 = forms.ModelChoiceField(
    #     queryset=Language_Level.objects.all(),
    #     empty_label=_(u'Indistinct'),
    #     required=False,
    #     label=_(u'Minimu Level of Language 1'),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    # )
    # language_2 = forms.ModelChoiceField(
    #     queryset=Language.objects.all(),
    #     empty_label=select_text,
    #     required=False,
    #     label=_(u'Language 2'),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    # )
    # level_2 = forms.ModelChoiceField(
    #     queryset=Language_Level.objects.all(),
    #     empty_label=_(u'Indistinct'),
    #     required=False,
    #     label=_(u'Minimu Level of Language 2'),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    # )
    travel = forms.BooleanField(
        label=_('Availability to Travel'),
        required=False,
    )
    residence = forms.BooleanField(
        label=_('Avalability to change residence'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with optional parameters for pre-selecting area and state.

        Args:
            area_selected (int or None): ID of the selected academic area.
            state_selected (int or None): ID of the selected state.

        The form dynamically updates career and municipal choices if bound.
        """
        area_selected = kwargs.pop('area_selected', None)
        state_selected = kwargs.pop('state_selected', None)
        super(SearchCvForm, self).__init__(*args, **kwargs)

        if self.is_bound:
            self.fields['career'].choices = get_academic_careers(area_selected)
            self.fields['municipal'].choices = get_municipals(state_selected)

    def clean_degree(self):
        """
        Validate the degree field by fetching Degree model instances.

        Returns:
            list: List of Degree instances corresponding to selected degree IDs.

        Raises:
            forms.ValidationError: If any selected degree ID is invalid.
        """
        invalid_degree = _('Level of Study is invalid')
        degrees = None
        try:
            degree_ids = self.cleaned_data.get('degree', None)
            if degree_ids:
                degrees = []
                for degree_id in degree_ids:
                    degree = Degree.objects.get(id=degree_id)
                    degrees.append(degree)
        except:
            raise forms.ValidationError(invalid_degree)
        return degrees

    def clean_status(self):
        """
        Validate the status field by fetching Academic_Status model instances.

        Returns:
            list: List of Academic_Status instances corresponding to selected IDs.

        Raises:
            forms.ValidationError: If any selected status ID is invalid.
        """
        invalid_status = _('Status is invalid')
        status = None
        try:
            status_ids = self.cleaned_data.get('status', None)
            if status_ids:
                status = []
                for status_id in status_ids:
                    status_obj = Academic_Status.objects.get(id=status_id)
                    status.append(status_obj)
        except:
            raise forms.ValidationError(invalid_status)
        return status

    # def clean_state(self):
    #     state_id = int(self.cleaned_data.get('state'))
    #     if state_id < 0:
    #         return None
    #     try:
    #         try:
    #             states = initial_country.state_set.all()
    #         except:
    #             states = []
    #         choices = [0]
    #         for state in states:
    #             choices.append(state.id)
    #         if state_id not in choices:
    #             raise forms.ValidationError(_(u'Select a State'))
    #         state = State.objects.get(pk = state_id)
    #     except State.DoesNotExist:
    #         raise forms.ValidationError(_(u'The state you selected is invalid'))
    #     return state

    # def clean_municipal(self):
    #     invalid_municipal = _(u'City is invalid')
    #     municipals = None
    #     try:
    #         municipal_ids = self.cleaned_data.get('municipal', None)
    #         if municipal_ids:
    #             municipals = []
    #             for municipal_id in municipal_ids:
    #                 municipal_obj = Municipal.objects.get(id=municipal_id)
    #                 municipals.append(municipal_obj)
    #     except:
    #         raise forms.ValidationError(invalid_municipal)
    #     return municipals

    # def clean_career(self):
    #     invalid_career = _(u'Area is invalid')
    #     careers = None
    #     try:
    #         careers_ids = self.cleaned_data.get('career', None)
    #         if careers_ids:
    #             careers = []
    #             for career_id in careers_ids:
    #                 career = Academic_Career.objects.get(id=career_id)
    #                 careers.append(career)
    #     except:
    #         raise forms.ValidationError(invalid_career)
        return careers

    def clean_min_age(self):
        """
        Validate that min_age is within valid range and less than or equal to max_age.

        Returns:
            int: Validated minimum age.

        Raises:
            forms.ValidationError: If min_age is out of range or greater than max_age.
        """
        min_age = int(self.cleaned_data.get('min_age'))
        max_age = int(self.data['max_age'])
        if min_age < 18 or min_age > 65:
                raise forms.ValidationError(_('Choose an age within the range of 18 to 65 years'))
        if min_age > max_age != 0:
            raise forms.ValidationError(_('The min age is greater than max age, please select a valid age.'))
        return min_age

    def clean_max_age(self):
        """
        Validate that max_age is within valid range.

        Returns:
            int: Validated maximum age.

        Raises:
            forms.ValidationError: If max_age is out of the allowed range.
        """
        max_age = int(self.cleaned_data.get('max_age'))
        if max_age < 18 or max_age > 65:
                raise forms.ValidationError(_('Choose an age within the range of 18 to 65 years'))
        return max_age

    # def clean_language_1(self):
    #     language = self.cleaned_data.get('language_1')
    #     level = self.data['level_1']
    #     if level and not language:
    #         raise forms.ValidationError(_(u'Choose the first Language'))
    #     elif not language and not level:
    #         return None
    #     return language

    # def clean_level_1(self):
    #     language = self.cleaned_data.get('language_1')
    #     level = self.cleaned_data.get('level_1')
    #     print('Level %s' % level)
    #     levels = None
    #     if language and not level:
    #         levels = Language_Level.objects.all()
    #     elif language and level:
    #         codename = level.codename
    #         if codename == 'basic':
    #             levels = Language_Level.objects.all()
    #         if codename == 'intermediate':
    #             levels = Language_Level.objects.filter(codename__in=['intermediate', 'advanced', 'native'])
    #         if codename == 'advanced':
    #             levels = Language_Level.objects.filter(codename__in=['advanced', 'native'])
    #         if codename == 'native':
    #             levels = Language_Level.objects.filter(codename='native')
    #     elif not language and not level:
    #         return None
    #     return levels

    # def clean_language_2(self):
    #     language = self.cleaned_data.get('language_2')
    #     level = self.data['level_2']
    #     if level and not language:
    #         raise forms.ValidationError(_(u'Choose your second Language'))
    #     elif not language and not level:
    #         return None
    #     return language

    # def clean_level_2(self):
        # language = self.cleaned_data.get('language_2')
        # level = self.cleaned_data.get('level_2')
        # levels = None
        # if language and not level:
        #     levels = Language_Level.objects.all()
        # elif language and level:
        #     codename = level.codename
        #     if codename == 'basic':
        #         levels = Language_Level.objects.all()
        #     if codename == 'intermediate':
        #         levels = Language_Level.objects.filter(codename__in=['intermediate', 'advanced', 'native'])
        #     if codename == 'advanced':
        #         levels = Language_Level.objects.filter(codename__in=['advanced', 'native'])
        #     if codename == 'native':
        #         levels = Language_Level.objects.filter(codename='native')
        # elif not language and not level:
        #     return None
        # return levels
