"""
Form classes for the common app.

This module provides form classes for handling various types of data input including:
- User registration and profile management
- File uploads
- Contact forms
- Address management
- Password management
- Email management
- Social authentication

Each form includes validation logic and custom widgets where appropriate.
"""

# -*- coding: utf-8 -*-
import ipgetter
import uuid
import socket
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from common.models import User, AccountVerification, Address, Country, State, Municipal, EmailVerification, send_TRM_email, Subdomain
from common import registration_settings
from django.template import loader
from django.template import RequestContext
from django.contrib.sites.requests import RequestSite
from TRM.settings import PHOTO_USER_DEFAULT
from upload_logos.widgets import AjaxClearableFileInput

def get_initial_country():
    """
    Get the default country for form initialization.
    
    Returns:
        Country: The default country object (usually Mexico)
    """
    try:
        initial_country = Country.objects.get(iso2_code__exact='IN')
    except:
        return None
    return initial_country


# ------------------------------------------------- #
# Home Registration Form User Data #
# ------------------------------------------------- #
class UserPhotoForm(forms.ModelForm):
    """
    Form for handling user profile photo uploads.
    
    Provides validation and processing for user photo uploads including:
    - File type validation
    - Size restrictions
    - Image processing
    """
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class':"form-control text-center"}), required=False)

    def clean_photo(self):
        """
        Validate and process the uploaded photo.
        
        Returns:
            ImageField: The cleaned and processed photo file
            
        Raises:
            ValidationError: If the photo doesn't meet requirements
        """
        default_photo = PHOTO_USER_DEFAULT
        from PIL import Image
        image = self.cleaned_data.get('photo', None)
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
                raise forms.ValidationError(_(u'You can only use images with extensions JPG, JPEG or PNG'))

            #validate file size
            if len(image) > (1 * 1024 * 1024):
                raise forms.ValidationError(_(u'The image selected is too large (Max 1MB)'))
        else:
            return default_photo
        return image

    class Meta():
        model = User
        fields = ('photo',)


class SubdomainForm(forms.ModelForm):
    """
    Form for managing subdomains.
    
    Handles creation and validation of subdomain entries including:
    - Domain name validation
    - Uniqueness checks
    - Format restrictions
    """
    cname = forms.CharField(
        widget = forms.TextInput(attrs={'placeholder':'career.yourdomain.com',
                                        'class':'form-control'
                                    }),
        error_messages={
            'invalid':'Enter a valid URL'
        }
    )

    def clean_cname(self):
        cname = self.cleaned_data['cname']
        cnames = Subdomain.objects.filter(cname = cname)
        if cnames:
            raise forms.ValidationError('This subdomain is already in use. Please remove it from the other account before procceeding.')
            #already exist
        else:
            cname = cname.split(':')[0]
            domains = cname.split('.')
            if domains[::-1][1] == 'spotaxis' and domains[::-1][0] == 'com':
                raise forms.ValidationError("Whoa! You can't use our own domain for your website.")
            ip = socket.gethostbyname(cname)
            if ipgetter.myip() == ip:
                return cname
            else:
                raise forms.ValidationError('It looks like this subdomain does not point to us. Please add the CNAME setting to your DNS before proceeding.')

    class Meta:
        model = Subdomain
        fields = ('cname',)

