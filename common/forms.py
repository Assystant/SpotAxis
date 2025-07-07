# -*- coding: utf-8 -*-
from __future__ import absolute_import
import ipgetter2
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
from django.utils.translation import gettext_lazy as _
from common.models import User, AccountVerification, Address, Country, State, Municipal, EmailVerification, send_TRM_email, Subdomain
from common import registration_settings
from django.template import loader
from django.template import RequestContext
from django.contrib.sites.requests import RequestSite
from TRM.settings import PHOTO_USER_DEFAULT
from upload_logos.widgets import AjaxClearableFileInput
from django.apps import apps

def get_initial_country():
    """
    Retrieves the initial country object for India (ISO code 'IN').
    Returns None if the country is not found.
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
    Form for handling user photo uploads with validation for image format and size.
    Validates that uploaded images are in JPG/JPEG/PNG format and under 1MB.
    """
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class':"form-control text-center"}), required=False)

    def clean_photo(self):
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
                raise forms.ValidationError(_('You can only use images with extensions JPG, JPEG or PNG'))

            #validate file size
            if len(image) > (1 * 1024 * 1024):
                raise forms.ValidationError(_('The image selected is too large (Max 1MB)'))
        else:
            return default_photo
        return image

    class Meta():
        model = User
        fields = ('photo',)


class SubdomainForm(forms.ModelForm):
    """
    Form for handling subdomain registration and validation.
    Validates that the subdomain is unique, not using spotaxis.com domain,
    and points to the correct IP address.
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
            if ipgetter2.myip() == ip:
                return cname
            else:
                raise forms.ValidationError('It looks like this subdomain does not point to us. Please add the CNAME setting to your DNS before proceeding.')

    class Meta:
        model = Subdomain
        fields = ('cname',)

class UserDataForm(forms.ModelForm):
    """
    Form for user registration and data collection.
    Handles user registration with email verification, password confirmation,
    and basic user information collection including name, email, and phone.
    """
    email_repeat_msg = _('Confirm your email')
    password_repeat_msg = _('* Confirm your Password')
    username = forms.RegexField(
        label=_("Name of User"),
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': _('* Username'),
                                      'class': "form-control s-form-v4__input"}),
        regex=r'^[\w.-]+$',
        error_messages={
            'invalid': _("Only letters, numbers and the following characters are allowed . - _"),
            'required': _("Enter a username")
        }
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _('* Email'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=75,
        error_messages={'required': _("Enter your Email")},
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
        widget=forms.PasswordInput(attrs={'placeholder': _('* Password'),
                                          'class': "form-control s-form-v4__input"}),
        max_length=128,
        error_messages={'required': _("ENter your Password")},
        label=_("Password")
    )

    password_repeat = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': password_repeat_msg,
                                          'class': "form-control s-form-v4__input"}),
        max_length=128,
        error_messages={'required': password_repeat_msg},
        label=password_repeat_msg,
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('* First Name'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        error_messages={'required': _("Enter your Name")},
        label=_("Name")
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('* Last Name'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        error_messages={'required': _("Enter your Last Name")},
        label=_("Surname")
    )

    cellphone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Phone'),
                                      'class': "form-control s-form-v4__input"}),
        max_length=30,
        min_length=5,
        required=False,
        error_messages={'required': _("Enter your Phone")},
        label=_("Phone")
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
                    _("Username already exists. Please try again."))

        return username

    def clean_email(self):
        if not registration_settings.CHECK_UNIQUE_EMAIL:
            return self.cleaned_data['email']

        new_email = self.cleaned_data['email']

        emails = User.objects.filter(email__iexact=new_email).count()
        
        if emails > 0:
            raise forms.ValidationError(
                _('This email is already registered. Please try a new one.'))
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
                    from django.forms.utils import ErrorList
                    self._errors['email'] = ErrorList()
                    self._errors['email'].append(_('Email addresses do not match'))
                    # raise forms.ValidationError(_(u'Email addresses do not match.'))

        if registration_settings.DOUBLE_CHECK_PASSWORD:
            if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
                if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                    from django.forms.utils import ErrorList
                    self._errors['password'] = ErrorList()
                    self._errors['password'].append(_('The passwords do not match'))
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
    Form for updating basic user information.
    Handles updates to user's name, email, and phone number with optional
    email change functionality based on settings.
    """
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Enter your name'),
                                      'class': 'form-control'}),
        max_length=30,
        required=True,
        error_messages={'required': _("Enter your name")},
        label=_("Name(s)")
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Enter your Surname'),
                                      'class': 'form-control'}),
        max_length=30,
        required=True,
        error_messages={'required': _("Enter your Surname")},
        label=_("Surname")
    )

    cellphone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Phone'),
                                      'class': "form-control"}),
        max_length=30,
        min_length=5,
        required = False,
        label=_("Phone")
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': _('Email'),
                                      'class': 'form-control'}),
        max_length=75,
        error_messages={'required': _("Enter your Email")},
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
    Form for handling email change requests.
    Validates new email uniqueness and sends verification email
    to the new address for confirmation.
    """
    new_email = forms.EmailField(
        label=_('New Email'),
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': _('Enter a new Email')
            }
        ),
        max_length=225,
        required=True,
        error_messages={'required': _('Enter a new Email')}
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
    Form for email-only registration.
    Validates email uniqueness and handles registration
    for users who don't have a registered email.
    """
    # Form for email registration, when the user does not have any registered
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('ENter your Email')}),
        max_length=75,
        required=True,
        error_messages={'required': _('ENter your Email')}
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        user_emails = User.objects.filter(email__iexact=email).count()
        verification_emails = EmailVerification.objects.filter(new_email__iexact=email, is_expired=False).count()
        if user_emails + verification_emails > 0:
            raise forms.ValidationError(_(
                'This email already exists. Please try a new one.'))
        return email

    class Meta:
        model = User
        fields = ['email']


