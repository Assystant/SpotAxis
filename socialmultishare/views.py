
from __future__ import absolute_import
from __future__ import print_function
import decimal
import os
import traceback
import json
import random
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import requests
import hmac
import hashlib
import oauth2 as oauth
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.template import RequestContext
from django.utils.translation import gettext as _
from .models import socialmultishareoauth as social_oauth
from django.contrib.auth import get_user
from vacancies.models import Vacancy
from linkedin import linkedin

@login_required
def share_to_social_media(request,vacancy_id=None):
    """#check login and check vacancy id against the user
    # GET ALL USER ACCESS TOKENS"""
    context={}
    context['vacancy_id'] = vacancy_id
    try:
        tokens = social_oauth.objects.filter(user=request.user)
        tokencount = social_oauth.objects.filter(user=request.user).count()
    except:
        tokens = ""
    if tokens:
        context['tokens'] = tokens
        context['user'] = request.user
        context['tokencount'] = tokencount
        fbtoken = social_oauth.objects.filter(user=request.user,media = 'FB')
        if fbtoken:
            if fbtoken[0].oauth_token and verify_fb_token(fbtoken[0]) and verify_fb_scopes(fbtoken[0]):
                context['fbtoken'] = fbtoken[0]
                context['fbgroups'] = get_fb_groups(context['fbtoken'])
                context['fbpages'] = get_fb_pages(context['fbtoken'])
            else:
                context['fbtoken'] = ""
                context['fbgroups'] = ""
                context['fbpages'] = ""
                context['tokencount']-=1
                messages.warning(request, _('Reauthorisation required for Facebook'))
        else:
            context['fbtoken'] = ""
        twtoken = tokens.filter(media = 'TW')
        if twtoken:
            if verify_tw_token(twtoken[0]):
                context['twtoken'] = twtoken[0]
            else:
                context['twtoken'] = ""
                messages.warning(request, _('Reauthorisation required for Twitter'))
                context['tokencount']-=1
        else:
            context['twtoken'] = ""
        litoken = tokens.filter(media = 'LI')
        if litoken:
            if verify_li_token(litoken[0]):
                context['litoken'] = litoken[0]
                li_pagesdata = get_li_pages(context['litoken'])
                if li_pagesdata['_total'] > 0 :
                    context['lipages'] = li_pagesdata['values']
                else:
                    context['lipages'] = ""
            else:
                context['litoken'] = ""
                context['lipages'] = ""
                messages.warning(request, _('Reauthorisation required for Linkedin'))
                context['tokencount']-=1
        else:
            context['litoken'] = ""
            context['lipages'] = ""
    else:
        context['tokencount'] = 0
        context['fbtoken'] = ""
        context['twtoken'] = ""
        context['litoken'] = ""
    if request.method == "POST":
        medialist = request.POST.getlist('socialmedia[]')
        fbgroups = request.POST.getlist('fbgroups[]')
        fbpages = request.POST.getlist('fbpages[]')
        lipages = request.POST.getlist('lipages[]')
        message = request.POST.get('message')
        posttofb = False
        posttotw = False
        posttoli = False
        if medialist:
            try:
                index = medialist.index('fb')
                posttofb = True
            except ValueError:
                pass
            try:
                index = medialist.index('tw')
                posttotw = True
            except ValueError:
                pass
            try:
                index = medialist.index('li')
                posttoli = True
            except ValueError:
                pass
            if posttofb and context['fbtoken']:
                for group in fbgroups:
                    group = group.strip('groupid-')
                    a=posttofbgroup(context['fbtoken'], message, group)
                for page in fbpages:
                    page = page.strip('pageid-')
                    a=posttofbpage(context['fbtoken'], message, page)
                if request.POST.get('fbprofile'):
                    a=posttofbprofile(context['fbtoken'],message)
                messages.success(request, _('Job shared on Facebook'))
            if posttotw and context['twtoken']:
                posttotwitter(context['twtoken'], message)
                messages.success(request, _('Job shared on Twitter'))
            if posttoli and context['litoken']:
                for page in lipages:
                    page = page.strip('pageid-')
                    a=posttolipage(context['litoken'], message, page)
                if request.POST.get('liprofile'):
                    a=posttoliprofile(context['litoken'], message)
                messages.success(request, _('Job shared on Linkedin'))
            return redirect(reverse('vacancies_get_vacancy_details',args = [vacancy_id]))
            
    # if request.post check and validate, post and redirect
    return render(request, 'socialmultishare.html', context)

