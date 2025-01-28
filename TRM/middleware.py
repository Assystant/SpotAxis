# -*- coding: utf-8 -*-
# from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from __future__ import absolute_import
from django.shortcuts import render
# from social.exceptions import AuthCanceled
from django.utils.cache import patch_vary_headers
from django.conf import settings

from TRM.settings import SUBDOMAIN_URLCONF, ROOT_DOMAIN, SITE_SUFFIX, SUPPORT_URLCONF, BLOG_URLCONF
from django.db.models import Q
from django.core.urlresolvers import set_urlconf, reverse, resolve
from django.http import Http404, HttpResponseRedirect
import time
from common.models import Subdomain
from TRM.context_processors import subdomain as check_subdomain
# class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
#     def process_exception(self, request, exception):
#         if type(exception) == AuthCanceled:
#             return render(request, "login.html", {})
#         else:
#             pass

class SubdomainMiddleware:
    def process_request(self,request):
        fqdn = request.get_host().split(':')[0]
        domain_parts = fqdn.split('.')
        # isSupport = False
        # isBlog = False
        # if len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[0] == 'blog':
        #     if len(domain_parts)>3:
        #         subdomain = domain_parts[0]
        #     else:
        #         subdomain = None
        #     try:
        #         subdomain = Subdomain.objects.get(
        #                 Q(cname=fqdn) |
        #                 Q(slug=subdomain)
        #             )
        #     except:
        #         subdomain = None
        #     isBlog = True
        # elif len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[0] == 'support':
        # if len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[0] == 'support':
        #     if len(domain_parts)>3:
        #         subdomain = domain_parts[0]
        #     else:
        #         subdomain = None
        #     try:
        #         subdomain = Subdomain.objects.get(
        #                 Q(cname=fqdn) |
        #                 Q(slug=subdomain)
        #             )
        #     except:
        #         subdomain = None
        #     isSupport = True
        # elif len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[-3] == 'demo':
        if len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[-3] == 'demo':
            if len(domain_parts)>3:
                subdomain = domain_parts[0]
            else:
                subdomain = None
            try:
                subdomain = Subdomain.objects.get(
                        Q(cname=fqdn) |
                        Q(slug=subdomain)
                    )
            except:
                subdomain = None
        else:
            if len(domain_parts) > 2 and ROOT_DOMAIN in domain_parts:
                subdomain = domain_parts[0]
            else:
                subdomain = None
            try:
                subdomain = Subdomain.objects.get(
                        Q(cname=fqdn) |
                        Q(slug=subdomain)
                    )
            except:
                subdomain = None
        # print(subdomain)
        # print(fqdn)
        # print(SITE_SUFFIX.strip('.').strip('/'))
        # if not isSupport and not isBlog:
        # if not isSupport:
        if subdomain:
            set_urlconf(SUBDOMAIN_URLCONF)
            request.urlconf = SUBDOMAIN_URLCONF
        elif fqdn!= SITE_SUFFIX.strip('.').strip('/'):
            # print('raising error')
            raise Http404()
            # print(request.urlconf)
        # elif isSupport:
        #     set_urlconf(SUPPORT_URLCONF)
        #     request.urlconf = SUPPORT_URLCONF
        # elif isBlog:
        #     set_urlconf(BLOG_URLCONF)
        #     request.urlconf = BLOG_URLCONF

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        return response


class MediumMiddleware:
    def process_request(self, request):
        subdomain_data = check_subdomain(request)
        if subdomain_data['active_subdomain'] or subdomain_data['hasCNAME']:
            referer = request.META.get('HTTP_REFERER')
            if referer and "spotaxis.com" not in referer and request.get_host() not in referer:
                try:
                    request.session['referral_source'] = referer.split('//', 1)[1].split('/', 1)[0]
                except:
                    request.session['referral_source'] = referer

import time

from django.utils.http import cookie_date
from django.contrib.sessions.middleware import SessionMiddleware