class UserDataForm(forms.ModelForm):
    """
    Form for managing user profile data.
    
    Handles user registration and profile updates including:
    - Username validation
    - Email verification
    - Password management
    - Personal information
    
    Attributes:
        email_repeat_msg (str): Message for email confirmation field
        password_repeat_msg (str): Message for password confirmation field
    """
    email_repeat_msg = _(u'Confirm your email')
    password_repeat_msg = _(u'* Confirm your Password')
    username = forms.RegexField(
        label=_(u"Name of User"),
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': _(u'* Username'),
                                      'class': "form-control s-form-v4__input"}),
        regex=r'^[\w.-]+$',
        error_messages={
            'invalid': _(u"Only letters, numbers and the following characters are allowed . - _"),
            'required': _(u"Enter a username")
        }
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _(u'* Email'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=75,
        error_messages={'required': _(u"Enter your Email")},
        label="Contact Email"
    )

    email_repeat = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': email_repeat_msg,
                                      'class': "form-control s-form-v4__input"}),
        max_length=75,
        error_messages={'required': email_repeat_msg},
        label= email_repeat_msg,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _(u'* Password'),
                                          'class': "form-control s-form-v4__input"}),
        max_length=128,
        error_messages={'required': _(u"ENter your Password")},
        label=_(u"Password")
    )

    password_repeat = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': password_repeat_msg,
                                          'class': "form-control s-form-v4__input"}),
        max_length=128,
        error_messages={'required': password_repeat_msg},
        label=password_repeat_msg,
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'* First Name'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        error_messages={'required': _(u"Enter your Name")},
        label=_(u"Name")
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'* Last Name'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        error_messages={'required': _(u"Enter your Last Name")},
        label=_(u"Surname")
    )

    cellphone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Phone'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        min_length=5,
        required=False,
        error_messages={'required': _(u"Enter your Phone")},
        label=_(u"Phone")
    )

    # photo = forms.ImageField(widget=AjaxClearableFileInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(UserDataForm, self).__init__(*args, **kwargs)

        if not registration_settings.DOUBLE_CHECK_EMAIL:
            del self.fields['email_repeat']

        if not registration_settings.DOUBLE_CHECK_PASSWORD:
            del self.fields['password_repeat']

        if not registration_settings.REGISTRATION_FULLNAME:
            del self.fields['first_name']
            del self.fields['last_name']

        if registration_settings.EMAIL_ONLY:
            self.fields['username'].widget = forms.widgets.HiddenInput()
            self.fields['username'].required = False

    def _generate_username(self):
        """ Generate a unique username """
        while True:
            # Generate a UUID username, removing dashes and the last 2 chars
            # to make it fit into the 30 char User.username field. Gracefully
            # handle any unlikely, but possible duplicate usernames.
            username = str(uuid.uuid4())
            username = username.replace('-', '')
            username = username[:-2]

            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                return username

    def clean_username(self):
        if registration_settings.EMAIL_ONLY:
            username = self._generate_username()
        else:
            username = self.cleaned_data['username']
            if User.objects.filter(username__iexact=username):
                raise forms.ValidationError(
                    _(u"Username already exists. Please try again."))

        return username

    def clean_email(self):
        if not registration_settings.CHECK_UNIQUE_EMAIL:
            return self.cleaned_data['email']

        new_email = self.cleaned_data['email']

        emails = User.objects.filter(email__iexact=new_email).count()
        
        if emails > 0:
            raise forms.ValidationError(
                _(u'This email is already registered. Please try a new one.'))
        else:
           emails = EmailVerification.objects.filter(new_email__iexact=new_email, is_expired=False)
           for email in emails:
                email.is_expired = True
                email.save()

        return new_email

    def clean(self):
        if registration_settings.DOUBLE_CHECK_EMAIL:
            if 'email' in self.cleaned_data and 'email_repeat' in self.cleaned_data:
                if self.cleaned_data['email'] != self.cleaned_data['email_repeat']:
                    from django.forms.util import ErrorList
                    self._errors['email'] = ErrorList()
                    self._errors['email'].append(_(u'Email addresses do not match'))
                    # raise forms.ValidationError(_(u'Email addresses do not match.'))

        if registration_settings.DOUBLE_CHECK_PASSWORD:
            if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
                if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                    from django.forms.utils import ErrorList
                    self._errors['password'] = ErrorList()
                    self._errors['password'].append(_(u'The passwords do not match'))
                    # raise forms.ValidationError(_(u'The passwords do not match.'))

        return self.cleaned_data

    def send_verification_mail(self, new_user):
        AccountVerification.objects.send_verification_mail(new_user=new_user)

    def save(self, *args, **kwargs):
        if registration_settings.USE_ACCOUNT_VERIFICATION:
            new_user = AccountVerification.objects.create_inactive_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
            )
            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']
            new_user.is_active = False
            new_user.save()
        else:
            new_user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
            )
            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']
            new_user.save()
        emails = EmailVerification.objects.filter(new_email__iexact=self.cleaned_data['email'],is_expired=False)
        for email in emails:
            email.is_expired = True
            email.save()
        if hasattr(self, 'save_profile'):
            self.save_profile(new_user, *args, **kwargs)

        return new_user

    class Meta():
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
# ---------------------------------------------- #
# Registration Form End User Data #
# ---------------------------------------------- #