# --------------------------------------- #
# Start Form for Change of Password #
# --------------------------------------- #
class ChangePasswordForm(forms.Form):
    """
    Form for handling password changes.
    Validates current password and ensures new password confirmation matches.
    Includes security checks and password update functionality.
    """
    actual_password_lbl = _('Actual Password')
    new_password_lbl = _('password new')
    confirm_new_password_lbl = _('Confirm new password')
    old_password = forms.CharField(label=actual_password_lbl,
                                   widget=forms.PasswordInput(
                                       attrs={'class': "form-control", 'placeholder': 'Current Password'}
                                   ),
                                   error_messages={'required': _('Please enter your current password')},
    )
    new_password1 = forms.CharField(label=new_password_lbl,
                                    widget=forms.PasswordInput(
                                        attrs={'class': "form-control", 'placeholder': 'New Password'}
                                    ),
                                    error_messages={'required': _('Please enter your new password')},
    )
    new_password2 = forms.CharField(label=confirm_new_password_lbl,
                                    widget=forms.PasswordInput(
                                        attrs={'class': "form-control", 'placeholder': 'Confirm New Password'}
                                    ),
                                    error_messages={'required': _('Please confirm your new password')},
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
            raise forms.ValidationError(_('The password is incorrect'))
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('The passwords do not match'))
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
    """
    Retrieves a list of states for a given country.
    Args:
        country: Country object or ID to get states for
        search_vacancy: Boolean to determine if this is for vacancy search
    Returns:
        List of tuples containing state IDs and names
    """
    choices = [('0', 'No choices')]
    if country:
        if type(country) == int or type(country) == int:
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
    """
    Retrieves a list of municipalities for a given state.
    Args:
        state: State object or ID to get municipalities for
    Returns:
        List of tuples containing municipal IDs and names
    """
    choices = [('0', 'Select a state first')]
    if state:
        if type(state) == int or type(state) == int:
            state = State.objects.get(pk= int(state))
        # municipals = state.municipal_set.all()
        # if municipals.count() > 0:
        #     choices = [('-1', 'Select...')]
        #     for municipal in municipals:
        #         choices.append([municipal.id, municipal.name])
    return choices


