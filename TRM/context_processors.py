from __future__ import absolute_import
from django.conf import settings
from django.shortcuts import get_object_or_404
from candidates.models import Candidate
from companies.models import Recruiter, Company
from common.models import Subdomain
from payments.models import Package, ServiceCategory
from activities.models import Notification
from django.utils.translation import gettext as _
from TRM import settings
from TRM.settings import LOGO_COMPANY_DEFAULT, LOGO_CANDIDATE_DEFAULT, ROOT_DOMAIN
import json
from django.db.models import Q
# from zinnia import settings as zinnia_settings
def debug_mode(request):
    return {'debug_mode': settings.DEBUG}

def project_name(request):
    return {'project_name': settings.PROJECT_NAME, 'HOSTED_URL':settings.HOSTED_URL}

"""
def candidate_full_name(request):
    full_name = _('Your Name')
    if request.user.is_authenticated:
        user_profile = request.user.profile.codename
        if user_profile == 'candidate':
            candidate = get_object_or_404(Candidate, user=request.user)
            full_name = '%s %s' % (candidate.first_name, candidate.last_name)
    return {'candidate_full_name': full_name}
"""

def candidate_full_name(request):
    full_name = _('Your Name')

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

        if profile and getattr(profile, 'codename', '') == 'candidate':
            try:
                candidate = Candidate.objects.get(user=request.user)
                full_name = f"{candidate.first_name} {candidate.last_name}"
            except Candidate.DoesNotExist:
                pass

    return {'candidate_full_name': full_name}

def logo_company_default(request):
    return {'LOGO_COMPANY_DEFAULT': LOGO_COMPANY_DEFAULT}

def logo_candidate_default(request):
    return {'LOGO_CANDIDATE_DEFAULT': LOGO_CANDIDATE_DEFAULT}

def subdomain(request):
    fqdn = request.get_host().split(':')[0]
    domain_parts = fqdn.split('.')
    if len(domain_parts)>=3 and domain_parts[-2] == 'spotaxis' and domain_parts[-3] == 'demo':
        if len(domain_parts) > 3:
            subdomain = domain_parts[0]
        elif len(domain_parts)<4:
            subdomain = None
            return {'active_subdomain':None,'active_host':None,'isRoot':True,'hasCNAME':False}
        else:
            subdomain=None
        b=subdomain
        try:
            subdomain = Subdomain.objects.get(
                    Q(cname=fqdn) |
                    Q(slug=subdomain)
                )
        except:
            subdomain = None
    else:
        if len(domain_parts) > 2 and ROOT_DOMAIN == domain_parts[1]:
            subdomain = domain_parts[0]
        elif len(domain_parts) < 3 and ROOT_DOMAIN == domain_parts[0]:
            subdomain = None
            return {'active_subdomain':None,'active_host':None,'isRoot':True,'hasCNAME': False}
        else:
            subdomain = None
        b = subdomain
        try:
            subdomain = Subdomain.objects.get(
                    Q(cname=fqdn) |
                    Q(slug=subdomain)
                )
        except:
            subdomain = None
    hasCNAME = False
    if subdomain:
        slug = subdomain.slug
        active_host = None
        if subdomain.cname:
            hasCNAME = True
            active_host = subdomain.cname
        elif subdomain.slug:
            active_host = subdomain.slug + '.' + ROOT_DOMAIN + '.com'
    else:
        slug=None
        active_host = None
    return {'active_subdomain': slug,'active_host':active_host, 'isRoot':False, 'hasCNAME':hasCNAME}

"""
def user_profile(request):
    if request.user.is_authenticated:
        user_profile = request.user.profile.codename
    else:
        user_profile = None
    try:
        company = Company.objects.get(subdomain__slug=subdomain(request)['active_subdomain'])
    except:
        company=None
    try:
        recruiter = Recruiter.objects.get(user=request.user,company=company, user__is_active=True)
    except:
        recruiter = None
    # print (recruiter)
    # print(subdomain(request)['active_subdomain'])
    # print ('recruiter')
    #added a new line without mentioning zinnia
    return {'user_profile': user_profile,'recruiter': recruiter, 'settings':settings}
    # return {'user_profile': user_profile,'recruiter': recruiter, 'settings':settings, 'zinnia_settings':zinnia_settings}

"""

def user_profile(request):
    user_profile = None
    recruiter = None
    company = None

    try:
        active_subdomain = subdomain(request)['active_subdomain']
        if active_subdomain:
            company = Company.objects.get(subdomain__slug=active_subdomain)
    except Company.DoesNotExist:
        company = None

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile:
            user_profile = profile.codename
        try:
            recruiter = Recruiter.objects.get(user=request.user, company=company, user__is_active=True)
        except Recruiter.DoesNotExist:
            recruiter = None

    return {
        'user_profile': user_profile,
        'recruiter': recruiter,
        'settings': settings
    }

def notifications(request):
    if request.user.is_authenticated:
        msgs = Notification.objects.filter(user=request.user)
        try:
            request.session['last_notification'] = msgs.latest('id').id
        except:
            request.session['last_notification'] = 0
        return {'notifications': msgs[:100],'unseen_notification_count':Notification.objects.filter(seen=False, user = request.user).count()}
    else:
        return {}

def packages(request):
    return {
        'packages':Package.objects.all(),
        'service_categories':ServiceCategory.objects.all()
    }