@login_required
def connect_to_twitter(request,vacancy_id=None):
    consumer_key = settings.SOCIALMULTISHARE_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_TWITTER_OAUTH_SECRET
    callbackuri = settings.HOSTED_URL + str(reverse('socialmultishare_connect_to_twitter',args=[vacancy_id]))
    request_token_url = 'https://api.twitter.com/oauth/request_token?oauth_callback='+callbackuri
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    
    if not request.GET.get('oauth_verifier'):
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urllib.parse.parse_qsl(content))
        return redirect(authorize_url+"?oauth_token="+request_token['oauth_token'])
    elif request.GET.get('oauth_verifier'):
        oauth_token = request.GET.get('oauth_token')
        oauth_verifier = request.GET.get('oauth_verifier')
        if oauth_token and oauth_verifier:
            # resp = urllib.urlopen(access_token_url+"?oauth_verifier="+oauth_verifier+"&oauth_token="+oauth_token)
            resp,content = client.request(access_token_url+"?oauth_verifier="+oauth_verifier+"&oauth_token="+oauth_token)
            # raise ValueError()
            if resp['status'] == '200':
                data = dict(urllib.parse.parse_qsl(content))
                print(resp)
                # print(resp.read())
                # data=str(resp.read())
                print(data)

                # raise ValueError()
                vacancy = Vacancy.objects.filter(id = vacancy_id)
                if vacancy:
                    user = vacancy[0].user
                    socialauth,created = social_oauth.objects.get_or_create(
                                media = 'TW',
                                user = user,
                            )
                    socialauth.oauth_token=str(data['oauth_token'])
                    socialauth.oauth_secret = str(data['oauth_token_secret'])
                    socialauth.identifier = str(data['user_id'])
                    socialauth.save()

    return redirect(reverse('socialmultishare_share_to_social_media', args=[vacancy_id]))

@login_required
def connect_to_facebook(request,vacancy_id=None):

    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    #check login and check vacancy id to decide redirect uri
    fbredirecturi = settings.HOSTED_URL + str(reverse('socialmultishare_connect_to_facebook',args=[vacancy_id]))
    if not request.GET.get('code'):
        return redirect("https://www.facebook.com/dialog/oauth?client_id="+consumer_key+"&redirect_uri="+fbredirecturi+"&scope=user_managed_groups,publish_actions,manage_pages,publish_pages")
    else:
        if request.GET['code']:
            request_token_url = "https://graph.facebook.com/v2.3/oauth/access_token?client_id="+consumer_key+"&redirect_uri="+fbredirecturi+"&client_secret="+consumer_secret+"&code="+request.GET['code']
            resp = urllib.request.urlopen(request_token_url)
            # return redirect(request_token_url)
            if resp.getcode() == 200:
                data = json.loads(resp.read())
                if data['access_token']:
                    vacancy = Vacancy.objects.filter(id = vacancy_id)
                    if vacancy:
                        user = vacancy[0].user
                        socialauth,created = social_oauth.objects.get_or_create(
                            media = 'FB',
                            user = user,
                        )
                        socialauth.oauth_token = str(data['access_token'])
                        url = "https://graph.facebook.com/debug_token?input_token="+str(data['access_token'])+"&access_token="+consumer_key+"|"+consumer_secret
                        resp = urllib.request.urlopen(url)
                        if resp.getcode() == 200:
                            Data = json.loads(resp.read())
                            if Data['data']:
                                socialauth.identifier = str(Data['data']['user_id'])
                        socialauth.save()
    return redirect(reverse('socialmultishare_share_to_social_media', args=[vacancy_id]))

