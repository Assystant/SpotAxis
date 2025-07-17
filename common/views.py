# -*- coding: utf-8 -*-

import traceback
import urllib
from urllib import parse as urlparse
import requests
import json
from django.urls import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from candidates.models import *
from companies.models import *
from TRM.settings import PROJECT_NAME, SITE_URL
from django.contrib import messages
from django.contrib.auth import login
from common.models import User, AccountVerification, Profile, Gender, send_email_to_TRM, send_TRM_email, SocialAuth, Country
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from common import registration_settings
from common.forms import ChangeEmailForm, ContactForm, RegisterEmailForm
from common.models import EmailVerification
from datetime import datetime, date
from payments.models import Subscription, PriceSlab
from TRM.context_processors import subdomain
from activities.utils import post_notification
from TRM import settings
from django.template.context_processors import csrf
from vacancies.models import Vacancy, Postulate
from utils import generate_random_username
from requests_oauthlib import OAuth1
from django.db.models import Q
from utils import is_ajax

"""
View functions for the common app.

This module provides view functions and classes for:
- User registration and activation
- Social authentication
- Profile management
- Email management
- Password management
- Contact form handling
- Social media integration

Most views require authentication unless explicitly noted.
"""


# ------------------- #
# Start Registration #
# ------------------- #
def save_candidate_social_data(backend, user, response, *args, **kwargs):
    """
    Save additional candidate data from social authentication.
    
    Called after successful social authentication to store additional
    profile information from the social platform.
    
    Args:
        backend: Social auth backend instance
        user: User instance
        response: Social platform's response data
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments
    """
    # Register candidate and profile when entering with Facebook or Google
    # print backend.name
    # print response
    user = User.objects.get(pk=user.id)
    try:
        candidate = Candidate.objects.get(user_id=user.pk)
        if not candidate.first_name and not candidate.last_name:
            candidate.first_name = user.first_name
            candidate.last_name = user.last_name
            candidate.save()
        pass
    except:
        try:
            gender = Gender.objects.get(codename__iexact=str(response.get('gender', '')))
        except:
            gender = None
        candidate = Candidate.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            gender = gender,
        )
        user.profile = Profile.objects.get(codename__exact='candidate')
        if backend.name == 'facebook':
            user.logued_by = 'FB'
        elif backend.name == 'google-oauth2':
            user.logued_by = 'GO'
        user.save()
        try:
            # Notification of New Registration
            date = datetime.strftime(datetime.now(), '%d-%m-%Y %I:%M:%S %p')
            body_email = 'User: %s<br><br>Candidate: %s<br><br>Date: %s' % (candidate.user, candidate.user.get_full_name(), date)
            send_email_to_TRM(subject='New Candidate Registration', body_email=body_email)
        except:
            pass


def registration_activate(request, activation_key):
    """
    Activate a user account using the provided activation key.
    
    Args:
        request: HttpRequest object
        activation_key: String key for account activation
        
    Returns:
        HttpResponse: Activation success/failure page
    """
    activation_key = activation_key.lower()
    account = AccountVerification.objects.activate_user(activation_key)

    if account:
        account.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, account)
        # print account
        user_profile = account.profile.codename
        # print user_profile
        if user_profile == 'candidate':
            try:
                # Notification
                candidate = Candidate.objects.get(user=account)
                date = datetime.strftime(datetime.now(), '%d-%m-%Y %I:%M:%S %p')
                body_email = 'User: %s<br><br>Candidate: %s<br><br>Date: %s' % (candidate.user, candidate.user.get_full_name(), date)
                send_email_to_TRM(subject='New Candidate Registration', body_email=body_email)
            except:
                pass

            messages.success(request, _(u'Welcome to %s. We have successfully activated your account. The next step is to complete your Profile.'%PROJECT_NAME))
            post_notification(user = request.user,action = "Welcome to SpotAxis!")
            return redirect('candidates_edit_curriculum')
        elif user_profile == 'recruiter':
            try:
                # Notifications
                company = Company.objects.select_related('user').get(user_id=account)

                #Inform company of the recommendation
                # try:
                #     recommendation =  Recommendations.objects.select_related('to_company').get(from_company=company)
                #     recommendation.status = Recommendation_Status.objects.get(codename__iexact='inactive')
                #     recommendation.save()
                #     context_email = {
                #         'user': company.user,
                #         'company': company.name,
                #         'companies_company_recommendations': True,
                #     }
                #     subject_template_name='mails/company_recommendation_subject.html',
                #     email_template_name='mails/company_recommendation_email.html',
                #     send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=recommendation.to_company.user.email)
                # except Exception, err:
                #     print(traceback.format_exc())
                #     pass

                # Notification
                date = datetime.strftime(datetime.now(), '%d-%m-%Y %I:%M:%S %p')
                body_email = 'User: %s<br><br>Company: %s<br><br>Date: %s' % (company.user, company.name, date)
                send_email_to_TRM(subject='New Company Registration', body_email=body_email)
            except:
                pass

            messages.success(request, _(u'Welcome to %s. We have successfully activated your account.' % PROJECT_NAME))
            return redirect('companies_record_company')
        else:
            raise Http404

    return render(request, 'new_registration_messages.html')


def registration_complete(request, template_name=None):
    """
    Display registration completion page.
    
    Args:
        request: HttpRequest object
        template_name: Optional template to use
        
    Returns:
        HttpResponse: Registration completion page
    """
    # raise ValueError(request.session.keys());
    if not template_name:
        template_name = 'new_registration_messages.html'
    return render(request, template_name, {
        'account_verification_active': registration_settings.USE_ACCOUNT_VERIFICATION,
        'email': request.session.get('new_email','you'),
        'expiration_days': registration_settings.ACCOUNT_VERIFICATION_DAYS,
        'static_header': True
    })