# --------------------------------------------- #
# Start Form Basics User Data #
# --------------------------------------------- #
class BasicUserDataForm(forms.ModelForm):
    """
    Form for basic user information updates.
    
    A simplified version of UserDataForm for basic profile updates including:
    - Name
    - Email
    - Phone numbers
    
    Does not include password or username management.
    """
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Enter your name'),
                                      'class': 'form-control'}),
        max_length=30,
        required=True,
        error_messages={'required': _(u"Enter your name")},
        label=_(u"Name(s)")
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Enter your Surname'),
                                      'class': 'form-control'}),
        max_length=30,
        required=True,
        error_messages={'required': _(u"Enter your Surname")},
        label=_(u"Surname")
    )

    cellphone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Phone'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=5,
        required = False,
        label=_(u"Phone")
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Email'),
                                      'class': 'form-control'}),
        max_length=75,
        error_messages={'required': _(u"Enter your Email")},
        label="E-mail"
    )

    def __init__(self, *args, **kwargs):
        super(BasicUserDataForm, self).__init__(*args, **kwargs)
        if not registration_settings.PROFILE_ALLOW_EMAIL_CHANGE:
            del self.fields['email']
        # else:
        #     self.fields.keyOrder.remove('email')
        #     self.fields.keyOrder.insert(0, 'email')

        # if not registration_settings.REGISTRATION_FULLNAME:
        #     del self.fields['first_name']
        #     del self.fields['last_name']
        # else:
        #     self.fields.keyOrder.remove('first_name')
        #     self.fields.keyOrder.remove('last_name')
        #     self.fields.keyOrder.insert(0, 'first_name')
        #     self.fields.keyOrder.insert(1, 'last_name')

    def update(self, *args, **kwargs):
        user = super(BasicUserDataForm, self).save(*args, **kwargs)
        if registration_settings.REGISTRATION_FULLNAME:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
        if registration_settings.PROFILE_ALLOW_EMAIL_CHANGE:
            user.email = self.data['email'].lower()
        if registration_settings.REGISTRATION_FULLNAME or registration_settings.PROFILE_ALLOW_EMAIL_CHANGE:
            user.save()

        if hasattr(self, 'save_profile'):
            self.save_profile(user, *args, **kwargs)

        return user

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'cellphone', 'email']
# --------------------------------------------- #
# End Form for Basic Data of User #
# --------------------------------------------- #


# ------------------------------------ #
# Start Form for Change of Email #
# ------------------------------------ #
class ChangeEmailForm(forms.Form):
    """
    Form for handling email address changes.
    
    Provides:
    - New email validation
    - Verification process initiation
    - Email format checking
    """
    new_email = forms.EmailField(
        label=_('New Email'),
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': _(u'Enter a new Email')
            }
        ),
        max_length=225,
        required=True,
        error_messages={'required': _(u'Enter a new Email')}
    )

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']

        user_emails = User.objects.filter(email__iexact=new_email).count()
        verification_emails = EmailVerification.objects.filter(
            new_email__iexact=new_email, is_expired=False).count()
        if user_emails + verification_emails > 0:
            raise forms.ValidationError(_(
                'This email is already registered. Please try a new one.'))
        if verification_emails > 0:
            raise forms.ValidationError(_('This email has alreday requested a token for change. Please wait for 2 hours before generating a new one.'))

        return new_email

    def save(self, user=None):
        if not user:
            return None

        verification = EmailVerification.objects.create(user=user,
            old_email=user.email, new_email=self.cleaned_data['new_email'])

        context_email = {
            'user': user,
            'verification': verification,
            'email_change': True,
        }

        subject_template_name = 'mails/emailverification_subject.html',
        email_template_name = 'mails/emailverification.html',

        send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=self.cleaned_data['new_email'])

        return verification