@login_required
def connect_to_linkedin(request,vacancy_id=None):
    request.session['vid'] = vacancy_id
    consumer_key = settings.SOCIALMULTISHARE_LINKEDIN_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_LINKEDIN_OAUTH_SECRET
    return_url = settings.HOSTED_URL + str(reverse('socialmultishare_connect_to_linkedin',args="1"))
    authentication = linkedin.LinkedInAuthentication(consumer_key,consumer_secret,return_url, ['r_basicprofile','r_emailaddress','rw_company_admin','w_share'])
    application = linkedin.LinkedInApplication(authentication)
    if not request.GET.get('code') and not request.GET.get('error'):
        return redirect(authentication.authorization_url)
    elif request.GET.get('code'):
        authentication.authorization_code = request.GET['code']
        data = authentication.get_access_token()
        if 'vid' in request.session:
            vacancy_id = request.session['vid']
            vacancy = Vacancy.objects.filter(id = vacancy_id)
            if vacancy:
                user = vacancy[0].user
                socialauth,created = social_oauth.objects.get_or_create(
                            media = 'LI',
                            user = user,
                        )
                socialauth.oauth_token=str(data[0])
                socialauth.save()
    return redirect('/vacante/share/'+ vacancy_id + '/')

def debug_fb_token(fbtoken):
    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    url = "https://graph.facebook.com/debug_token?input_token="+str(fbtoken.oauth_token)+"&access_token="+consumer_key+"|"+consumer_secret
    resp = urllib.request.urlopen(url)
    Data = json.loads(resp.read())
    return Data

def verify_fb_token(fbtoken):
    token_data = debug_fb_token(fbtoken)
    try:
        if token_data['data']['is_valid']:
            if fbtoken.identifier == token_data['data']['user_id']:
                return True
    except:
        pass
    return False

def verify_fb_scopes(fbtoken):
    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    url = "https://graph.facebook.com/me/permissions?access_token="+str(fbtoken.oauth_token)+"&appsecret_proof="+str(get_fb_app_secret_proof(str(fbtoken.oauth_token)))
    resp = urllib.request.urlopen(url)
    Data = json.loads(resp.read())
    for data in Data['data']:
        if data['status']!='granted':
            return False
    return True
def verify_tw_token(twtoken):
    consumer_key = settings.SOCIALMULTISHARE_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_TWITTER_OAUTH_SECRET
    token = oauth.Token(twtoken.oauth_token,twtoken.oauth_secret)
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer,token)
    post_url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    resp, content = client.request(post_url,'GET')
    if resp['status'] == '200':
        return True
    else:
        return False
    
def verify_li_token(litoken):
    token = litoken.oauth_token
    post_url = "https://api.linkedin.com/v1/people/~?oauth2_access_token="+token+"&format=json"
    r = urllib.request.urlopen(post_url)
    if r.getcode() == 200:
        return True
    else:
        return False

def get_page_token(fbtoken,pageid):
    url = "https://graph.facebook.com/"+str(pageid)+"/?fields=access_token&access_token="+str(fbtoken.oauth_token)+"&appsecret_proof="+str(get_fb_app_secret_proof(str(fbtoken.oauth_token)))
    resp = urllib.request.urlopen(url)
    Data = json.loads(resp.read())
    return Data['access_token']

def get_fb_app_access_token():
    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    request_token_url = "https://graph.facebook.com/oauth/access_token?client_id="+consumer_key+"&client_secret"+consumer_secret+"&grant_type=client_credentials"
    resp = urllib.request.urlopen(request_token_url)
    if resp.getcode() == 200:
        data = json.loads(resp.read())
        return data['access_token']
    else:
        return None