# ---------------- #
# End Registration #
# ---------------- #


@login_required
def register_blank_email(request):
    """
    Handle registration of email for users without one.
    
    Typically used after social authentication when email is not provided.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Email registration form or success page
    """
    """ Register e-mail when the user does not have registered in the database """
    if request.method == 'POST':
        form = RegisterEmailForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('common_redirect_after_login')
    else:
        form = RegisterEmailForm(instance=request.user)

    return render(request, 'register_blank_email.html', {'actual_email': request.user.email, 'form': form})


@login_required
def redirect_after_login(request):
    """ Redirecting the user depending on your profile """
    #profile = request.user.profile.codename
    profile = getattr(getattr(request.user, 'profile', None), 'codename', None)
    redirect_page = 'TRM-Subindex'    
    context={}
    subdomain_data = subdomain(request)
    context['success']=True
    # redirect_page = request.session.pop('next','')
    # if redirect_page:
    #     return redirect(redirect_page)
        
    if not request.user.email:
        # If you have registered without email
        redirect_page = 'common_register_blank_email'
    if profile == 'recruiter':
        # If is Recruiter/Company
        recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        if recruiter.company.all():
            subscription,created = Subscription.objects.get_or_create(company = recruiter.company.all()[0])
            if created:
                subscription.price_slab = PriceSlab.objects.first()
                subscription.save()
            if subdomain_data['active_host']:
                redirect_page = request.scheme + "://" + subdomain_data['active_host'].replace('http://','').replace('https://','')
            else:
                redirect_page = request.scheme + "://" + recruiter.company.all()[0].getsubdomainurl().replace('http://','').replace('https://','')
        else:
            redirect_page = 'companies_record_company'
    elif profile == 'candidate':
        # If is Candidate
        try:
            host = subdomain_data['active_host']
        except:
            host=None
        if host:
            redirect_page = reverse('TRM-Subindex')
        else:
            #redirect_page = reverse('TRM-index')
            redirect_page = reverse('candidates_edit_curriculum')
    elif profile == 'Admin':
        redirect_page = SITE_URL + '/admin/'
    if not is_ajax(request):
        return redirect(redirect_page)
    else:
        return JsonResponse(context)

# ------------ #
# Email Change #
# ------------ #
@login_required
def email_change(request):
    """
    Handle email address change requests.
    
    Processes the email change form and initiates verification process.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Email change form or confirmation page
    """
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            verification = form.save(request.user)
            email = request.POST['new_email']
            request.session['new_email'] = email
            return redirect('common_email_change_requested')
    else:
        form = ChangeEmailForm()

    return render(request, 'email_change.html', {'actual_email': request.user.email, 'form': form})


@login_required
def email_change_requested(request):
    return render(request, 'email_change_requested.html',
                  {'email': request.session['new_email'],
                   'expiration_days': registration_settings.EMAIL_VERIFICATION_DAYS,})


@login_required
def email_change_approve(request, token, code):
    try:
        verification = EmailVerification.objects.get(token=token, code=code,
            user=request.user, is_expired=False, is_approved=False)
        verification.is_approved = True
        verification.save()
        messages.success(request, _(u'The email has changed to %(email)s' % {
            'email': verification.new_email}))
    except EmailVerification.DoesNotExist:
        messages.error(request,
            _(u'You cannot change the Email address. The confirmation link is invalid.'))
    profile = request.user.profile.codename
    if profile == 'candidate':
        return redirect('candidates_edit_curriculum')
    else:
        return redirect('companies_recruiter_profile')


# ---------------------- #
# Password Change #
# ---------------------- #
@login_required
def password_change_done(request):
    profile = request.user.profile
    messages.success(request, _(u'Your password has changed successfully.'))
    if profile == 'candidate':
        return redirect('candidates_edit_curriculum')
    else:
        return redirect('companies_recruiter_profile')


def custom_password_reset_complete(request):
    """ When the password is reset """
    messages.success(request, _(u'Your password has been successfully restored'))
    return redirect('auth_login')


def recover_user_requested(request):
    """ Recover User """
    return render(request, 'new_recover_user_requested.html',{'static_header':True})


# ------------------ #
# Contact Page #
# ------------------ #
from django.views.generic.edit import FormView

