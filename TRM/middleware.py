# -*- coding: utf-8 -*-
# from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from __future__ import absolute_import
from django.shortcuts import render
# from social.exceptions import AuthCanceled
from django.utils.cache import patch_vary_headers
from django.conf import settings

from TRM.settings import SUBDOMAIN_URLCONF, ROOT_DOMAIN, SITE_SUFFIX, SUPPORT_URLCONF, BLOG_URLCONF
from django.db.models import Q
from django.urls import set_urlconf, reverse, resolve
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
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Migrate process_request logic here
        fqdn = request.get_host().split(':')[0]
        domain_parts = fqdn.split('.')

        subdomain = None
        if len(domain_parts) >= 3 and domain_parts[-2] == 'spotaxis' and domain_parts[-3] == 'demo':
            if len(domain_parts) > 3:
                subdomain_slug = domain_parts[0]
            else:
                subdomain_slug = None
            try:
                subdomain = Subdomain.objects.get(
                    Q(cname=fqdn) |
                    Q(slug=subdomain_slug)
                )
            except Subdomain.DoesNotExist:
                subdomain = None
        else:
            if len(domain_parts) > 2 and ROOT_DOMAIN in fqdn:
                subdomain_slug = domain_parts[0]
            else:
                subdomain_slug = None
            try:
                subdomain = Subdomain.objects.get(
                    Q(cname=fqdn) |
                    Q(slug=subdomain_slug)
                )
            except Subdomain.DoesNotExist:
                subdomain = None

        if subdomain:
            set_urlconf(SUBDOMAIN_URLCONF)
            request.urlconf = SUBDOMAIN_URLCONF
        elif fqdn != SITE_SUFFIX.strip('.').strip('/'):
            raise Http404()

        response = self.get_response(request)

        # Migrate process_response logic here
        patch_vary_headers(response, ('Host',))
        return response


class MediumMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Equivalent of process_request
        subdomain_data = check_subdomain(request)
        if subdomain_data.get('active_subdomain') or subdomain_data.get('hasCNAME'):
            referer = request.META.get('HTTP_REFERER')
            if referer and "spotaxis.com" not in referer and request.get_host() not in referer:
                try:
                    request.session['referral_source'] = referer.split('//', 1)[1].split('/', 1)[0]
                except Exception:
                    request.session['referral_source'] = referer

        # Continue processing the request
        response = self.get_response(request)
        return response

import time
from http.cookies import _getdate as cookie_date
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
from django.urls import resolve, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

class ExpiredPlanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        if request.user.is_authenticated and getattr(request.user, 'profile', None) and request.user.profile.codename == 'recruiter':
            current_url = resolve(request.path_info).url_name

            company_qs = request.user.recruiter.company.all()
            if company_qs:
                company = company_qs[0]
                total_recruiters = company.recruiter_set.filter(user__is_active=True).count()
                permitted_recruiters = (
                    company.subscription.price_slab.package.free_users +
                    company.subscription.added_users
                )

                if permitted_recruiters > 0 and total_recruiters > permitted_recruiters:
                    safe_urls = {
                        "companies_company_team_space", "companies_recruiter_profile", "companies_company_profile",
                        "companies_billing", "common_email_change", "auth_password_change",
                        "common_password_change_done", "common_email_change_requested", "common_email_change_approve",
                        "companies_payment", "companies_job_widget", "auth_logout", "notifications", "payments_checkout"
                    }

                    safe_paths = {
                        "/ajax/removemember/", "/ajax/updatepermissions/", "/ajax/changeownership/",
                        "/ajax/set_plan/", "/ajax/verify_code/", "/ajax/update_recurring/",
                        "/ajax/renew_now/", "/ajax/"
                    }

                    if current_url not in safe_urls and request.path_info not in safe_paths:
                        if request.user.recruiter.is_admin():
                            messages.error(request, 'Your team strength exceeds the limit of your current plan. Remove members or upgrade plan to continue normal usage.')
                        else:
                            messages.error(request, 'Your plan subscription has not been updated. Kindly contact your admin.')

                        return HttpResponseRedirect(reverse('companies_company_team_space'))

        return None