def get_fb_app_secret_proof(access_token):
    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    h = hmac.new(
        consumer_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()

def get_fb_groups(fbtoken):
    request_token_url = str("https://graph.facebook.com/"+str(fbtoken.identifier)+"/groups/?appsecret_proof="+str(get_fb_app_secret_proof(str(fbtoken.oauth_token)))+"&access_token="+str(fbtoken.oauth_token))
    resp = urllib.request.urlopen(str(request_token_url))
    if resp.getcode() == 200:
        data = json.loads(resp.read())
        return data['data']
    else:
        return None   
def get_fb_pages(fbtoken):
    consumer_key = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET
    request_token_url = "https://graph.facebook.com/me/accounts/?access_token="+fbtoken.oauth_token+"&appsecret_proof="+str(get_fb_app_secret_proof(str(fbtoken.oauth_token)))
    request_token_url = str(request_token_url)
    resp = urllib.request.urlopen(request_token_url)
    if resp.getcode() == 200:
        data = json.loads(resp.read())
        return data['data']
    else:
        return None    
def get_li_pages(litoken):
    url = 'https://api.linkedin.com/v1/companies?format=json&is-company-admin=true&oauth2_access_token='+litoken.oauth_token
    resp = urllib.request.urlopen(url)
    if resp.getcode() == 200:
        data = json.loads(resp.read())
        return data
    else:
        return None
def get_li_groups(litoken):
    application = linkedin.LinkedInApplication(litoken.oauth_token)
    url = 'https://api.linkedin.com/v1/companies?format=json&is-company-admin=true&oauth2_access_token='+litoken.oauth_token
    resp = urllib.request.urlopen(url)
    if resp.getcode() == 200:
        data = json.loads(resp.read())
        return data
    else:
        return None
def posttofbprofile(fbtoken, message):
    post_url = "https://graph.facebook.com/me/feed/"
    token = fbtoken.oauth_token
    r = requests.post(
        post_url,
        data = {
                'message': message,
                'access_token': token,
                'appsecret_proof': str(get_fb_app_secret_proof(str(token))),
            }
        )
    print((r.status_code))
    # raise ValueError(r.reason)
    return r
def posttofbgroup(fbtoken, message, groupid):
    request_token_url = "https://graph.facebook.com/"+str(groupid)+"/feed/"
    r = requests.post(
        request_token_url, 
        data={
            'message': message,
            'access_token': str(fbtoken.oauth_token),
            'appsecret_proof': str(get_fb_app_secret_proof(str(fbtoken.oauth_token))),
            }
        )
    print((r.status_code))
    return r
def posttofbpage(fbtoken, message, pageid):
    request_token_url = "https://graph.facebook.com/"+str(pageid)+"/feed/"
    pagetoken = get_page_token(fbtoken,pageid)
    r = requests.post(
        request_token_url, 
        data={
            'message': message,
            'access_token': str(pagetoken),
            'appsecret_proof': str(get_fb_app_secret_proof(str(pagetoken))),
            }
        )
    if r.status_code == 403:
        r = requests.post(
            request_token_url, 
            data={
                'message': message,
                'access_token': str(fbtoken.oauth_token),
                'appsecret_proof': str(get_fb_app_secret_proof(str(fbtoken.oauth_token))),
                }
            )
    print((r.status_code))
    return r
def posttotwitter(twtoken, message):
    consumer_key = settings.SOCIALMULTISHARE_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALMULTISHARE_TWITTER_OAUTH_SECRET
    token = oauth.Token(twtoken.oauth_token,twtoken.oauth_secret)
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer,token)
    post_url = "https://api.twitter.com/1.1/statuses/update.json"
    resp, content = client.request(post_url,'POST',"status="+message)
    if resp['status'] == '200':
        return True
    else:
        return False
def posttolipage(litoken, message, pageid):
    token = litoken.oauth_token
    post_url = "https://api.linkedin.com/v1/companies/"+pageid+"/shares?oauth2_access_token="+token+"&format=json"
    body = json.dumps({
        "visibility": {
            "code": "anyone"
            },
            "comment": message
        })
    r = requests.post(
        post_url,
        data = body,
        headers={"content-type":"application/json"}
        )
    print((r.status_code))
    return r
def posttoliprofile(litoken, message):
    token = litoken.oauth_token
    post_url = "https://api.linkedin.com/v1/people/~/shares?oauth2_access_token="+token+"&format=json"
    body = json.dumps({
        "visibility": {
            "code": "anyone"
            },
            "comment": message
        })
    r = requests.post(
        post_url,
        data = body,
        headers={"content-type":"application/json"}
        )
    print((r.status_code))
    return r