def contact_form(request):
    form = ContactForm(data=request.POST, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('common_contact_form_sent')
    return render(request,'contact_page.html',{'form':form,})

class ContactFormView(FormView):
    """
    View for handling contact form submissions.
    
    Provides:
    - Form display
    - Validation
    - Email sending
    - Success handling
    
    Attributes:
        form_class: The form class to use
        template_name: Template for rendering the form
    """
    form_class = ContactForm
    template_name = 'contact_page.html'

    def form_valid(self, form):
        """
        Handle valid form submission.
        
        Args:
            form: Validated form instance
            
        Returns:
            HttpResponse: Redirect to success page
        """
        form.save()
        return super(ContactFormView, self).form_valid(form)

    def get_form_kwargs(self):
        # ContactForm instances require instantiation with an
        # HttpRequest.
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        # This is in a method instead of the success_url attribute
        # because doing it as an attribute would involve a
        # module-level call to reverse(), creating a circular
        # dependency between the URLConf (which imports this module)
        # and this module (which would need to access the URLConf to
        # make the reverse() call).
        return reverse('common_contact_form_sent')

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        context['isContact'] = True
        return self.response_class(
            request = self.request,
            template = self.get_template_names(),
            context = context,
            **response_kwargs
        )

def debug_fb_token(fbtoken):
    """
    Debug a Facebook access token.
    
    Args:
        fbtoken: Facebook access token
        
    Returns:
        dict: Token debug information
    """
    consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
    url = "https://graph.facebook.com/debug_token?input_token="+str(fbtoken)+"&access_token="+consumer_key+"|"+consumer_secret
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def revoke_fb_token(fbtoken):
    consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
    url = "https://graph.facebook.com/debug_token?input_token="+str(fbtoken)+"&access_token="+consumer_key+"|"+consumer_secret
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def debug_gp_token(ghtoken):
    consumer_key = settings.SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET
    url = " https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+ghtoken
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def debug_gh_token(ghtoken):
    consumer_key = settings.SOCIALAUTH_GITHUB_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_GITHUB_OAUTH_SECRET
    url = "https://api.github.com/user?access_token="+ghtoken
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def debug_so_token(sotoken):
    consumer_key = settings.SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET
    url = "https://api.stackexchange.com/2.2/access-tokens/"+sotoken
    resp = requests.get(url)
    Data = json.loads(resp.content)
    return Data

def debug_li_token(litoken):
    consumer_key = settings.SOCIALAUTH_LINKEDIN_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_LINKEDIN_OAUTH_SECRET
    url = "https://api.linkedin.com/v1/people/~:(id,picture-url,headline,first-name,last-name)?format=json&oauth2_access_token="+litoken
    resp = requests.get(url)
    Data = json.loads(resp.content)
    return Data

def revoke_li_token(litoken):
    consumer_key = settings.SOCIALAUTH_LINKEDIN_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_LINKEDIN_OAUTH_SECRET
    url = "https://api.linkedin.com/v1/people/~:(id,picture-url,headline,first-name,last-name)?format=json&oauth2_access_token="+litoken
    resp = requests.get(url)
    Data = json.loads(resp.content)
    return Data

def debug_tw_token(twtoken):
    consumer_key = settings.SOCIALAUTH_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_TWITTER_OAUTH_SECRET
    access_token = twtoken.split('|-|')[0]
    access_token_secret = twtoken.split('|-|')[1]
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    resp = requests.get(url, auth=auth)
    Data = json.loads(resp.content)
    return Data

def revoke_tw_token(twtoken):
    consumer_key = settings.SOCIALAUTH_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_TWITTER_OAUTH_SECRET
    access_token = twtoken.split('|-|')[0]
    access_token_secret = twtoken.split('|-|')[1]
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    url = "https://api.twitter.com/oauth2/invalidate_token"
    resp = requests.get(url, auth=auth)
    Data = json.loads(resp.content)
    return Data

def debug_token(token,social_code):
    if social_code == 'fb':
        return debug_fb_token(token)
    elif social_code == 'gp':
        return debug_gp_token(token)
    elif social_code == 'gh':
        return debug_gh_token(token)
    if social_code == 'li':
        return debug_li_token(token)
    elif social_code == 'so':
        return debug_so_token(token)    
    if social_code == 'tw':
        return debug_tw_token(token)
def revoke_token(token,social_code):
    if social_code == 'fb':
        return revoke_fb_token(token)
    # elif social_code == 'gp':
        # return revoke_gp_token(token)
    # elif social_code == 'gh':
        # return revoke_gh_token(token)
    elif social_code == 'li':
        return revoke_li_token(token)
    # elif social_code == 'so':
        # return revoke_so_token(token)    
    elif social_code == 'tw':
        return revoke_tw_token(token)
def get_account(social_code, identifier, email):
    auth = SocialAuth.objects.filter(social_code=social_code, identifier = identifier)
    if auth:
        return auth[0].user
    user = User.objects.filter(email=email)
    if user:
        return user[0]
    return None

def get_fb_web_response(suffix, socialauth=None):
    url = "https://graph.facebook.com/v2.8/" + suffix
    if socialauth:
        url = url + '&access_token=' + str(socialauth)
    resp = urllib.urlopen(url)
    return resp

def get_fb_user_groups(user):
    consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
    socialUser = SocialAuth.objects.get(user = user, social_code = 'fb')
    url = "https://graph.facebook.com/me/groups?access_token="+socialUser.oauth_token
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def get_fb_user_pages(user):
    consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
    socialUser = SocialAuth.objects.get(user = user, social_code = 'fb')
    url = "https://graph.facebook.com/me/accounts?access_token="+socialUser.oauth_token
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def get_fb_profile(user):
    consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
    socialUser = SocialAuth.objects.get(user = user, social_code = 'fb')
    url = "https://graph.facebook.com/me/?fields=name,picture&access_token="+socialUser.oauth_token
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data
    
def get_li_companies(user):
    socialUser = SocialAuth.objects.get(user = user, social_code = 'li')
    url = 'https://api.linkedin.com/v1/companies?format=json&is-company-admin=true&oauth2_access_token='+socialUser.oauth_token
    resp = urllib.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def social_login(request, social_code, vacancy_id=None, recruiter_id=None, redirect_type=None):
    """
    Handle social media login requests.
    
    Processes login/registration through various social platforms.
    
    Args:
        request: HttpRequest object
        social_code: Identifier for social platform
        vacancy_id: Optional vacancy to redirect to
        recruiter_id: Optional recruiter reference
        redirect_type: Optional redirect behavior specification
        
    Returns:
        HttpResponse: Redirect to appropriate page after login
    """
    csrftoken = csrf(request).values()[0]
    if not recruiter_id:
        recruiter_id = request.session.pop('recruiter_id', None)
    if not vacancy_id:
        vacancy_id = request.session.pop('vacancy_id',None)
    if request.user.is_authenticated and not recruiter_id:
        raise Http404
    if not social_code in settings.social_application_list:
        if not vacancy_id:
            raise Http404
        else:
            messages.error(request,'We currently do not support this method of authentication. Please try again later.')
            return redirect('vacancies_get_vacancy_details', vacancy_id=vacancy_id)
    subdomain_data = subdomain(request)

    redirect_uri = settings.HOSTED_URL + reverse('social_login', kwargs={'social_code':social_code})
    if social_code =='fb':
        app_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
        header_required = False
        if recruiter_id:
            scope = 'public_profile,email,publish_actions,user_managed_groups,manage_pages,publish_pages'
        else:
            scope = 'public_profile,email,user_about_me,user_birthday,user_education_history,user_hometown,user_likes,user_location,user_website,user_work_history'

        auth_url_prefix = "https://www.facebook.com/dialog/oauth/?auth_type=rerequest&"
        token_url_prefix = "https://graph.facebook.com/v2.8/oauth/access_token?client_id="+app_key+"&redirect_uri="+redirect_uri+"&client_secret="+app_secret+"&code="
    elif social_code == 'li':
        app_key = settings.SOCIALAUTH_LINKEDIN_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_LINKEDIN_OAUTH_SECRET
        header_required = False
        if recruiter_id:
            scope = 'r_basicprofile%20r_emailaddress%20w_share%20rw_company_admin'
        else:
            scope = 'r_basicprofile%20r_emailaddress'
        auth_url_prefix = "https://www.linkedin.com/oauth/v2/authorization/?response_type=code&"
        token_url_prefix = "https://www.linkedin.com/oauth/v2/accessToken/?grant_type=authorization_code&client_id="+app_key+"&redirect_uri="+redirect_uri+"&client_secret="+app_secret+"&code="
    elif social_code == 'tw':
        app_key = settings.SOCIALAUTH_TWITTER_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_TWITTER_OAUTH_SECRET
        auth = OAuth1(client_key = app_key,client_secret = app_secret, callback_uri = redirect_uri)
        # timestamp = str(get_epoch())
        # signed_key = 
        # headers = {
        #     'Authorization': 'OAuth oauth_callback="' + redirect_uri + '",oauth_consumer_key="' + app_key + '",oauth_none="' + str(csrftoken) + '",oauth_signature="' + app_key + '",oauth_signature_method="HMAC-SHA1",oauth_timestamp="' + timestamp + '",oauth_version="1.0"'
        # }
        header_required = True
        scope = ''
        auth_url_prefix= "https://api.twitter.com/oauth/authenticate?oauth_token="
        if not request.GET.get('oauth_verifier'):
            oauth_token_url = "https://api.twitter.com/oauth/request_token"
            oauth_token_response = requests.get(oauth_token_url, auth=auth)
            code = oauth_token_response.status_code
            content = json.loads(json.dumps(urlparse.parse_qs(oauth_token_response.content)))
            oauth_token = content['oauth_token']
            oauth_token_secret = content['oauth_token_secret']
            auth_url_prefix += oauth_token[0]
            # return redirect(auth_url)
        token_url_prefix = "https://api.twitter.com/oauth/access_token"
    elif social_code == 'gp':
        app_key = settings.SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET
        scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/user.birthday.read'

        header_required = True
        auth_url_prefix = 'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&'
        token_url_prefix = 'https://www.googleapis.com/oauth2/v4/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri
        }
    elif social_code == 'gh':
        app_key = settings.SOCIALAUTH_GITHUB_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_GITHUB_OAUTH_SECRET
        scope = 'user,public_repo'
        header_required = False
        auth_url_prefix = 'https://github.com/login/oauth/authorize?'
        token_url_prefix = "https://github.com/login/oauth/access_token?accept=json&client_id="+app_key+"&redirect_uri="+redirect_uri+"&client_secret="+app_secret+"&code="
    elif social_code == 'so':
        app_key = settings.SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY
        app_secret = settings.SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET
        scope = ''
        header_required = True
        auth_url_prefix = 'https://stackexchange.com/oauth?'
        token_data = {
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri
        }
        token_url_prefix = 'https://stackexchange.com/oauth/access_token'
    authCode = request.GET.get('code', None)
    if social_code == 'tw':
        authCode = request.GET.get('oauth_verifier', None)
    callback_host = request.session.pop('redirect_to', None)
    if subdomain_data['active_host'] and recruiter_id:
        request.session['enableshare'] = True
    if not subdomain_data['active_host'] and authCode:
        if request.GET.get('state') != str(csrftoken) and not social_code == 'tw':
            messages.error(request,'Unauthorised access')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
        if recruiter_id:
            reversepath = reverse('social_login',kwargs={'social_code':social_code,'vacancy_id':vacancy_id,'recruiter_id':recruiter_id})
        elif vacancy_id:
            reversepath = reverse('social_login',kwargs={'social_code':social_code,'vacancy_id':vacancy_id})
        else:
            reversepath = reverse('social_login',kwargs={'social_code':social_code})
        if social_code == 'tw':
            return redirect(callback_host + reversepath + '?oauth_token=' + request.GET.get('oauth_token') + '&oauth_verifier=' + authCode)
        else:
            return redirect(callback_host + reversepath + '?code=' + authCode)
    elif subdomain_data['active_host'] and not authCode:
        callback_host = request.scheme + '://' + request.get_host()
        return redirect(settings.HOSTED_URL + request.path + '?redirect_to=' + callback_host)
    elif not subdomain_data['active_host'] and not authCode:
        request.session['redirect_to'] = request.GET.get('redirect_to','')
        request.session['vacancy_id'] = vacancy_id
        request.session['recruiter_id'] = recruiter_id
        if social_code != 'tw':
            auth_url = auth_url_prefix + 'client_id='+app_key+'&redirect_uri='+redirect_uri+'&state='+str(csrftoken)+'&scope='+scope
        else:
            auth_url = auth_url_prefix
        return redirect(auth_url)
    # raise ValueError(request.session)
    review={}
    social_name=""
    photo = ""
    if not header_required:
        token_url = token_url_prefix + authCode
        resp = requests.get(token_url)
        resp_data = resp.content
    elif social_code == 'tw':
        token_url = token_url_prefix
        auth = OAuth1(app_key,app_secret,request.GET.get('oauth_token'))
        resp = requests.post(token_url,auth = auth, data="oauth_verifier="+request.GET.get('oauth_verifier'))
        resp_data = resp.content
    else:
        token_url = token_url_prefix
        token_data['code'] = authCode
        resp = requests.post(token_url, data=token_data)
        # raise ValueError(resp.content)
        resp_data = resp.content
    if social_code == 'fb':
        auth_data = json.loads(resp_data)
        #check permissions on token
        access_token = auth_data['access_token']
        token_data = debug_fb_token(auth_data['access_token'])
        if not token_data.has_key('data'):
            messages.error(request,'Failed to acquire authentication')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
        token_data = token_data['data']
        identifier = token_data['user_id']
        received_scopes = token_data['scopes']
        scopes = scope.split(',')
    elif social_code == 'li':
        auth_data = json.loads(resp_data)
        access_token = auth_data['access_token']
        token_data = debug_li_token(access_token)
        photo = token_data['pictureUrl']
        social_name = token_data['firstName'] + ' ' + token_data['lastName']
        received_scopes = ""
        identifier = token_data['id']
        scopes = ""
    elif social_code  == 'tw':
        resp_data = json.dumps(urlparse.parse_qs(resp_data))
        auth_data = json.loads(resp_data)
        access_token = auth_data['oauth_token'][0] + '|-|' + auth_data['oauth_token_secret'][0]
        token_data = debug_tw_token(access_token)
        photo = token_data['profile_image_url_https']
        social_name = token_data['name'] + ' @' + token_data['screen_name']
        identifier = auth_data['user_id'][0]
        received_scopes = ""
        scopes = scope.split(',')
    elif social_code == 'gh':
        resp_data = json.dumps(urlparse.parse_qs(resp_data))
        auth_data = json.loads(resp_data)
        access_token = auth_data['access_token']
        if access_token:
            access_token = access_token[0]
            token_data = debug_gh_token(access_token)
            received_scopes = auth_data['scope']
            if received_scopes:
                received_scopes = received_scopes[0].split(',')
        else:
            access_token = ""
            token_data = ""
            received_scopes = ""
        scopes = scope.split(',')

    elif social_code == 'gp':
        # resp_data = json.dumps(resp_data)
        auth_data  = json.loads(resp_data)
        access_token = auth_data['access_token']
        token_data = debug_gp_token(access_token)
        identifier = token_data['user_id']
        received_scopes = token_data['scope']
        if received_scopes:
            received_scopes = received_scopes.split(' ')
        scopes = scope.split(' ')
    elif social_code == 'so':
        resp_data = json.dumps(urlparse.parse_qs(resp_data))
        auth_data = json.loads(resp_data)
        access_token = auth_data['access_token'][0]
        token_data = debug_so_token(access_token)
        identifier = token_data['items'][0]['account_id']
        received_scopes = ""
        scopes=""
    if social_code == 'fb' and recruiter_id:
        if not 'publish_actions' in received_scopes:
            messages.error(request, 'Publish permissions are required to post on Facebook.')  
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)     
    else:
        for scope in scopes:
            if scope and scope not in received_scopes:
                messages.error(request,'Provide full permissions')
                return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
    if recruiter_id:
        try:
            recruiter = Recruiter.objects.get(id=recruiter_id)
            # if recruiter.user != request.user:
            #     raise ValueError()
            social,created = SocialAuth.objects.get_or_create(user = recruiter.user, social_code = social_code)
            social.oauth_token = access_token
            if photo:
                social.get_remote_image(photo)
                social.remote_photo = photo
            if social_name:
                social.social_name = social_name
            # if created:
            social.identifier = identifier
            social.save()
            if social_code == 'fb':
                profile_data = get_fb_profile(recruiter.user)
                social.get_remote_image(profile_data['picture']['data']['url'])
                social.remote_photo = profile_data['picture']['data']['url']
                social.social_name = profile_data['name']
                social.save()
            return redirect('social_verification',vacancy_id=vacancy_id,social_code=social_code)
        except Exception as e:
            messages.error(request, 'Authentication Failed')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
    else:
        if social_code == 'fb':
            fields = 'id,name,work,education,email,first_name,last_name,gender,birthday,website,languages,picture'
            perm_url = "https://graph.facebook.com/me?fields="+fields+"&access_token=" + access_token
            perm_resp = urllib.urlopen(perm_url)
            perm_data = json.loads(perm_resp.read())
        elif social_code == 'li':
            fields = 'id,first-name,last-name,location,positions,picture-url,email-address'
            perm_url = 'https://api.linkedin.com/v1/people/~:(' + fields + ')?format=json&oauth2_access_token=' + access_token
            perm_resp = urllib.urlopen(perm_url)
            perm_data = json.loads(perm_resp.read())
        elif social_code == 'gh':
            perm_url = 'http://api.github.com/user?access_token='+access_token
            repo_url = 'http://api.github.com/user/repos?access_token='+access_token
            perm_resp = urllib.urlopen(perm_url)
            repo_resp = urllib.urlopen(repo_url)
            perm_data = json.loads(perm_resp.read())
            perm_data['repos'] = json.loads(repo_resp.read())
            try:
                if perm_data['repos']['message']:
                    perm_data['repos'] = []
            except:
                pass
            identifier = perm_data['id']
        elif social_code == 'gp':
            perm_url = 'https://www.googleapis.com/plus/v1/people/me?access_token='+access_token
            perm_resp = urllib.urlopen(perm_url)
            perm_data = json.loads(perm_resp.read())
        elif social_code == 'so':
            requestkey = settings.SOCIALAUTH_STACKOVERFLOW_OAUTH_REQUESTKEY
            perm_url = 'https://api.stackexchange.com/2.2/me?site=stackoverflow&access_token=' + access_token + '&key=' + requestkey
            # perm_resp = urllib.urlopen(perm_url)
            perm_resp = requests.get(perm_url)
            # perm_resp = perm_resp
            perm_data = json.loads(perm_resp.content)
            skill_url = 'https://api.stackexchange.com/2.2/me/top-tags?site=stackoverflow&access_token=' + access_token + '&key=' + requestkey
            # skill_resp = urllib.urlopen(skill_url)
            skill_resp = requests.get(skill_url)
            skill_data = json.loads(skill_resp.content)
            if skill_data:
                perm_data['skilltags'] = skill_data

        email = ""
        if perm_data.has_key('email'):
            email = perm_data['email']
        elif perm_data.has_key('emails'):
            email = perm_data['emails'][0]['value']
        elif perm_data.has_key('emailAddress'):
            email = perm_data['emailAddress']
        user = get_account(social_code,identifier, email)
        first_name = ""
        last_name = ""
        if perm_data.has_key('first_name'):
            first_name = perm_data['first_name']
        elif perm_data.has_key('firstName'):
            first_name = perm_data['firstName']
        if perm_data.has_key('last_name'):
            last_name = perm_data['last_name']
        elif perm_data.has_key('lastName'):
            last_name = perm_data['lastName']

        if not perm_data.has_key('first_name') and not perm_data.has_key('last_name'):
            if perm_data.has_key('name'):
                name = perm_data['name']
                try:
                    if name.has_key('givenName') or name.has_key('familyName'):
                        first_name = name['givenName']
                        last_name = name['familyName']
                except:
                    name = name.split(' ')
                    first_name = name[0]
                    if len(name)>1:
                        last_name = name[-1]
            elif perm_data.has_key('items'):
                items = perm_data['items'][0]
                if items.has_key('display_name'):
                    name  = items['display_name'].split(' ')
                    first_name = name[0]
                    if len(name) > 1:
                        last_name = name[-1]

        if not user:
            user = User.objects.create_user(username = generate_random_username(),email = email, first_name = first_name, last_name = last_name, profile = Profile.objects.get(codename='candidate'))
            # user.set_unusable_pasword()
        candidate,candidate_created = Candidate.objects.get_or_create(user = user)
        if(perm_data.has_key('gender')):
            try:
                gender = Gender.objects.get(codename = perm_data['gender'])
            except:
                gender = None
            if not candidate.gender and gender:
                candidate.gender = gender
            elif candidate.gender != gender:
                review['gender'] = str(gender)
        if not candidate.first_name:
            candidate.first_name = candidate.user.first_name

        if not candidate.last_name:
            candidate.last_name = candidate.user.last_name

        if(perm_data.has_key('birthday')):
            if social_code == 'gp':
                bday = perm_data['birthday'].split('-')
                if int(bday[0]) == 0 and perm_data.has_key('ageRange'):
                    bday[0] = date.today().year - perm_data['ageRange']['min']
                if int(bday[0]) == 0:
                    pass
                elif len(bday) == 3 and not candidate.birthday:
                    candidate.birthday = date(int(bday[0]), int(bday[1]), int(bday[2]))
                elif candidate.birthday != date(int(bday[0]), int(bday[1]), int(bday[2])):
                    review['birthday'] = str(date(int(bday[0]), int(bday[1]), int(bday[2])))
            else:
                bday = perm_data['birthday'].split('/')
                if len(bday) == 3 and not candidate.birthday:
                    candidate.birthday = date(int(bday[2]),int(bday[0]),int(bday[1]))
                elif len(bday) == 3 and candidate.birthday != date(int(bday[2]),int(bday[0]),int(bday[1])):
                    review['birthday'] = str(date(int(bday[2]),int(bday[0]),int(bday[1])))    
        if(perm_data.has_key('education')):
            for school in perm_data['education']:
                schoolname = ''
                schoolyear = None
                schooltype = ''
                schoolarea = ''
                schooldegree = ''
                schoolstatus = ''
                schoolcity = ''
                schoolstate = ''
                schoolcountry = ''
                if school.has_key('school'):
                    schoolname = school['school']['name'] or ''
                    request_slug = str(school['school']['id']) + '/?fields=location&access_token=' + auth_data['access_token']
                    subresp = get_fb_web_response(request_slug)
                    if subresp.getcode() == 200:
                        subdata = json.loads(subresp.read())
                        if subdata.has_key('location'):
                            if subdata['location'].has_key('city'):
                                schoolcity = subdata['location']['city']
                            if subdata['location'].has_key('state'):
                                schoolstate = subdata['location']['state']
                            if subdata['location'].has_key('country'):
                                schoolcountry = subdata['location']['country']
                                schoolcountry = Country.objects.filter(name__iexact=schoolcountry)
                                if schoolcountry:
                                    schoolcountry = schoolcountry[0]
                if school.has_key('year'):
                    schoolyear = datetime(int(school['year']['name']),1,1)
                    if int(school['year']['name']) < datetime.now().year:
                        schoolstatus = Academic_Status.objects.get(codename = 'complete')
                    else:
                        schoolstatus = Academic_Status.objects.get(codename = 'progress')
                if school['type'] == 'High School':
                    schooltype = Degree.objects.get(codename = 'higher_school')
                elif school['type'] == 'College':
                    schooltype = Degree.objects.get(codename = 'graduate')
                elif school['type'] == 'Graduate School':
                    schooltype = Degree.objects.get(codename = 'pg')
                else:
                    schooltype = Degree.objects.get(codename = 'other')
                if school.has_key('degree'):
                    schooldegree = school['degree']['name']
                if school.has_key('concentration'):
                    schoolarea = ','.join([concentration['name'] for concentration in school['concentration']])
                academic,academic_created=Academic.objects.get_or_create(candidate=candidate, school = schoolname, end_date=schoolyear, degree=schooltype, area = schoolarea, course_name = schooldegree)
                if academic and academic.status!=schoolstatus:
                    academic.status = schoolstatus
                if schoolcity and not academic.city:
                    academic.city = schoolcity
                if schoolstate and not academic.state:
                    academic.state = schoolstate
                if schoolcountry and not academic.country:
                    academic.country = schoolcountry
                academic.save()
        if(perm_data.has_key('work')):
            for work in perm_data['work']:
                workname = ''
                workstart = None
                workend = None
                workongoing = False 
                worktype = ''
                workdegree = ''
                workcity = ''
                workstate = ''
                workcountry = ''
                if work.has_key('employer'):
                    workname = work['employer']['name'] or ''
                    request_slug = str(work['id']) + '/?fields=location&access_token=' + auth_data['access_token']
                    subresp = get_fb_web_response(request_slug)
                    if subresp.getcode() == 200:
                        subdata = json.loads(subresp.read())
                        if subdata.has_key('location'):
                            if subdata['location'].has_key('city'):
                                workcity = subdata['location']['city']
                            if subdata['location'].has_key('state'):
                                workstate = subdata['location']['state']
                            if subdata['location'].has_key('country'):
                                workcountry = subdata['location']['country']
                                try:
                                    workcountry = Country.objects.get(Q(name__iexact=workcountry)|Q(iso2_code__iexact=workcountry))
                                except:
                                    workcountry = None
                if work.has_key('start_date'):
                    datesplit = work['start_date'].split('-')
                    if len(datesplit) == 3:
                        workstart = datetime(int(datesplit[0]),int(datesplit[1]),int(datesplit[2]))
                if work.has_key('end_date'):
                    datesplit = work['end_date'].split('-')
                    if len(datesplit) == 3:
                        workend = datetime(int(datesplit[0]),int(datesplit[1]),int(datesplit[2]))
                else:
                    workongoing = True
                if work.has_key('position'):
                    worktype = work['position']['name']
                if work.has_key('description'):
                    workdegree = work['description']['name']
                if work.has_key('projects'):
                    for project in work['projects']:
                        projectname = project['name']
                        projectdescription = project['description']
                        project, project_created = Project.objects.get_or_create(name=projectname,description = projectdescription, candidate = candidate)
                experience, experience_created = Expertise.objects.get_or_create(candidate=candidate, company = workname, employment = worktype, tasks = workdegree)
                experience.present = workongoing
                if workstart:
                    experience.start_date = workstart
                if workend:
                    experience.end_date = workend
                if workcity and not experience.city:
                    experience.city = workcity
                if workstate and not experience.state:
                    experience.state = workstate
                if workcountry and not experience.country:
                    experience.country = workcountry
                experience.save()
        elif(perm_data.has_key('positions')):
            for work in perm_data['positions']['values']:
                workname = ''
                workstart = None
                workend = None
                workongoing = False
                worktype = ''
                workdegree = ''
                workcity = ''
                workstate = ''
                workcountry = '' 
                if work.has_key('title'):
                    worktype = work['title']
                if work.has_key('isCurrent'):
                    workongoing = work['isCurrent']
                if work.has_key('startDate'):
                    year = ""
                    month = ""
                    if work['startDate'].has_key('year'):
                        year = work['startDate']['year']
                    if work['startDate'].has_key('month'):
                        month = work['startDate']['month']
                    if year and month:
                        workstart = datetime(int(year),int(month),1)
                    elif year:
                        workstart = datetime(int(year),1,1)
                if work.has_key('company'):
                    if work['company'].has_key('name'):
                        workname = work['company']['name']
                if work.has_key('location'):
                    if work['location'].has_key('country'):
                        try:
                            workcountry = Country.objects.get(Q(name__iexact=work['location']['country']['name'])|Q(iso2_code__iexact=work['location']['country']['code']))
                        except:
                            workcountry = None
                    if work['location'].has_key('name'):
                        workcity = work['location']['name'].split(',')[0]
                experience, experience_created = Expertise.objects.get_or_create(candidate=candidate, company = workname, employment = worktype, tasks = workdegree)
                experience.present = workongoing
                if workstart:
                    experience.start_date = workstart
                if workend:
                    experience.end_date = workend
                if workcity and not experience.city:
                    experience.city = workcity
                if workstate and not experience.state:
                    experience.state = workstate
                if workcountry and not experience.country:
                    experience.country = workcountry
                experience.save()       

        if(perm_data.has_key('languages')):
            for language in perm_data['languages']:
                languages = Language.objects.filter(name__iexact = language['name'])
                if languages:
                    language, language_created = CV_Language.objects.get_or_create(candidate = candidate, language=languages[0])
        if(perm_data.has_key('picture')) and candidate.user.photo.name == settings.PHOTO_USER_DEFAULT:
            if not perm_data['picture']['data']['is_silhouette']:
                result = candidate.user.get_remote_image(perm_data['picture']['data']['url'])
        elif perm_data.has_key('image') and candidate.user.photo.name == settings.PHOTO_USER_DEFAULT:
            candidate.user.get_remote_image(perm_data['image']['url'].split('?sz=')[0]+'?sz=200')
        elif perm_data.has_key('pictureUrl') and candidate.user.photo.name == settings.PHOTO_USER_DEFAULT:
            candidate.user.get_remote_image(perm_data['pictureUrl'])
        if perm_data.has_key('bio'):
            candidate.objective = perm_data['bio']
        if perm_data.has_key('repos'):
            for repo in perm_data['repos']:
                if repo['fork'] == False:
                    description = repo['description']
                    if not description:
                        description = ''
                    project, project_created = Project.objects.get_or_create(candidate=candidate, name=repo['name'], description=description)
        if perm_data.has_key('organizations'):
            for organization in perm_data['organizations']:
                if organization['type'] == 'work':
                    organizationname = ''
                    organizationstart = None
                    organizationend = None
                    organizationongoing = False 
                    organizationtype = ''
                    organizationdegree = ''
                    organizationcity = ''
                    organizationstate = ''
                    organizationcountry = ''
                    if organization.has_key('name'):
                        organizationname = organization['name'] or ''
                    if organization.has_key('startDate'):
                        organizationstart = datetime(int(organization['startDate']),1,1)
                    if organization.has_key('endDate'):
                        organizationend = datetime(int(organization['endDate']),1,1)
                    else:
                        organizationongoing = True
                    if organization.has_key('title'):
                        organizationtype = organization['title']
                    if organization.has_key('description'):
                        organizationdegree = organization['description']['name']
                    experience, experience_created = Expertise.objects.get_or_create(candidate=candidate, company = organizationname, employment = organizationtype, tasks = organizationdegree)
                    experience.present = organizationongoing
                    if organizationstart:
                        experience.start_date = organizationstart
                    if organizationend:
                        experience.end_date = organizationend
                    experience.save()
                elif organization['type'] == 'school':
                    organizationname = ''
                    organizationstart = None
                    organizationend = None
                    organizationtype = ''
                    organizationarea = ''
                    organizationdegree = ''
                    organizationstatus = ''
                    organizationcity = ''
                    organizationstate = ''
                    organizationcountry = ''
                    if organization.has_key('name'):
                        organizationname = organization['name'] or ''
                    if organization.has_key('startDate'):
                        organizationstart = datetime(int(organization['startDate']),1,1)


                    if organization.has_key('endDate'):
                        organizationend = datetime(int(organization['endDate']),1,1)
                        if int(organization['endDate']) < datetime.now().year:
                            organizationstatus = Academic_Status.objects.get(codename = 'complete')
                        else:
                            organizationstatus = Academic_Status.objects.get(codename = 'progress')
                    else:
                        organizationstatus = Academic_Status.objects.get(codename = 'progress')
                    if organization.has_key('title'):
                        organizationdegree = organization['title']
                    academic,academic_created=Academic.objects.get_or_create(candidate=candidate, school = organizationname, end_date=organizationend, start_date=organizationstart, course_name = organizationdegree)
                    if academic and academic.status!=organizationstatus:
                        academic.status = organizationstatus
                    academic.save()
        if perm_data.has_key('items'):
            item = perm_data['items'][0]
            # if item.has_key('website_url') and item['website_url']:
            #     if not candidate.website:
            #         candidate.website = item['website_url']
            #     elif candidate.website != item['website_url']:
            #         review['website'] = item['website_url']
            # else:
            #     if not candidate.website:
            #         candidate.website = "http://stackoverflow.com/users/story/"+item['user_id']
            #     elif candidate.website != item['website_url']:
            #         review['website'] = "http://stackoverflow.com/users/story/"+item['user_id']
            if item.has_key('profile_image') and not candidate.user.photo.name == settings.PHOTO_USER_DEFAULT:
                candidate.user.get_remote_image(item['profile_image'].split('?s=')[0] + '?s=200')
        if perm_data.has_key('skilltags'):
            skills = ""
            skills += ','.join([skill['tag_name'] for skill in perm_data['skilltags']['items']])
            if not candidate.skills:
                candidate.skills = skills
            else:
                candidate_skills = candidate.skills.split(',')
                for skill in skills.split(','):
                    if skill and not skill in candidate_skills:
                        candidate.skills += ',' + skill
        if perm_data.has_key('location'):
            if perm_data['location'].has_key('country'):
                if perm_data['location']['country'].has_key('code'):
                    try:
                        country = Country.objects.get(iso2_code__iexact=perm_data['location']['country']['code'])
                    except:
                        country = None
                    if country and not candidate.nationality:
                        candidate.nationality = country
            if perm_data['location'].has_key('name') and not candidate.city:
                candidate.city = perm_data['location']['name'].split(',')[0]
        # if perm_data.has_key
        candidate.save()
        curriculum, curriculum_created = Curriculum.objects.get_or_create(candidate = candidate)          
        social, social_created = SocialAuth.objects.get_or_create(user=user, identifier = identifier, social_code = social_code)
        social.oauth_token = access_token
        social.save()
        if social_created or candidate_created:
            perm_data
            # Get Profile and append
        if not vacancy_id:
            from django.contrib.auth import login
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request,user)
            return redirect('common_redirect_after_login')
        job = Vacancy.objects.filter(id=vacancy_id )
        if job:
            job = job[0]
        else:
            messages.error(request,'Job Opening does not exist')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
        if not job.status.codename=='open' or job.public_cvs == False:
            messages.error(request,'This Job is currently not available for application')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
        
        application = Postulate.objects.filter(vacancy = job, candidate = candidate)
        if not candidate_created and application:
            messages.error(request,'Already Applied')
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)
            
            #redirect back to job application
            # raise ValueError(request.session['subdomain_redirect_type'])
            # redirect_type = request.session.pop('subdomain_redirect_type')
            # if redirect_type == 1:
            #     callback_url = job.company.geturl()
            # elif redirect_type == 2:
            #     callback_url = job.company.getsubdomainurl()
            # else:
            #     callback_url = ''
            # callback_url += reverse('vacancies_apply_via_social', kwargs={'vacancy_id': vacancy_id, 'social_code': social_code})
        request.session['socialUser'] = social.id
        # raise ValueError(request.session['socialUser'])
        request.session['review'] = str(review)
        return redirect('vacancies_apply_via_social', vacancy_id = vacancy_id, social_code = social_code)
    messages.error(request,'Failed to acquire authentication')
    return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)

        