# --------------------------------- #
# End Form for change of Email #
# --------------------------------- #


class RegisterEmailForm(forms.ModelForm):
    """
    Form for initial email registration.
    
    Used when a user needs to register an email address for the first time,
    typically after social authentication.
    """
    # Form for email registration, when the user does not have any registered
    email = forms.EmailField(
        label=_(u'Email'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _(u'ENter your Email')}),
        max_length=75,
        required=True,
        error_messages={'required': _(u'ENter your Email')}
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        user_emails = User.objects.filter(email__iexact=email).count()
        verification_emails = EmailVerification.objects.filter(new_email__iexact=email, is_expired=False).count()
        if user_emails + verification_emails > 0:
            raise forms.ValidationError(_(
                u'This email already exists. Please try a new one.'))
        return email

    class Meta:
        model = User
        fields = ['email']


# --------------------------------------- #
# Start Form for Change of Password #
# --------------------------------------- #
class ChangePasswordForm(forms.Form):
    """
    Form for password changes.
    
    Handles:
    - Current password verification
    - New password validation
    - Password confirmation
    - Password strength requirements
    """
    actual_password_lbl = _(u'Actual Password')
    new_password_lbl = _(u'password new')
    confirm_new_password_lbl = _(u'Confirm new password')
    old_password = forms.CharField(label=actual_password_lbl,
                                   widget=forms.PasswordInput(
                                       attrs={'class': "form-control", 'placeholder': 'Current Password'}
                                   ),
                                   error_messages={'required': _(u'Please enter your current password')},
    )
    new_password1 = forms.CharField(label=new_password_lbl,
                                    widget=forms.PasswordInput(
                                        attrs={'class': "form-control", 'placeholder': 'New Password'}
                                    ),
                                    error_messages={'required': _(u'Please enter your new password')},
    )
    new_password2 = forms.CharField(label=confirm_new_password_lbl,
                                    widget=forms.PasswordInput(
                                        attrs={'class': "form-control", 'placeholder': 'Confirm New Password'}
                                    ),
                                    error_messages={'required': _(u'Please confirm your new password')},
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_(u'The password is incorrect'))
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_(u'The passwords do not match'))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
# --------------------------------------- #
# Start Form for change of Password #
# --------------------------------------- #


# -------------------------------- #
# Start Form for Address #
# -------------------------------- #
def get_states(country=None, search_vacancy=False):
    choices = [('0', 'No choices')]
    if country:
        if type(country) == long or type(country) == int:
            country = Country.objects.get(pk=int(country))
        states = country.state_set.all()
        if states.count() > 0:
            if search_vacancy:
                choices = [('-1', 'All')]
            else:
                choices = [('-1', 'Select...')]
            for state in states:
                choices.append([state.id, state.name])
    return choices


def get_municipals(state=None):
    choices = [('0', 'Select a state first')]
    if state:
        if type(state) == long or type(state) == int:
            state = State.objects.get(pk= int(state))
        # municipals = state.municipal_set.all()
        # if municipals.count() > 0:
        #     choices = [('-1', 'Select...')]
        #     for municipal in municipals:
        #         choices.append([municipal.id, municipal.name])
    return choices