# class SessionHostDomainMiddleware(SessionMiddleware):
#     def process_response(self, request, response):
#         """
#         If request.session was modified, or if the configuration is to save the
#         session every time, save the changes and set a session cookie.
#         """
#         print(dir(request))
#         print(dir(response))
#         if response.status_code == 302:
#             path = response.url
#             if 'spotaxis.com' in path and not path.startswith(request.get_host()):
#                 response.cookies = request.COOKIES

#         try:
#             accessed = request.session.accessed
#             modified = request.session.modified
#         except AttributeError:
#             pass
#         else:
#             if accessed:
#                 patch_vary_headers(response, ('Cookie',))
#             if modified or settings.SESSION_SAVE_EVERY_REQUEST:
#                 if request.session.get_expire_at_browser_close():
#                     max_age = None
#                     expires = None
#                 else:
#                     max_age = request.session.get_expiry_age()
#                     expires_time = time.time() + max_age
#                     expires = cookie_date(expires_time)
#                 # Save the session data and refresh the client cookie.
#                 # Skip session save for 500 responses, refs #3881.
#                 if response.status_code != 500:
#                     request.session.save()
#                     host = request.get_host().split(':')[0]
#                     response.set_cookie(settings.SESSION_COOKIE_NAME,
#                             request.session.session_key, max_age=max_age,
#                             expires=expires, domain=host,
#                             path=settings.SESSION_COOKIE_PATH,
#                             secure=settings.SESSION_COOKIE_SECURE or None,
#                             httponly=settings.SESSION_COOKIE_HTTPONLY or None)
#         return response

from django.contrib import messages
class ExpiredPlanMiddleware:
    def process_request(self,request):
        # if excess users, trigger mesage and redirect
        if request.user.is_authenticated() and request.user.profile.codename == 'recruiter':
            current_url = resolve(request.path_info).url_name
            # messages.success(request, request.path_info)
            if request.user.recruiter.company.all():
                total_recruiters = request.user.recruiter.company.all()[0].recruiter_set.all().filter(user__is_active=True).count()
                permitted_recruiters = request.user.recruiter.company.all()[0].subscription.price_slab.package.free_users + request.user.recruiter.company.all()[0].subscription.added_users
                if permitted_recruiters > 0 and total_recruiters > permitted_recruiters:
                    if current_url=="companies_company_team_space" or current_url=="companies_recruiter_profile" or current_url=="companies_company_profile" or current_url=="companies_billing" or current_url=='common_email_change' or current_url=='auth_password_change' or current_url =='common_password_change_done' or current_url=='common_email_change_requested'or current_url=='common_email_change_approve'or current_url=='companies_payment'or current_url=='companies_job_widget'or current_url=="auth_logout" or current_url == "notifications" or current_url == "payments_checkout" or request.path_info == '/ajax/removemember/' or request.path_info == '/ajax/updatepermissions/' or request.path_info == '/ajax/changeownership/' or request.path_info == '/ajax/set_plan/'or request.path_info == '/ajax/verify_code/'or request.path_info == '/ajax/update_recurring/'or request.path_info == '/ajax/renew_now/'or request.path_info == '/ajax/':
                        pass
                    else:
                        if request.user.recruiter.is_admin():
                            messages.error(request,'Your team strength exceeds the limit of your current plan. Remove members or upgrade plan to continue normal usage.')
                        else:
                            messages.error(request,'Your plan subscription has not been updated. Kindly contact your admin.')
                            # messages.success(request,current_url)
                        return HttpResponseRedirect(reverse('companies_company_team_space'))

# class CrossDomainSessionMiddleware(object):
#     def process_response(self, request, response):
#         if response.cookies:
#             host = request.get_host()
#             # check if it's a different domain
#             # if host not in settings.SESSION_COOKIE_DOMAIN:
#             domain = ".{domain}".format(domain=host)
#             for cookie in response.cookies:
#                 if 'domain' in response.cookies[cookie]:
#                     response.cookies[cookie]['domain'] = domain
#         return response