class AdressForm(forms.ModelForm):
    """
    Form for handling address information.
    Manages address data including state, city, street, and postal code
    with dynamic state and municipal selection based on country.
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
        label=_('State')
    )
    municipal = forms.ChoiceField(
        choices = get_municipals(None),
        widget=forms.Select(attrs={'class': "form-control"}),
        label = _('City:'),
        required=False
    )
    street = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Street No or Colony'),
                                      'class': "form-control"}),
        max_length=200,
        error_messages={'required': _("Enter the address of your company")},
        label=_("Address:"),
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(' Postal Code'),
                                      'class': "form-control"}),
        max_length=5,
        error_messages={'required': _("Enter your Postal Code")},
        label=_("Postal Code:"),
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
            raise forms.ValidationError(_('Select a State'))
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
                raise forms.ValidationError(_('Select a state'))
            state = State.objects.get(pk = state_id)
        except State.DoesNotExist:
            raise forms.ValidationError(_('The state selected is invalid'))
        return state

    def clean_municipal(self):
        try:
            municipal_id = int(self.cleaned_data.get('municipal'))
        except:
            raise forms.ValidationError(_('The city selected is invalid'))
        if municipal_id < 0:
            raise forms.ValidationError(_('Select a City'))
        if municipal_id == 0:
            raise forms.ValidationError(_('Select a State first'))
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
                raise forms.ValidationError(_('Select a city'))
            municipal = Municipal.objects.get(pk = municipal_id)
        except Municipal.DoesNotExist:
            raise forms.ValidationError(_('The selected city is invalid'))
        return municipal

    class Meta:
        model = Address
        fields = ('state', 'municipal', 'street', 'postal_code')
# ----------------------------- #
# End Form for Address #
# ----------------------------- #


# Reset Password
class CustomPasswordResetForm(forms.Form):
    """
    Form for handling password reset requests.
    Validates user email, checks authentication method,
    and sends password reset instructions.
    """
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.TextInput(attrs={'placeholder': _('* Email'), 'class': "form-control s-form-v4__input"}))

    def clean_email(self):
        email = self.cleaned_data['email']

        # Check and Inform the user if they enter through social networks
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            if user.logued_by == 'FB':
                raise forms.ValidationError(_('Registration was performed using your Facebook account.'))
            elif user.logued_by == 'GO':
                raise forms.ValidationError(_('Registration was performed using your Google Accont'))

        # Check who does not have registered email
        user_emails = User.objects.filter(email__iexact=email).count()
        if user_emails <= 0:
            raise forms.ValidationError(_('The email is not registered n the system. Please enter a different one.'))

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
    """
    Form for handling username recovery requests.
    Validates user email and authentication method,
    sends recovery instructions to verified email.
    """
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.TextInput(attrs={'placeholder': _('* Email'), 'class': "form-control s-form-v4__input"}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user_emails = User.objects.filter(email__iexact=email).count()
        verification_emails = EmailVerification.objects.filter(
            new_email__iexact=email, is_expired=False).count()
        if user_emails + verification_emails <= 0:
            raise forms.ValidationError(_('This email is not registered in the system. Please enter a different one.'))
        else:
            active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            if user.logued_by == 'FB':
                raise forms.ValidationError(_('Registration was done with your Facebook account'))
            elif user.logued_by == 'GO':
                raise forms.ValidationError(_('Registration was done with your Google account'))

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
    The base contact form class from which all contact form classes
    should inherit.

    If you don't need any custom functionality, you can simply use
    this form to provide basic contact functionality; it will collect
    name, email address and message.

    The ``ContactForm`` view included in this application knows how to
    work with this form and can handle many types of subclasses as
    well (see below for a discussion of the important points), so in
    many cases it will be all that you need. If you'd like to use this
    form or a subclass of it from one of your own views, just do the
    following:

    1. When you instantiate the form, pass the current ``HttpRequest``
       object to the constructor as the keyword argument ``request``;
       this is used internally by the base implementation, and also
       made available so that subclasses can add functionality which
       relies on inspecting the request.

    2. To send the message, call the form's ``save`` method, which
       accepts the keyword argument ``fail_silently`` and defaults it
       to ``False``. This argument is passed directly to
       ``send_mail``, and allows you to suppress or raise exceptions
       as needed for debugging. The ``save`` method has no return
       value.

    Other than that, treat it like any other form; validity checks and
    validated data are handled normally, through the ``is_valid``
    method and the ``cleaned_data`` dictionary.


    Base implementation
    -------------------

    Under the hood, this form uses a somewhat abstracted interface in
    order to make it easier to subclass and add functionality. There
    are several important attributes subclasses may want to look at
    overriding, all of which will work (in the base implementation) as
    either plain attributes or as callable methods:

    * ``from_email`` -- used to get the address to use in the
      ``From:`` header of the message. The base implementation returns
      the value of the ``DEFAULT_FROM_EMAIL`` setting.

    * ``message`` -- used to get the message body as a string. The
      base implementation renders a template using the form's
      ``cleaned_data`` dictionary as context.

    * ``recipient_list`` -- used to generate the list of recipients
      for the message. The base implementation returns the email
      addresses specified in the ``MANAGERS`` setting.

    * ``subject`` -- used to generate the subject line for the
      message. The base implementation returns the string 'Message
      sent through the web site', with the name of the current
      ``Site`` prepended.

    * ``template_name`` -- used by the base ``message`` method to
      determine which template to use for rendering the
      message. Default is ``contact_form/contact_form_email.txt``.

    Internally, the base implementation ``_get_message_dict`` method
    collects ``from_email``, ``message``, ``recipient_list`` and
    ``subject`` into a dictionary, which the ``save`` method then
    passes directly to ``send_mail`` as keyword arguments.

    Particularly important is the ``message`` attribute, with its base
    implementation as a method which renders a template; because it
    passes ``cleaned_data`` as the template context, any additional
    fields added by a subclass will automatically be available in the
    template. This means that many useful subclasses can get by with
    just adding a few fields and possibly overriding
    ``template_name``.

    Much useful functionality can be achieved in subclasses without
    having to override much of the above; adding additional validation
    methods works the same as any other form, and typically only a few
    items -- ``recipient_list`` and ``subject_line``, for example,
    need to be overridden to achieve customized behavior.


    Other notes for subclassing
    ---------------------------

    Subclasses which want to inspect the current ``HttpRequest`` to
    add functionality can access it via the attribute ``request``; the
    base ``message`` takes advantage of this to use ``RequestContext``
    when rendering its template. See the ``AkismetContactForm``
    subclass in this file for an example of using the request to
    perform additional validation.

    Subclasses which override ``__init__`` need to accept ``*args``
    and ``**kwargs``, and pass them via ``super`` in order to ensure
    proper behavior.

    Subclasses should be careful if overriding ``_get_message_dict``,
    since that method **must** return a dictionary suitable for
    passing directly to ``send_mail`` (unless ``save`` is overridden
    as well).

    Overriding ``save`` is relatively safe, though remember that code
    which uses your form will expect ``save`` to accept the
    ``fail_silently`` keyword argument. In the base implementation,
    that argument defaults to ``False``, on the assumption that it's
    far better to notice errors than to silently not send mail from
    the contact form.

    """
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        super(ContactForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request

    name = forms.CharField(max_length=100,
                           label=_('Full Name'),
                           widget=forms.TextInput(attrs={'placeholder': _('* Name'), 'class': "form-control s-form-v3__input"})
    )
    email = forms.EmailField(max_length=200,
                             label=_('Email'),
                             widget=forms.TextInput(attrs={'placeholder': _('* Email'), 'class': "form-control s-form-v3__input"}),
    )

    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('* Your message'), 'class': "form-control s-form-v3__input", 'rows': '5'}),
                            label='Message')

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
        #if Site._meta.installed:
        #    site = Site.objects.get_current()
        if apps.is_installed('django.contrib.sites'):
            try:
                site = Site.objects.get_current()
            except Site.DoesNotExist:
                site = RequestSite(self.request)
        else:
            site = RequestSite(self.request)
        #return RequestContext(self.request,
        #                      dict(self.cleaned_data,
        #                           site=site))
        return {
            **self.cleaned_data,
            "site": site
        }

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
                           label=_('Organization'),
                           widget=forms.TextInput(attrs={'placeholder': _('* Organization'), 'class': "form-control s-form-v3__input"})
    )
    
    position = forms.CharField(max_length=100,
                           label=_('Position'),
                           widget=forms.TextInput(attrs={'placeholder': _('* Position'), 'class': "form-control s-form-v3__input"})
    )
    
    subject_template_name = "mails/early_access_form_subject.txt"

    template_name = 'mails/early_access_form_email.txt'