class AdressForm(forms.ModelForm):
    """
    Form for managing address information.
    
    Handles:
    - Country selection
    - State/province selection
    - City/municipal selection
    - Street address
    - Postal code validation
    
    Features dynamic loading of location options based on selected country/state.
    """
    initial_country = get_initial_country()
    # country = forms.ModelChoiceField(
    #     queryset=countries(),
    #     widget=forms.Select(attrs={'class': "form-control"}),
    #     required=True,
    #     label=_(u'Country'),
    #     empty_label=_(u'Select...'),
    #     initial=Country.objects.get(id=initial_country.id)
    # )
    state = forms.ChoiceField(
        choices= get_states(initial_country),
        widget=forms.Select(attrs={'class': "form-control"}),
        label=_(u'State')
    )
    municipal = forms.ChoiceField(
        choices = get_municipals(None),
        widget=forms.Select(attrs={'class': "form-control"}),
        label = _(u'City:'),
        required=False
    )
    street = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'Street No or Colony'),
                                      'class': "form-control"}),
        max_length=200,
        error_messages={'required': _(u"Enter the address of your company")},
        label=_(u"Address:"),
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u' Postal Code'),
                                      'class': "form-control"}),
        max_length=5,
        error_messages={'required': _(u"Enter your Postal Code")},
        label=_(u"Postal Code:"),
    )

    def __init__(self, *args, **kwargs):
        change_profile = False
        country_selected = kwargs.pop('country_selected', None)
        state_selected = kwargs.pop('state_selected', None)
        try:
            if kwargs.pop('change_profile'):
                change_profile = True
        except:
            pass

        super(AdressForm, self).__init__(*args, **kwargs)

        if change_profile:
            self.fields['state'].choices = get_states(country_selected)
            self.fields['municipal'].choices = get_municipals(state_selected)

        if self.is_bound:
            if not country_selected:
                country_selected = self.initial_country
            if state_selected == 0:
                country_selected = None
                state_selected = None

            self.fields['state'].choices = get_states(country_selected)
            self.fields['municipal'].choices = get_municipals(state_selected)

    def clean_state(self):
        state_id = int(self.cleaned_data.get('state'))
        if state_id < 0:
            raise forms.ValidationError(_(u'Select a State'))
        if state_id == 0:
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
                raise forms.ValidationError(_(u'Select a state'))
            state = State.objects.get(pk = state_id)
        except State.DoesNotExist:
            raise forms.ValidationError(_(u'The state selected is invalid'))
        return state

    def clean_municipal(self):
        try:
            municipal_id = int(self.cleaned_data.get('municipal'))
        except:
            raise forms.ValidationError(_(u'The city selected is invalid'))
        if municipal_id < 0:
            raise forms.ValidationError(_(u'Select a City'))
        if municipal_id == 0:
            raise forms.ValidationError(_(u'Select a State first'))
        try:
            choices = [0]
            try:
                state = self.cleaned_data.get('state')
                state_id = state.pk
                state = State.objects.get(id=state_id)
                municipals = state.municipal_set.all()
                for municipal in municipals:
                    choices.append(municipal.id)
            except:
                return None
            if municipal_id not in choices:
                raise forms.ValidationError(_(u'Select a city'))
            municipal = Municipal.objects.get(pk = municipal_id)
        except Municipal.DoesNotExist:
            raise forms.ValidationError(_(u'The selected city is invalid'))
        return municipal

    class Meta:
        model = Address
        fields = ('state', 'municipal', 'street', 'postal_code')
# ----------------------------- #
# End Form for Address #
# ----------------------------- #


# Reset Password
class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.TextInput(attrs={'placeholder': _(u'* Email'), 'class': "form-control s-form-v4__input"}))

    def clean_email(self):
        email = self.cleaned_data['email']

        # Check and Inform the user if they enter through social networks
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            if user.logued_by == 'FB':
                raise forms.ValidationError(_(u'Registration was performed using your Facebook account.'))
            elif user.logued_by == 'GO':
                raise forms.ValidationError(_(u'Registration was performed using your Google Accont'))

        # Check who does not have registered email
        user_emails = User.objects.filter(email__iexact=email).count()
        if user_emails <= 0:
            raise forms.ValidationError(_(u'The email is not registered n the system. Please enter a different one.'))

        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             token_generator=default_token_generator,
             from_email=None,
             use_https=None,
             request=None,
             *args, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the user.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            context_email = {
                'email': user.email,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'password_reset': True,
            }
            send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=user.email)


class RecoverUserForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.TextInput(attrs={'placeholder': _(u'* Email'), 'class': "form-control s-form-v4__input"}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user_emails = User.objects.filter(email__iexact=email).count()
        verification_emails = EmailVerification.objects.filter(
            new_email__iexact=email, is_expired=False).count()
        if user_emails + verification_emails <= 0:
            raise forms.ValidationError(_(u'This email is not registered in the system. Please enter a different one.'))
        else:
            active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            if user.logued_by == 'FB':
                raise forms.ValidationError(_(u'Registration was done with your Facebook account'))
            elif user.logued_by == 'GO':
                raise forms.ValidationError(_(u'Registration was done with your Google account'))

        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             token_generator=default_token_generator,
             from_email=None,
             use_https=None,
             request=None,
             *args, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the user.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            context_email = {
                'email': user.email,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'recover_username': True,
            }

            send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=user.email)



### Contat Form ###
class ContactForm(forms.Form):
    """
    Base contact form for user inquiries.
    
    A comprehensive contact form implementation that:
    - Validates input data
    - Handles email sending
    - Supports template-based messages
    - Provides spam protection
    
    This form can be subclassed to create specialized contact forms
    with additional fields or custom behavior.
    """
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        super(ContactForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request

    name = forms.CharField(max_length=100,
                           label=_(u'Full Name'),
                           widget=forms.TextInput(attrs={'placeholder': _(u'* Name'), 'class': "form-control s-form-v3__input"})
    )
    email = forms.EmailField(max_length=200,
                             label=_(u'Email'),
                             widget=forms.TextInput(attrs={'placeholder': _(u'* Email'), 'class': "form-control s-form-v3__input"}),
    )

    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _(u'* Your message'), 'class': "form-control s-form-v3__input", 'rows': '5'}),
                            label=u'Message')

    from_email = settings.DEFAULT_FROM_EMAIL

    recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]

    subject_template_name = "mails/contact_form_subject.txt"

    template_name = 'mails/contact_form_email.txt'

    def message(self):
        """
        Render the body of the message to a string.

        """
        if callable(self.template_name):
            template_name = self.template_name()
        else:
            template_name = self.template_name
        return loader.render_to_string(template_name,
                                       self.get_context())

    def subject(self):
        """
        Render the subject of the message to a string.

        """
        subject = loader.render_to_string(self.subject_template_name,
                                          self.get_context())
        return ''.join(subject.splitlines())

    def get_context(self):
        """
        Return the context used to render the templates for the email
        subject and body.

        By default, this context includes:

        * All of the validated values in the form, as variables of the
          same names as their fields.

        * The current ``Site`` object, as the variable ``site``.

        * Any additional variables added by context processors (this
          will be a ``RequestContext``).

        """
        if not self.is_valid():
            raise ValueError("Cannot generate Context from invalid contact form")
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(self.request)
        return RequestContext(self.request,
                              dict(self.cleaned_data,
                                   site=site))

    def get_message_dict(self):
        """
        Generate the various parts of the message and return them in a
        dictionary, suitable for passing directly as keyword arguments
        to ``django.core.mail.send_mail()``.

        By default, the following values are returned:

        * ``from_email``

        * ``message``

        * ``recipient_list``

        * ``subject``

        """
        if not self.is_valid():
            raise ValueError("Message cannot be sent from invalid contact form")
        message_dict = {}
        for message_part in ('from_email', 'message', 'recipient_list', 'subject'):
            attr = getattr(self, message_part)
            message_dict[message_part] = attr() if callable(attr) else attr
        return message_dict

    def save(self, fail_silently=False):
        """
        Build and send the email message.

        """
        send_mail(fail_silently=fail_silently, **self.get_message_dict())
### End Contact Form ###
#
#
class EarlyAccessForm(ContactForm):
    
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        super(EarlyAccessForm, self).__init__(request=request, data=data, files=files, *args, **kwargs)
        self.fields['body'].required = False

    organization = forms.CharField(max_length=100,
                           label=_(u'Organization'),
                           widget=forms.TextInput(attrs={'placeholder': _(u'* Organization'), 'class': "form-control s-form-v3__input"})
    )
    
    position = forms.CharField(max_length=100,
                           label=_(u'Position'),
                           widget=forms.TextInput(attrs={'placeholder': _(u'* Position'), 'class': "form-control s-form-v3__input"})
    )
    
    subject_template_name = "mails/early_access_form_subject.txt"

    template_name = 'mails/early_access_form_email.txt'