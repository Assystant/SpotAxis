
from __future__ import absolute_import
from __future__ import print_function
import decimal
import json
import os
import random
import re
import traceback
from activities.utils import *
from activities.models import *
from candidates.models import Candidate, Academic, CV_Language, Curriculum, Academic_Area, Expertise, Training, Certificate, Project
from common import registration_settings
from common.forms import AdressForm, UserDataForm, BasicUserDataForm, UserPhotoForm, SubdomainForm
from common.models import Profile, Country, send_email_to_TRM, Gender, Subdomain, send_TRM_email
from companies.forms import CompanyForm, SearchCvForm, CompanyLogoForm, MemberInviteForm
from companies.models import Company_Industry, Recommendations, Recommendation_Status, Company, Wallet, Recruiter, Stage, RecruiterInvitation, ExternalReferal
from customField.forms import TemplateForm, FieldFormset
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext, Context, TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_exempt
from hashids import Hashids
from payments.models import *
from TRM.context_processors import subdomain
from TRM.settings import SITE_URL, num_pages, number_objects_page, DEFAULT_SITE_TEMPLATE, STATIC_URL
from vacancies.forms import VacancyForm, VacancyFileForm, Public_FilesForm
from vacancies.models import Vacancy, Vacancy_Status, Postulate, Vacancy_Files, VacancyStage
from vacancies.response import JSONResponse, response_mimetype
from vacancies.serialize import serialize
from vacancies.views import save_public_application
from utils import is_ajax

regex = re.compile('[^A-Za-z0-9]')
subdomain_hash = Hashids(salt='TRM Subdomain',min_length=4)
invite_hash = Hashids(salt='Invitation',min_length=7)


def record_recruiter(request, token=None):
    """
    Handle the registration of a recruiter user.

    If the user is already authenticated, raises Http404.
    Supports GET requests to set price slab in session.
    Handles POST requests to process recruiter registration form, 
    including invitation token processing, user creation, 
    email verification, and optional automatic login.
    """
    context = {}
    context['success'] = False
    if request.user.is_authenticated:
        raise Http404
    if request.GET:
        slabid = request.GET['price_slab']
        request.session['price_slab'] = slabid
        return redirect('companies_record_recruiter')

    if request.method == 'POST':
        invitation = None
        form_user = UserDataForm(data=request.POST,files=request.FILES)
        try:
            country_selected = Country.objects.get(iso2_code__exact='IN')
        except:
            country_selected = None
        if form_user.is_valid():
            # raise ValueError() 
            new_user = form_user.save()
            try:
                new_user.profile = Profile.objects.get(codename__exact='recruiter')
                new_user.logued_by = 'EL'
                new_user.save()
                r,created = Recruiter.objects.get_or_create(user=new_user, user__is_active=True)
                if token:
                    invitation = RecruiterInvitation.objects.get(token=token)
                    company = invitation.invited_by.recruiter.company.all()[0]
                    r.company.add(company)
                    r.membership = invitation.membership
                    r.save()
                    new_user.is_active = True
                    new_user.save()
                    post_notification(user=new_user,action="Welcome to SpotAxis!")
                    invitations = RecruiterInvitation.objects.filter(email = invitation.email).delete()
                    invitations = RecruiterInvitation.objects.filter(email = new_user.email).delete()
                else:
                    invitation = None
                    form_user.send_verification_mail(new_user)
                username = form_user.cleaned_data['username']
                password = form_user.cleaned_data['password']

            except Exception as err:
                print((traceback.format_exc()))
                new_user.delete()
                raise Http404

            if registration_settings.AUTO_LOGIN or token:
                # Automatically log this user in
                if registration_settings.EMAIL_ONLY:
                    username = form_user.cleaned_data['email']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
            if token:
                return redirect('common_redirect_after_login')
            request.session['new_email'] = new_user.email
            return redirect(registration_settings.REGISTRATION_REDIRECT)
            if is_ajax(request):
                context['success']=True
                context['msg'] = 'Profile Updated'
                return JSONResponse(context)
            else:
                return redirect(registration_settings.REGISTRATION_REDIRECT)
        else:
            invitation = RecruiterInvitation.objects.filter(token=token)
            if invitation:
                invitation = invitation[0]
            else:
                invitation = None
            #if request.is_ajax():
            if is_ajax(request):
                context['errors'] = form_user.errors;
                return JSONResponse(context)
    else:
        form_user = UserDataForm()
        invitation = RecruiterInvitation.objects.filter(token=token)
        if invitation:
            invitation = invitation[0]
        else:
            invitation = None
    template = 'new_record_edit_recruiter.html'
    subdomain_data = subdomain(request)
    static_header = True
    if subdomain_data['active_host']:
        template = 'record_edit_recruiter.html'
        static_header = False
    return render(request, template,
                              {'form_user': form_user,
                               'registration': True,
                               'invitation': invitation,
                               'token': token,
                               'static_header': static_header})
                              #context_instance=RequestContext(request))

@login_required
def record_company(request):
    """
    Allow a logged-in recruiter to create and register a new company profile.

    Checks if the recruiter already has a company associated; redirects if yes.
    Handles POST requests to validate and save company form data, 
    creates related objects such as Subdomain, Wallet, Subscription, and Stages,
    assigns company to recruiter with membership updates, and redirects to the company's page.

    """
    try:
        recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
    except:
        recruiter=""
        raise Http404
    if recruiter.company.all():
        return redirect('companies_company_profile')
    if request.method == 'POST':
        # form_user = UserDataForm(data=request.POST, files=request.FILES, )
        try:
            country_selected = Country.objects.get(id=request.POST['country'])
            # country_selected = Country.objects.get(iso2_code__exact='MX')
        except:
            country_selected = None
        # try:
        #     if int(request.POST['state']) == 0:
        #         state_selected = 0
        #     else:
        #         state_selected = State.objects.get(id=request.POST['state'])
        # except:
        #     state_selected = None
        # form_address = AdressForm(data=request.POST,
        #                           files=request.FILES,
        #                           country_selected=country_selected,
        #                           state_selected=state_selected)
        # try:
        #     area_selected = Company_Area.objects.get(pk=int(request.POST['area']))
        # except:
        #     area_selected = None
        try:
            if int(request.POST['industry']) == 0:
                industry_selected = 0
            else:
                industry_selected = Company_Industry.objects.get(id=request.POST['industry'])
        except:
            industry_selected = None
        form_company = CompanyForm(data=request.POST,
                                   files=request.FILES,
                                   # area_selected=area_selected,
                                   country_selected=country_selected,
                                   industry_selected=industry_selected)
        if form_company.is_valid():

            new_company = form_company.save()
            try:
                new_company.user = request.user
                # to_company = form_company.cleaned_data['to_company']
                # if to_company:
                #     Recommendations.objects.create(to_company=to_company,
                #                                    from_company=new_company,
                #                                    status=Recommendation_Status.objects.get(codename__iexact='preregistration'))
                #     new_company.user_recommendation = to_company
                brand_name = slugify(new_company.name).replace('-','')
                brand_name = regex.sub('',brand_name)
                slug = brand_name + subdomain_hash.encode(new_company.id)
                subdomain = Subdomain.objects.create(slug=slug)
                new_company.subdomain = subdomain
                template_id = DEFAULT_SITE_TEMPLATE
                new_company.site_template = template_id
                above_job = render_to_string('careers/base/t-'+ str(template_id) +'/above_jobs.html',{'STATIC_URL':STATIC_URL})
                new_company.above_jobs = above_job
                below_job = render_to_string('careers/base/t-'+ str(template_id) +'/below_jobs.html',{'STATIC_URL':STATIC_URL})
                new_company.below_jobs = below_job
                new_company.save()
                discounts = Discount.objects.filter(available_to_signups = True)
                for discount in discounts:
                    du, created = Discount_Usage.objects.get_or_create(discount = discount, company = new_company)
                    du.save()
                    # discount.companies.add(new_company)
                    # discount.save()
                recruiter.company.add(new_company)
                recruiter.membership = 3
                recruiter.save()
                Wallet.objects.create(company = new_company, available=0)
                Subscription.objects.create(company=new_company, price_slab = PriceSlab.objects.get(id=2))
                Stage.objects.create(name="New Candidates",company=new_company)
                Stage.objects.create(name="Onboarding",company=new_company)
                # new_user.profile = Profile.objects.get(codename__exact='recruiter')
                # new_user.logued_by = 'EL'
                # new_user.save()
                request.session['first_time'] = True
                return redirect(new_company.geturl())
                # form_user.send_verification_mail(new_user)
                # username = form_user.cleaned_data['username']
                # password = form_user.cleaned_data['password']
            except Exception as err:
                print((traceback.format_exc()))
                new_company.delete()
                raise Http404
                # messages.error(request,'Could not Save: ' + str(err))

            
    else:
        # form_user = UserDataForm()
        # form_address = AdressForm()
        form_company = CompanyForm()

    return render(request,'record_edit_company.html',{
                              # {'form_user': form_user,
                              # 'form_address': form_address,
                               'form_company': form_company,
                               'registration': True})
                              

@login_required
def edit_company(request):
    """
    Allow a logged-in user to edit their company profile, user data, and address.

    Redirects users without an email to a blank email registration page.
    Handles GET requests to render forms prefilled with existing data.
    Handles POST requests to validate and save updated user, address, and company information,
    including updating the company subdomain slug and notifying relevant recruiters.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    user = request.user
    company = get_object_or_404(Company, user=user)
    address = company.address
    if request.method == 'POST':
        form_user = BasicUserDataForm(request.POST, request.FILES, instance=user)
        try:
            # country_selected = Country.objects.get(id= request.POST['country'])
            country_selected = Country.objects.get(iso2_code__exact='MX')
        except:
            country_selected = None
        try:
            if int(request.POST['state']) == 0:
                state_selected = 0
            else:
                state_selected = State.objects.get(id=request.POST['state'])
        except:
            state_selected = None
        form_address = AdressForm(request.POST, request.FILES, instance=address,
                                  country_selected=country_selected,
                                  state_selected=state_selected, )
        try:
            industry_selected = Company_Industry.objects.get(pk=int(request.POST['industry']))
        except:
            industry_selected = None
        try:
            if int(request.POST['area']) == 0:
                area_selected = 0
            else:
                area_selected = Company_Area.objects.get(id=request.POST['area'])
        except:
            area_selected = None
        form_company = CompanyForm(request.POST, request.FILES, instance=company,
                                   area_selected=area_selected,
                                   industry_selected=industry_selected, )
        if form_user.is_valid() and form_company.is_valid() and form_address.is_valid():
            user = form_user.save()
            address = form_address.save()
            address.country = country_selected
            address.save()
            company = form_company.save()
            company.address = address
            company.save()
            brand_name = slugify(company.social_name).replace('-','')
            brand_name = regex.sub('',brand_name)
            slug = brand_name + subdomain_hash.encode(company.id)
            sub_domain = company.subdomain
            sub_domain.slug = slug
            message_chunks = [
                    {
                        'subject': "Company Profile",
                        'subject_action': '',
                        'action_url': company.get_absolute_url(),
                    }
                ]
            post_org_notification(message_chunks = message_chunks, user=[r.user for r in Recruiter.admins.all()], actor=request.user,  action ="updated", subject = "Company Profile", url=company.get_absolute_url())
            sub_doman.save()
            messages.success(request, _('We have modified the information successfully'))
            subscribers = [r.user for r in user.recruiter.fellow_recruiters.all()]
            return redirect('companies_company_profile')
    else:
        form_user = BasicUserDataForm(instance=request.user)
        form_company = CompanyForm(instance=company, area_selected=company.area,
                                   industry_selected=company.industry, change_profile=True,
                                   initial={'phone': company.phone})
        form_address = AdressForm(instance=address, country_selected=address.country,
                                  state_selected=address.state, change_profile=True)
    pageheader = _('Modify my Profile')
    return render(request, 'record_edit_company.html', {'form_user': form_user,
                                                        'form_company': form_company,
                                                        'form_address': form_address,
                                                        'user': user,})

@login_required
def recruiter_profile(request):
    """
    Display and update the logged-in recruiter's profile, including user data and profile photo.

    Redirects users without an email to a blank email registration page.
    Handles GET requests to render profile forms.
    Handles POST requests to update user data or profile photo,
    supporting AJAX responses for profile data updates.
    """
    context={}
    context['success'] = False
    if request.user.is_authenticated and not request.user.email:
        # If the user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    try:
        recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
    except:
        recruiter=""
        return Http404
    if request.method == 'POST':
        form_user = BasicUserDataForm(data=request.POST,files=request.FILES, instance=request.user)
        form_user_photo = UserPhotoForm(data=request.POST,files=request.FILES, instance=request.user)
        if is_ajax(request):
            if form_user.is_valid():
                form_user.save()
                context['success'] = True
                context['msg'] = 'Profile Updated'
                context['img'] = request.user.photo.url
            else:
                context['errors'] = form_user.errors
        else:
            if form_user_photo.is_valid():
                form_user_photo.save()
                messages.success(request, "Profile Image Updated.")
            else:
                messages.error(request, "Image not updated")

        if is_ajax(request):
            return JSONResponse(context)
    else:
        form_user = BasicUserDataForm(instance=request.user)
        form_user_photo = UserPhotoForm(instance=request.user)
    # company = get_object_or_404(Company, user=request.user)
    created = False
    return render(request, 'recruiter_profile.html',
                              {'isProfile': True,
                               'user': request.user,
                               'form_user': form_user,
                               'form_user_photo': form_user_photo,
                               'recruiter': recruiter,
                               'companies': recruiter.company.all(),
                               # 'company': company,
                               # 'company_wallet': company_wallet,
                               'created': created
                              })
                            

@login_required
def company_profile(request):
    """
    Display and update the company profile for the company associated with the current subdomain.

    Redirects users without an email to a blank email registration page.
    Raises 404 if the active host subdomain is not found.
    Allows authorized recruiters (admins) to update company details or logo.
    Handles both standard and AJAX requests, returning JSON responses for AJAX updates.
    Loads and passes company vacancies and their stages to the template.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    context={}
    context['success'] = False
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        raise Http404
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    # company = Company.objects.get(subdomain__slug='trm7')
    created = False
    statuses = Vacancy_Status.objects.all()
    if request.user.is_authenticated:
        try:
            recruiter = Recruiter.objects.get(user=request.user, company=company, user__is_active=True)
        except:
            recruiter = None
    form_company = CompanyForm(instance=company)
    logo_form = CompanyLogoForm(instance=company)
    if request.method=='POST' and recruiter and recruiter.is_admin():
        if request.POST.get('isimage','0') == '1':
            logo_form = CompanyLogoForm(data = request.POST,files = request.FILES, instance = company)
            if logo_form.is_valid():
                logo_form.save()
                messages.success(request,"Logo Updated.")
            else:
                context['errors'] = logo_form.errors
        else:
            form_company = CompanyForm(data = request.POST, files = request.FILES, instance = company)
            if form_company.is_valid():
                form_company.save()
                # company = Company.objects.get(user=request.user)
                company = recruiter.company.all()[0]
                # company.refresh_from_db()
                brand_name = slugify(company.name).replace('-','')
                brand_name = regex.sub('',brand_name)
                slug = brand_name + subdomain_hash.encode(company.id)
                sub_domain = company.subdomain
                if sub_domain and not sub_domain.slug == slug:
                    sub_domain.slug = slug
                    sub_domain.save()
                    if not sub_domain.cname:
                        company.refresh_from_db()
                        context['redirect'] = company.get_absolute_url()
                        return redirect(company.get_absolute_url())
                context['success'] = True
                context['msg'] = 'Profile Updated'
                context['img'] = company.logo.url
                
            else:
                context['errors'] = form_company.errors
            if is_ajax(request):
                return JSONResponse(context)
    vacancies = Vacancy.objects.filter(company = company)
    for vacancy in vacancies:
        vacancy.stages = VacancyStage.objects.filter(vacancy=vacancy)
    return render(request,'company_profile.html',
                              {'recruiter': recruiter,
                               'isCompanyProfile': True,
                               'isProfile': True,
                               'user': request.user,
                               'company': company,
                               'form_company': form_company,
                               'logo_form': logo_form,
                               'vacancy_status': statuses,
                               'company_wallet': company_wallet,
                               'created': created,
                               'vacancies': vacancies
                              })
                              

@login_required
def site_management(request, setting=None):
    """ Handles site management pages for a recruiter's company including template, subdomain, and embed settings."""
    if request.user.is_authenticated and not request.user.email:
        # If the user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    context={}
    context['success'] = False
    if not setting:
        setting = 'template'
    # if not setting:
    #     setting = 'subdomain'
    try:
        recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
    except:
        raise Http404
    if not recruiter.is_admin():
        raise Http404
    context['user'] = request.user
    context['recruiter'] = recruiter
    company = recruiter.company.all()
    if company:
        company = company[0]
    else:
        raise Http404
    context['company'] = company
    context['sub_domain'] = company.subdomain
    if setting == 'template':
        context['isTemplatePage'] = True
    elif setting == 'subdomain' and company.check_service('CSM_CNAME'):
        context['isSubdomainPage'] = True
        if request.method == 'POST':
            form_subdomain = SubdomainForm(instance=context['sub_domain'], data=request.POST, files = request.FILES)
            if form_subdomain.is_valid():
                form_subdomain.save()
                messages.success(request, 'The subdomain has been successfully updated')
        else:
            form_subdomain = SubdomainForm(instance=context['sub_domain'])
        context['form_subdomain'] = form_subdomain
    elif setting == 'embed' and company.check_service('CSM_JOBS_WIDGET') or not setting and company.check_service('CSM_JOBS_WIDGET'):
        context['isEmbedPage'] = True
        context['Embedurl'] = company.geturl() + reverse('companies_job_widget')
    # elif setting == 'joblinks' or not setting:
    #     context['isJobLinkPage'] = True
    #     context['vacancies'] = Vacancy.publishedjobs.filter(company = company)
    # elif setting == 'applyform' and company.check_service('CSM_ONSITE_APPLY'):
    #     context['isApplyFormPage'] = True
    #     context['vacancies'] = Vacancy.publishedjobs.filter(company = company)
    else:
        raise Http404
    context['isCompanyManagement'] = True
    return render(request,'site_management.html',context)
    
@login_required
def team_space(request):
    """Displays the team space page where the recruiter can invite new team members and view existing members."""
    if request.user.is_authenticated and not request.user.email:
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    context={}
    recruiter = get_object_or_404(Recruiter, user=request.user)
    company = recruiter.company.all()
    if company:
        company = company[0]
    else:
        return redirect('companies_record_company')
    if request.method == 'POST' and company.check_service('CH_ADD_TEAM'):
        context['form_invite'] = MemberInviteForm(data = request.POST)
        if context['form_invite'].is_valid():
            invitation = context['form_invite'].save()
            invitation.token = invite_hash.encode(invitation.id)
            invitation.invited_by = request.user
            invitation.membership = int(request.POST.get('membershipoptions',1))
            invitation.save()
            invitations = RecruiterInvitation.objects.filter(invited_by__recruiter__company__in = recruiter.company.all(), email = invitation.email).exclude(id=invitation.id).delete()
            subject_template_name = 'mails/recruiter_invitation_subject.html'
            email_template_name = 'mails/recruiter_invitation.html'
            url = company.geturl() + reverse('companies_recruiter_invitation', args=[invitation.token])
            context_email = {
                'invitation': invitation,
                'company': company,
                'href_url': url
            }
            sent = send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=invitation.email)
            messages.success(request,str(sent)+' Invitation Sent')
    else:
        context['form_invite'] = MemberInviteForm()
    context['members'] = Recruiter.objects.filter(company=company, user__is_active=True)
    context['company'] = company
    context['isTeamSpace'] = True
    context['isTeam'] = True
    return render(request,'company_profile.html',context)
    
@login_required
def finalize_vacancy(request, vacancy_id, message=None):
    """ Finalizes (closes) a vacancy with a reason for closing."""
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company=request.user.recruiter.company.all()[0])
    vacancy.status = Vacancy_Status.objects.get(codename__exact='closed')  # Finalised
    vacancy.end_date = date.today()
    # raise ValueError()
    if message == '1':
        vacancy.vacancy_reason = "Candidates Selection Complete"
    elif message == '2':
        vacancy.vacancy_reason = "No Suitable Candidate Found"
    elif message == '3':
        vacancy.vacancy_reason = "Job Opening is on hold"
    else:
        # raise ValueError(message == '1')
        raise Http404
    vacancy.save()
    if not vacancy.expired:
        vacancy.unpublish()
    # vacancy = vacancy_stage.vacancy
    subscribers = list(set([r.user for r in vacancy.company.recruiter_set.all().exclude(user = request.user)]))
    # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
    message_chunks = [
            {
                'subject': str(vacancy.employment),
                'subject_action': '',
                'action_url': vacancy.get_absolute_url(),
            }
        ]
    post_activity(message_chunks = message_chunks, actor = request.user,action = 'closed job opening - ', subject = str(vacancy.employment), subscribers = subscribers, action_url = vacancy.get_absolute_url())
    messages.success(request, _('Job Opening for "%s" has been closed') % vacancy.employment)
    return redirect('TRM-Subindex')

@login_required
def remove_vacancy(request, vacancy_id):
    """Removes (closes) a vacancy, marking its status as closed and setting the end date."""
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company=request.user.company.pk)
    vacancy.status = Vacancy_Status.objects.get(codename__exact='closed')  # Removed
    vacancy.end_date = date.today()
    vacancy.save()
    if not vacancy.expired:
        vacancy.unpublish()
    messages.success(request, _('Job Opening for "%s" has been closed') % vacancy.employment)
    return redirect('companies_vacancies_by_status',vacancy_status_name='closed')

@login_required
def publish_vacancy(request, vacancy_id):
    """Publishes a vacancy, optionally setting a publish period if specified."""
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company=request.user.company.pk)
    # 5 more days are assigned to edit the vacancy
    publish_period = None
    if vacancy.company.check_service('JM_DURATION') and request.method == 'POST':
        publish_period = request.POST.get('publish_period', None)
    if publish_period:
        start,end = publish_period.split('-')
        start = start.strip()
        end = end.strip()
        start = datetime.strptime(start, "%m/%d/%Y").date()
        end = datetime.strptime(end, "%m/%d/%Y").date()
        if start < date.today():
            messages.error(request,'Bad Range')
        elif start == date.today():
            vacancy.publish()
            if not vacancy.hasbeenPublished:
                vacancy.editing_date = date.today() + timedelta(days=5)
            vacancy.pub_after = False
        else:
            vacancy.pub_after = True
            vacancy.pub_date = start
        if end and end > start:
            vacancy.unpub_date = end
    else:
        vacancy.publish()
        if not vacancy.hasbeenPublished:
            vacancy.editing_date = date.today() + timedelta(days=5)
        vacancy.pub_after = False
    vacancy.save()
    messages.success(request, _('Successfully Published Job'))
    return redirect('companies_vacancies_by_status',vacancy_status_name='open')

@login_required
def unpublish_vacancy(request, vacancy_id):
    """Unpublishes a vacancy by setting its status to unpublished and disabling the scheduled publish."""
    try:
        company = request.user.recruiter.company.all()[0]
    except:
        raise Http404
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company=company.pk)
    # 5 more days are assigned to edit the vacancy
    vacancy.unpublish()
    vacancy.pub_after = False
    vacancy.save()
    messages.success(request, _('Successfully UnPublished Job'))
    return redirect('companies_vacancies_by_status',vacancy_status_name='open')

@login_required
def applications_for_vacancy(request, vacancy_id):
    """ Displays a list of candidates who have applied for a specific vacancy.
    Handles discarding candidates via POST requests."""
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, user=request.user)
    applications = Postulate.objects.filter(vacancy=vacancy, discard=False)

    if request.method == 'POST':
        candidates_ids = request.POST.getlist('candidates_ids[]')
        for candidate_id in candidates_ids:
            candidate = get_object_or_404(Candidate, pk=int(candidate_id))
            postulate = get_object_or_404(Postulate, vacancy=vacancy, candidate=candidate)
            postulate.discard = True
            postulate.save()
            vacancy.applications -= 1
            vacancy.save()

    # The pooled CV information of a candidates obtained is stored in the 'curriculum' list
    curricula = []
    if applications:
        for application in applications:
            candidate = application.candidate
            expertises = Expertise.objects.filter(candidate=candidate)
            academics = Academic.objects.filter(candidate=candidate)
            curriculum = Postulate.objects.get(candidate=candidate, vacancy=vacancy)
            curricula.append([candidate, expertises, academics, curriculum])
    else:
        return redirect('companies_vacancies_summary')

    today = datetime.now().date()
    return render(request,'vacancies/vacancy_applications.html',
                              {'isVacancy': True, 'curricula': curricula, 'vacancy': vacancy, 'today': today})
    """return render_to_response('vacancies/vacancy_applications.html',
                              {'isVacancy': True, 'curricula': curricula, 'vacancy': vacancy, 'today': today},
                              context_instance=RequestContext(request))"""

@login_required
def discard_candidate(request, vacancy_id, candidate_id):
    """ Marks a candidate's application for a vacancy as discarded. """
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id, user=request.user)
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    postulate = get_object_or_404(Postulate, vacancy=vacancy, candidate=candidate)
    postulate.discard = True
    postulate.save()
    vacancy.applications -= 1
    vacancy.save()
    return redirect(reverse('companies_applications_for_vacancy', args=[vacancy.pk]))

@login_required
def curriculum_detail(request, candidate_id=None, vacancy_id=None):
    """Displays detailed curriculum vitae information for a candidate, optionally within the context of a specific vacancy.
    Marks the candidate's application as seen and sends notification email if accessed for the first time."""
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    expertises = Expertise.objects.filter(candidate=candidate)
    academics = Academic.objects.filter(candidate=candidate)
    # softwares = CV_Software.objects.filter(candidate=candidate)
    languages = CV_Language.objects.filter(candidate=candidate)
    trainings = Training.objects.filter(candidate=candidate)
    projects = Project.objects.filter(candidate=candidate)
    certificates = Certificate.objects.filter(candidate=candidate)
    curriculum = get_object_or_404(Curriculum, candidate=candidate)
    vacancy = None
    try:
        recruiter = Recruiter.objects.get(user = request.user)
    except:
        raise Http404
    if vacancy_id:
        # If there is vacancy id, it means that it is reviewing a nomination for a vacancy
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company__in=recruiter.company.all())
        postulate = get_object_or_404(Postulate, candidate=candidate, vacancy=vacancy)
        if not postulate.seen:
            # It is marked as seen the curriculum / application and are notified by mail candidate
            postulate.seen = True
            postulate.save()
            context_email = {
                'vacancy': vacancy,
                'candidate': candidate,
                'seen_candidate': True,
                'vacancy_url': vacancy.company.geturl() + reverse('vacancies_get_vacancy_details', args={str(vacancy_id)})
            }
            subject_template_name = 'mails/seen_candidate_subject.html',
            email_template_name = 'mails/seen_candidate_email.html',
            contact_email = ""
            if candidate.user:
                contact_email = candidate.user.email
            else:
                contact_email = candidate.public_email
            send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=contact_email)
    else:
        raise Http404
    today = datetime.now().date()
    vacancies = Postulate.objects.filter(vacancy__company = vacancy.company, candidate = candidate)
    for postulates in vacancies:
        postulates.ratings = postulates.comment_set.all().filter(comment_type=2).count()
        postulates.processes = postulates.postulate_stage_set.all().exclude(vacancy_stage__order=100)
        postulates.timeline = postulates.comment_set.all().filter(comment_type__gte=2)
        postulates.comments = postulates.comment_set.all().filter(comment_type__lt=2)
    isProcessManager=False
    if postulate.vacancy_stage and request.user.recruiter in postulate.vacancy_stage.recruiters.all():
        isProcessManager = True
    return render(request,'view_curriculum.html',
                              {'isVacancy': True,
                               'today': today,
                               'isProcessManager': isProcessManager,
                               'candidate': candidate,
                               'postulate': postulate,
                               'vacancy': vacancy,
                               'company': True,
                               'vacancies': vacancies,
                               'curriculum': curriculum,
                               'academics': academics,
                               'expertises': expertises,
                               'languages': languages,
                               'trainings': trainings,
                               'certificates': certificates,
                               'projects': projects })
                            

# @login_required
# def public_curriculum_detail(request, candidate_id=None, vacancy_id=None):
    #     # candidate = get_object_or_404(Candidate, pk=candidate_id)

    #     # expertises = Expertise.objects.filter(candidate=candidate)
    #     # academics = Academic.objects.filter(candidate=candidate)
    #     # # softwares = CV_Software.objects.filter(candidate=candidate)
    #     # languages = CV_Language.objects.filter(candidate=candidate)
    #     # trainings = Training.objects.filter(candidate=candidate)
    #     # projects = Project.objects.filter(candidate=candidate)
    #     # certificates = Certificate.objects.filter(candidate=candidate)
    #     # curriculum = get_object_or_404(Curriculum, candidate=candidate)
    #     vacancy = None
    #     try:
    #         recruiter = Recruiter.objects.get(user = request.user)
    #     except:
    #         raise Http404
    #     if vacancy_id:
    #         # If there is vacancy id, it means that it is reviewing a nomination for a vacancy
    #         vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company__in=recruiter.company.all())
    #         postulate = get_object_or_404(Public_Postulate, id=candidate_id, vacancy=vacancy)
    #         # if not postulate.seen:
    #         #     # It is marked as seen the curriculum / application and are notified by mail candidate
    #         #     postulate.seen = True
    #         #     postulate.save()
    #         #     context_email = {
    #         #         'vacancy': vacancy,
    #         #         'candidate': candidate,
    #         #         'seen_candidate': True,
    #         #         'vacancy_url': vacancy.company.geturl() + reverse('vacancies_get_vacancy_details', args={str(vacancy_id)})
    #         #     }
    #         #     subject_template_name = 'mails/seen_candidate_subject.html',
    #         #     email_template_name = 'mails/seen_candidate_email.html',
    #         #     send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=candidate.user.email)
    #     else:
    #         raise Http404
    #     today = datetime.now().date()
    #     vacancies = Public_Postulate.objects.filter(vacancy__company = vacancy.company, email = postulate.email)
    #     for postulate in vacancies:
    #         postulate.ratings = postulate.comment_set.all().filter(comment_type=2).count()
    #         postulate.processes = postulate.public_postulate_stage_set.all().exclude(vacancy_stage__order=100)
    #         postulate.timeline = postulate.comment_set.all().filter(comment_type__gte=2)
    #     isProcessManager=False
    #     if postulate.vacancy_stage and request.user.recruiter in postulate.vacancy_stage.recruiters.all():
    #         isProcessManager = True
    #     return render_to_response('view_curriculum.html',
    #                               {'isVacancy': True,
    #                                'today': today,
    #                                'isProcessManager': isProcessManager,
    #                                'candidate': postulate,
    #                                'postulate': postulate,
    #                                'vacancy': vacancy,
    #                                'company': True,
    #                                'public': True,
    #                                'vacancies': vacancies,},
    #                               context_instance=RequestContext(request))

# @login_required
def vacancies_summary(request, vacancy_status_name=None): 
    """Display a summary of a company's vacancies based on vacancy status and user role.

    Handles vacancy listing for recruiters and general users, manages file cleanup
    for incomplete vacancy creation, processes invitation form submission, and
    renders appropriate templates."""
    """ Show the summary of a Company's vacancies """
    # raise ValueError()
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    subdomain_data = subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
        # company = get_object_or_404(Company, user=request.user)
    if request.user.is_authenticated and getattr(getattr(request.user, 'profile', None), 'codename', None)== 'recruiter':
    #if request.user.is_authenticated and request.user.profile.codename == 'recruiter
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        except:
            return redirect('companies_record_company')
    else:
        recruiter=None
    try:
        company = Company.objects.get(subdomain__slug=subdomain_data['active_subdomain'])
    except:
        raise Http404
    if vacancy_status_name and not recruiter:
        raise Http404

    try:
        # If he has not finished creating a vacancy and
        # user has pre-loaded files, remove
        # to clear disk space
        random_number = request.session.get('random_number')
        if random_number:
            print(('random_number.- %s' % random_number))
            uploaded_files = Vacancy_Files.objects.filter(random_number=random_number)
            for uploaded_file in uploaded_files:
                uploaded_file.delete()
            try:
                remove_dir = os.path.join(settings.MEDIA_ROOT, Vacancy_Files.default_path, Vacancy_Files.tmp_folder, str(random_number))
                os.rmdir(remove_dir)
            except:
                tb = traceback.format_exc()
                print(tb)
                pass
            request.session['random_number'] = None
    except:
        tb = traceback.format_exc()
        print(tb)
        pass
    if recruiter and company in recruiter.company.all():
        my_vacancy = True
    else:
        my_vacancy = False
    # Different vacancy status
    if vacancy_status_name:
        vacancy_status = Vacancy_Status.objects.filter(codename=vacancy_status_name)
        if not vacancy_status:
            raise Http404
        else:
            vacancy_status = vacancy_status[0]
    else:
        vacancy_status = Vacancy_Status.objects.get(codename='open')
    # vacancies_status = Vacancy_Status.objects.all()
    # active_status = vacancies_status.get(codename='active')
    # inactive_status = vacancies_status.get(codename='inactive')
    # programmed_status = vacancies_status.get(codename='programmed')
    # finalized_status = vacancies_status.get(codename='finalized')

    # # Vacancies depending on their status
    # vacancies = Vacancy.objects.filter(user=request.user).values('pk', 'employment', 'seen', 'applications', 'pub_date', 'end_date')
    # active_vacancies = vacancies.filter(status=active_status)
    # inactive_vacancies = vacancies.filter(status=inactive_status)
    # programmed_vacancies = vacancies.filter(status=programmed_status)
    # finalized_vacancies = vacancies.filter(status=finalized_status)
    # try:
    #     company_wallet = get_object_or_404(Wallet, company=company)
    # except:
    #     company_wallet = None
    statuses = Vacancy_Status.objects.all()
    if recruiter:
        if vacancy_status_name == 'open':
            vacancies = Vacancy.openjobs.filter(company = company)
        elif vacancy_status_name == 'closed':
            vacancies = Vacancy.closedjobs.filter(company = company)
        else:
            vacancies = Vacancy.objects.none()

    else:
        vacancies = Vacancy.publishedjobs.filter(company = company)
    for vacancy in vacancies:
        vacancy.stages = VacancyStage.objects.filter(vacancy=vacancy)
    if recruiter:
        if request.method == 'POST' and vacancy_status_name:
            try:
                vacancy_id = request.POST.get('vacancy')
                vacancy = Vacancy.objects.get(id=vacancy_id)
            except:
                messages.error(request, 'A matching Job was not found. Please check and try again')
            if vacancy:
                public_form = save_public_application(request, vacancy, recruiter)
            else:
                public_form = Public_FilesForm()
            if is_ajax(request):
                return JsonResponse(context)
        else:
            public_form = Public_FilesForm()
        if request.method == 'POST' and not vacancy_status_name and company.check_service('CH_ADD_TEAM'):
            form_invite = MemberInviteForm(data = request.POST)
            if form_invite.is_valid():
                invitation = form_invite.save()
                invitation.token = invite_hash.encode(invitation.id)
                invitation.invited_by = request.user
                invitation.membership = int(request.POST.get('membershipoptions',1))
                invitation.save()
                invitations = RecruiterInvitation.objects.filter(invited_by__recruiter__company__in = recruiter.company.all(), email = invitation.email).exclude(id=invitation.id).delete()
                subject_template_name = 'mails/recruiter_invitation_subject.html'
                email_template_name = 'mails/recruiter_invitation.html'
                url = company.geturl() + reverse('companies_recruiter_invitation', args=[invitation.token])
                context_email = {
                    'invitation': invitation,
                    'company': company,
                    'href_url': url
                }
                sent = send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=invitation.email)
                messages.success(request, str(sent)+' Invitation Sent')
        else:
            form_invite = MemberInviteForm()
    else:
        public_form = Public_FilesForm()
    if not recruiter or not my_vacancy:
        template = 'careers/base/root.html'
        jobs_template = 'careers/base/t-' + str(company.site_template) + '/jobs.html'
        stylesheet = 'sa-ui-kit/t-' + str(company.site_template) + '/style.css'
        return render(request,template ,
                            {'isVacancy': True,
                               # 'active_vacancies': active_vacancies,
                               # 'inactive_vacancies': inactive_vacancies,
                               # 'programmed_vacancies': programmed_vacancies,
                               # 'finalized_vacancies': finalized_vacancies,
                               # 'company_wallet': company_wallet,
                               'vacancy_status': vacancy_status,
                               'statuses': statuses,
                               'vacancies': vacancies,
                               'company': company,
                               'my_vacancy': my_vacancy,
                               'public_form': public_form,
                               'jobs_template':jobs_template, 
                               'stylesheet':stylesheet,
                            })
    elif vacancy_status_name:
        return render(request,'vacancies/vacancies_summary.html' ,
                            {'isVacancy': True,
                               # 'active_vacancies': active_vacancies,
                               # 'inactive_vacancies': inactive_vacancies,
                               # 'programmed_vacancies': programmed_vacancies,
                               # 'finalized_vacancies': finalized_vacancies,
                               # 'company_wallet': company_wallet,
                               'vacancy_status': vacancy_status,
                               'statuses': statuses,
                               'vacancies': vacancies,
                               'company': company,
                               'my_vacancy': my_vacancy,
                               'public_form': public_form,
                            }) 
    else:
        packages = Package.objects.all()
        service_categories = ServiceCategory.objects.all()
        if 'first_time' in list(request.session.keys()) and request.session['first_time']:
            first_time = True
            request.session['first_time'] = False
        else:
            first_time = False
        activity_stream = Activity.objects.all().filter(Q(actor = request.user) | Q(subscribers__in=[request.user])).distinct()
        return render(request,'activities.html',{
                                'company': company,
                                'recruiter': recruiter,
                                'form_invite': form_invite,
                                'activity_stream': activity_stream,
                                'packages': packages,
                                'first_time': first_time,
                                'service_categories': service_categories,
                            })
def upload_vacancy_file(request):
    """
    Handle AJAX file upload for vacancy files, validate and save the file(s).

    Processes files sent via POST request, validates the number of uploaded files,
    saves them associated with a vacancy or temporary session, and returns serialized
    file data or errors as JSON response.
    """
    # FUNCION AJAX
    # Function to upload a file sent by AJAX, validate the form,
    # if the form has errors, returns to fail method section $('#id_file').fileupload
    # and displays an error alert form validation. Returns the serialized file (array)
    if request.method == 'POST':
        try:
            fileForm = VacancyFileForm(data=request.POST, files=request.FILES)

            if request.FILES and request.FILES.getlist('file'):
                # If there uploaded files, get the number to validate that do not climb more than maximum allowed
                uploaded_files = len(request.FILES.getlist('file'))
                fileForm.validate_number_files(uploaded_files)
            if fileForm.is_valid():
                if request.FILES:
                    vacancy_id = request.POST.get('vacancy_id')
                    vacancy = None
                    if vacancy_id and int(vacancy_id) > 0:
                        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
                    # Save the file, using the method of the known form, which have overwritten
                    object = fileForm.save(vacancy=vacancy, random_number=request.session.get('random_number'))
                    if vacancy:
                        # If there is a vacancy
                        objFiles = Vacancy_Files.objects.filter(vacancy=vacancy).count()
                    else:
                        # If the vacancy is just being created, we obtain the number of files that have that random number.
                        objFiles = Vacancy_Files.objects.filter(random_number=request.session.get('random_number')).count()

                    # serialize the object (convert to array)
                    files = [serialize(object)]

                    # These variables back to the template (files and obj Files)
                    data = {'files': files, 'objFiles': objFiles}
                    response = JSONResponse(data, mimetype=response_mimetype(request))
                    response['Content-Disposition'] = 'inline; filename=files.json'
                    return response
            else:
                # We pass form data errors
                data = json.dumps(dict([(k, [str(e) for e in v]) for k,v in list(fileForm.errors.items())]))
                return HttpResponse(content=data, status=400, content_type='application/json')
        except:
            tb = traceback.format_exc()
            print(tb)
            data = json.dumps("Error al crear archivo")
            return HttpResponse(content=data, status=400, content_type='application/json')

@login_required
def delete_vacancy_file(request):
    """
    Handle AJAX request to delete a vacancy file by its ID.

    Deletes the specified Vacancy_Files object identified by POST parameter 'id'
    and returns a JSON response indicating success or failure.
    """
    # FUNCION AJAX
    # Function to delete a file in realtime with AJAX to create/modify vacancy
    try:
        object = Vacancy_Files.objects.get(pk=request.POST.get('id'))
        object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    except:
        tb = traceback.format_exc()
        print(tb)
        data = json.dumps("Error in deleting file.")
        return HttpResponse(content=data, status=400, content_type='application/json')

@login_required
def add_update_vacancy(request, vacancy_id=False):
    """
    Handle the creation and update of a job vacancy.

    This view allows authenticated recruiters with management rights to create or update
    a vacancy for their company. It supports both displaying the vacancy form and processing
    form submissions including file uploads related to the vacancy.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)
    subdomain_data =  subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
    try:
        recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
    except:
        recruiter=None
        raise Http404
    if not recruiter.is_manager():
        raise Http404
    # company = Company.objects.get(subdomain__slug=subdomain_data['active_subdomain'])
    company = recruiter.company.all()[0]
    if not company.check_service('JP_POST'):
        raise Http404
    stages = Stage.objects.filter(company = company)
    if vacancy_id:
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id,company__in=recruiter.company.all())
        vacancy_status = vacancy.status.codename
        if vacancy_status == 'closed':
            raise Http404
        if vacancy_status == 'finalized':
            finalized = True
        else:
            finalized = False
        # state_selected = vacancy.state
        industry_selected = vacancy.industry
        another_email = vacancy.another_email
        update = True
        # Random_number session variable serves to pre-load files to the system when
        # the user is just creating a job.
        # We removed/cleaned the variable random_number if they ave any value
        request.session['random_number'] = None
        # Get files that have a job
        objFiles = Vacancy_Files.objects.filter(vacancy=vacancy)
    else:
        vacancy = None
        vacancy_status = None
        state_selected = None
        industry_selected = None
        finalized = False
        another_email = False
        update = False

        # Variable of random_number session serves to pre-load files to the system when
        # the user is just creating a job.
        # If job is only created, check if the session variable has some value random_number
        # if in case we made a form submit and have validation errors, thus
        # retain the files even if the user does not fill well the other fields of the form.
        random_number = request.session.get('random_number')
        if not random_number:
            # If you do not have a value,we generate a random number that we serve to identify files
            # to upload or remove even if job id is not assigned.
            request.session['random_number'] = random.randint(100000, 999999)
        # print("random_number.- %s" % request.session.get('random_number'))
        # Get files with randome number if there
        objFiles = Vacancy_Files.objects.filter(random_number=request.session.get('random_number'))
    template = None
    if request.method == 'POST':
        # try:
        #     if int(request.POST['state']) == 0:
        #         state_selected = 0
        #     else:
        #         state_selected = State.objects.get(id=request.POST['state'])
        # except:
        #     state_selected = None
        if request.POST.get('template',None) and company.check_service('JP_TEMPLATE'):
            try:
                vacancy=Vacancy.objects.get(id=int(request.POST.get('template')), company=company)
                vacancy_form = VacancyForm(instance=vacancy,industry_selected=industry_selected, another_email=another_email,update=update, company_email=company.company_email,company = recruiter.company.all()[0])
                fileForm = VacancyFileForm()
                template = request.POST.get('template')
            except:
                raise Http404
        else:
            try:
                if int(request.POST['industry']) <= 0:
                    industry_selected = None
                else:
                    industry_selected = Company_Industry.objects.get(id=request.POST['industry'])
            except:
                industry_selected = None
            another_email = request.POST['another_email']
            try:
                email = request.POST['email']
            except:
                email = None
            pub_date = None
            if vacancy:
                status = vacancy.status
                editing_date = vacancy.editing_date
                end_date = vacancy.end_date
                pub_after = vacancy.pub_after
                message = _('We have successfully updated the job')
                pub_date = vacancy.pub_date
            vacancy_form = VacancyForm(instance=vacancy, data=request.POST, files=request.FILES, industry_selected=industry_selected,
                                       company_email=company.user.email, update=update, another_email=another_email, company = recruiter.company.all()[0])

            # Request.Files files are loaded if the browser has JavaScript disabled
            fileForm = VacancyFileForm(data=request.POST, files=request.FILES)
            if request.FILES and request.FILES.getlist('file'):
                # Validates the no of uloaded files even if JS is deactivated
                uploaded_files = len(request.FILES.getlist('file'))
                fileForm.validate_number_files(uploaded_files)

            if vacancy_form.is_valid() and fileForm.is_valid():
                import pdb 
                # pdb.set_trace()
                publish_now = True
                unpub_date = None
                if not update:
                    # If a new job
                    message = _('The Job opening has been successfuly published.')
                    if not vacancy_form.cleaned_data['pub_after']:
                        status = Vacancy_Status.objects.get(codename__exact='open')
                    elif vacancy_form.cleaned_data['pub_date'] == date.today():
                        unpub_date = vacancy_form.cleaned_data['unpub_date']
                        status = Vacancy_Status.objects.get(codename__exact='open')
                    else:
                        publish_now = False
                        unpub_date = vacancy_form.cleaned_data['unpub_date']
                        status = Vacancy_Status.objects.get(codename__exact='open')
                        message = _('The job opening has been successfuly scheduled.')
                    # 5 more days are assigned to edit the job
                    editing_date = vacancy_form.cleaned_data['pub_date'] + timedelta(days=5)
                    # The end date of job is assigned 30 days afte the publication date
                    end_date = vacancy_form.cleaned_data['pub_date'] + timedelta(30)
                    pub_after = vacancy_form.cleaned_data['pub_after']

                else:
                    publish_now = False
                    if pub_date <= date.today(): # Already published
                        if vacancy_form.cleaned_data['pub_after']: # Opted to Schedule
                            if vacancy_form.cleaned_data['pub_date'] > date.today(): # Scheduled for Future
                                vacancy.unpublish() # Unpublish
                                # Schedule
                                pub_after = vacancy_form.cleaned_data['pub_after']
                                pub_date = vacancy_form.cleaned_data['pub_date']
                                unpub_date = vacancy_form.cleaned_data['unpub_date']
                                editing_date = vacancy_form.cleaned_data['pub_date'] + timedelta(days=5)
                    else: # Not published yet
                        if vacancy_form.cleaned_data['pub_after']: # Opted to Schedule
                            if vacancy_form.cleaned_data['pub_date'] > date.today():  # Scheduled for Future
                                # schedule
                                pub_after = vacancy_form.cleaned_data['pub_after']
                                pub_date = vacancy_form.cleaned_data['pub_date']
                                unpub_date = vacancy_form.cleaned_data['unpub_date']
                                editing_date = vacancy_form.cleaned_data['pub_date'] + timedelta(days=5)
                            else: # Scheduled for Today
                                publish_now = True
                                unpub_date = vacancy_form.cleaned_data['unpub_date']
                                editing_date = date.today() + timedelta(days=5)
                                # publish
                            
                    # if not vacancy_form.cleaned_data['pub_after'] or vacancy_form.cleaned_data['pub_date'] == date.today():
                    #     finalized = True
                    # if finalized:
                    #     status = Vacancy_Status.objects.get(codename__exact='open')
                    #     pub_date = date.today()
                    #     # 5 more days are assigned to edit the job
                    #     editing_date = pub_date + timedelta(days=5)
                    #     # The end date of job is assigned 30 days after the date of publication
                    #     pub_after = False
                    #     message = _(u'We have updated and published the job')
                    # else:
                vacancy = vacancy_form.save(commit=False)
                if pub_date:
                    vacancy.pub_date = pub_date
                if not vacancy.user:
                    vacancy.user = request.user
                if not vacancy.company:
                    vacancy.company = recruiter.company.all()[0]
                vacancy.status = status
                if not vacancy.editing_date or pub_after:
                    vacancy.editing_date = editing_date
                vacancy.pub_after = pub_after
                if publish_now:
                    vacancy.publish()
                if unpub_date:
                    vacancy.unpub_date = unpub_date

                if vacancy.confidential:
                    vacancy.data_contact = False
                messages.success(request, "%s" % message)
                if email:
                    vacancy.email = email
                else:
                    vacancy.email = company.user.email

                vacancy.save()
                request.session['enableshare'] = True
                first_stage = Stage.objects.get(company=vacancy.company,name="New Candidates")
                last_stage = Stage.objects.get(company=vacancy.company,name="Onboarding")
                VacancyStage.objects.get_or_create(stage=first_stage, vacancy=vacancy, order=0,locked=True)
                VacancyStage.objects.get_or_create(stage=last_stage, vacancy=vacancy, order=100,locked=True)
                #### Transfer loaded/preloaded files to a job ###
                if request.FILES and request.FILES.getlist('file'):
                    # Create files even if browser JS is disabled
                    for f in request.FILES.getlist('file'):
                        Vacancy_Files.objects.create(file=f, vacancy=vacancy, random_numer=request.session.get('random_number'))

                if request.session.get('random_number'):
                    # If the job is new, we obtain the files that we go and have the same random_number of the session variable
                    uploaded_files = Vacancy_Files.objects.filter(random_number=request.session.get('random_number'))

                    for uploaded_file in uploaded_files:
                        # job assigned
                        uploaded_file.vacancy = vacancy
                        # Remove the field value random_number, to avoid duplicates in the future
                        uploaded_file.random_number = None

                        # We set the manager's name to create (Id Vacante), which move the files. full directory path
                        new_dir = os.path.join(settings.MEDIA_ROOT, uploaded_file.default_path, str(vacancy.pk))
                        # Get file full path
                        old_path = uploaded_file.file.path
                        # Establish the full path where you move files, ie new directory with the filename
                        new_path = os.path.join(new_dir, uploaded_file.filename())

                        try:
                            # We create the new directory
                            os.makedirs(new_dir)
                        except OSError as e:
                            if e.errno == 17:
                                # If the directory already exists:
                                pass

                        # Rename/Move the file
                        os.rename(old_path, new_path)
                        # We update the field value file in the database with new routes
                        uploaded_file.file.name = '%s/%s/%s' % (uploaded_file.default_path, str(vacancy.pk), uploaded_file.filename())
                        # We save the changes to the database
                        uploaded_file.save()

                    try:
                        # Remove the now empty old wallet
                        remove_dir = os.path.join(settings.MEDIA_ROOT, Vacancy_Files.default_path, Vacancy_Files.tmp_folder, str(request.session.get('random_number')))
                        os.rmdir(remove_dir)
                    except:
                        tb = traceback.format_exc()
                        print(tb)
                        pass

                # Removing session variable
                request.session['random_number'] = None
                #### End treatment of loaded/preloaded files to a job ###

                if not update:
                    # Notification email is sent on new job registration
                    # try:
                    # current_site = Site.objects.get_current()
                    url = request.scheme+'://%s/jobs/%s/' % (company.geturl().strip('/'), vacancy.pk)
                    date_mail = datetime.strftime(datetime.now(), '%d-%m-%Y %I:%M:%S %p')
                    body_email = 'Company: %s<br><br>Job: %s<br><br>Date: %s<br><br>Link: <a href="%s" target="_blank">%s</a>' % (company.name, vacancy.employment, date_mail, url, url)
                    send_email_to_TRM(subject='New Job Posted', body_email=body_email)
                    # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = 'all')
                    message_chunks = [
                        {
                            'subject': str(vacancy.employment),
                            'subject_action': '',
                            'action_url': vacancy.get_absolute_url(),
                        }
                    ]
                    post_activity(message_chunks = message_chunks, actor = request.user,action = 'created a new job opening - ', subject = str(vacancy.employment), subscribers = [r.user for r in company.recruiter_set.all().exclude(user = request.user)], action_url = vacancy.get_absolute_url())
                    # except:
                    #     pass
                else:
                    # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = 'all')
                    message_chunks = [
                            {
                                'subject': str(vacancy.employment),
                                'subject_action': '',
                                'action_url': vacancy.get_absolute_url(),
                            }
                        ]
                    post_activity(message_chunks = message_chunks, actor = request.user,action = 'updated job opening - ', subject=str(vacancy.employment), subscribers = [r.user for r in company.recruiter_set.all()], action_url = vacancy.get_absolute_url())
                return redirect(reverse('companies_add_update_vacancy_hiring_process', args=[vacancy.id]))
                # return redirect(reverse('vacancies_get_vacancy_details', args=[vacancy.pk])+'?manage=true')
            # return redirect(reverse('socialmultishare_share_to_social_media', args=[vacancy.pk]))
    else:
        if vacancy:
            vacancy_form = VacancyForm(instance=vacancy, industry_selected=industry_selected,
                             another_email=another_email, update=update, company_email = company.company_email, company = recruiter.company.all()[0])
        else:
            vacancy_form = VacancyForm(instance=vacancy, industry_selected=industry_selected,
                             another_email=another_email, update=update, company_email = company.company_email,
                             state=company.state, city=company.city, nationality=company.nationality, industry=company.industry, company = recruiter.company.all()[0])
        fileForm = VacancyFileForm()
    template_form  = TemplateForm()
    template_formset = FieldFormset()
    # raise ValueError()
    return render(request,'vacancies/add_update_vacancy.html',
                              {'isVacancy': True,
                               'vacancy_form': vacancy_form,
                               'vacancy_id': vacancy_id,
                               'user': request.user,
                               'vacancy_status': vacancy_status,
                               'objFiles': objFiles,
                               'fileForm': fileForm,
                               'stages': stages,
                               'company': company,
                               'update': update,
                               'template': template,
                               'template_form': template_form,
                               'template_formset': template_formset,
                               'template_form': template_form,
                               'template_formset': template_formset,
                               'page':1
                               })
                             

@login_required
def add_update_vacancy_hiring_process(request, vacancy_id = None):
    """
    View to display and manage the hiring process stages for a specific vacancy.
    - Requires the user to be authenticated and have an email registered.
    - Checks the active subdomain and verifies the user is a manager recruiter.
    - Validates the vacancy belongs to the recruiter's companies and is not removed.
    - Retrieves stages already added to the vacancy and all other stages available in the company.
    - Renders the 'add_update_vacancy_hiring_process.html' template with vacancy and stage data.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)    
    subdomain_data =  subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
    recruiter = get_object_or_404(Recruiter,user=request.user, user__is_active=True)
    if not recruiter.is_manager():
        raise Http404
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    if not company.check_service('JP_POST'):
        raise Http404
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id,company__in=recruiter.company.all())
    vacancy_status = vacancy.status.codename
    if vacancy_status == 'removed':
        raise Http404
    if vacancy_status == 'finalized':
        finalized = True
    else:
        finalized = False
    stages = VacancyStage.objects.filter(vacancy=vacancy)
    return render(request, 
        'vacancies/add_update_vacancy_hiring_process.html', 
        {
            'isVacancy': True,
            'vacancy_id': vacancy_id,
            'user': request.user,
            'vacancy_status': vacancy_status,
            'company': company,
            'vacancy': vacancy,
            'stages': stages,
            'page': 2,
            'allstages': Stage.objects.filter(company=vacancy.company).exclude(id__in=[stage.id for stage in stages])
        })

@login_required
def add_update_vacancy_talent_sourcing(request, vacancy_id = None):
    """
    View to add or update talent sourcing options for a specific vacancy.

    - Ensures authenticated user with registered email.
    - Validates active subdomain, manager recruiter role, and vacancy existence/status.
    - Retrieves external referers associated with the company for sourcing talent.
    - Renders the 'add_update_vacancy_talent_sourcing.html' template with relevant data.

    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)    
    subdomain_data =  subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
    recruiter = get_object_or_404(Recruiter,user=request.user, user__is_active=True)
    if not recruiter.is_manager():
        raise Http404
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    if not company.check_service('JP_POST'):
        raise Http404
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id,company__in=recruiter.company.all())
    vacancy_status = vacancy.status.codename
    if vacancy_status == 'removed':
        raise Http404
    if vacancy_status == 'finalized':
        finalized = True
    else:
        finalized = False

    # jobboard_referers = ExternalReferal.objects.filter(Q(company=company)|Q(company=None)).filter(referal_type='JB')
    external_referers = ExternalReferal.objects.filter(company=company, referal_type='ER')
    return render(request, 
        'vacancies/add_update_vacancy_talent_sourcing.html', 
        {
            'isVacancy': True,
            'vacancy_id': vacancy_id,
            'user': request.user,
            'vacancy_status': vacancy_status,
            'company': company,
            # 'jobboard_referers': jobboard_referers,
            'external_referers': external_referers,
            'vacancy': vacancy,
            'page': 3
        })

@login_required
def company_recommendations(request):
    """
    View to display recommendations sent to the authenticated user's company.

    - Requires the user to be authenticated and have an email registered.
    - Retrieves the company linked to the user.
    - Fetches recommendations directed to this company.
    - Renders 'recommendations.html' template with company and recommendations data.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is registered and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    company = get_object_or_404(Company, user=request.user)
    recommendations = Recommendations.objects.filter(to_company=company)
    return render(request,'recommendations.html',
                              {'isProfile': True, 'company': company, 'recommendations': recommendations})
   

@login_required
def first_search_curricula(request):
    """
    Initializes session variables for the curriculum search interface and redirects
    the user to the main curriculum search page.

    This function clears any previously stored search filters for both vacancies
    and candidates. It also sets default values for the curriculum search filters,
    such as age range, gender, and language preferences.

    If the user is authenticated but has no registered email, they are redirected
    to complete their email registration.
    """
    if request.user.is_authenticated and not request.user.email:
        # If the user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    # Sessions job search
    request.session['vacancies_search_industry'] = []
    request.session['vacancies_search_area'] = []
    request.session['vacancies_search_state'] = []
    request.session['vacancies_search_employment_type'] = []
    request.session['vacancies_search_pub_date'] = []
    request.session['vacancies_search_text'] = []
    request.session['pub_dates'] = []
    request.session['industries'] = []
    request.session['states'] = []
    request.session['employment_types'] = []

    # Curricula search sessions
    request.session['candidates_cvs'] = []
    request.session['first_search_cvs'] = True
    request.session['degrees'] = None
    request.session['status'] = None
    request.session['area'] = None
    request.session['careers'] = None
    request.session['state'] = None
    request.session['municipal'] = None
    request.session['gender'] = Gender.objects.get(codename='indistinct')
    request.session['min_age'] = 18
    request.session['max_age'] = 65
    request.session['travel'] = None
    request.session['residence'] = None
    request.session['language_1'] = None
    request.session['level_1'] = None
    request.session['language_2'] = None
    request.session['level_2'] = None
    request.session['candidates_cvs'] = []

    return redirect('companies_search_curricula')

@login_required
def search_curricula(request):
    """  Vista search depending on curricula filters the user selects """
    """
    Handles curriculum (CV) search based on user-selected filters from a form.

    This view manages both the GET and POST requests for curriculum filtering:
    - On GET, it displays a form and optionally paginated results from a previous session.
    - On POST, it processes the submitted search form and filters candidate CVs
      based on academic background, gender, location, language skills, and preferences
      such as willingness to travel or relocate.

    Filters are stored in the session to preserve state across page navigations.
    """
    if request.user.is_authenticated and not request.user.email:
        # If user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    # Candidates - Information of candidates from search form
    gender = request.session.get('gender')
    state = request.session.get('state')
    municipal = request.session.get('municipal')
    min_age = request.session.get('min_age')
    max_age = request.session.get('max_age')
    min_year = None
    max_year = None
    travel = request.session.get('travel')
    residence = request.session.get('residence')

    # Academic - Information of academics from search form
    degrees = request.session.get('degrees')
    area = request.session.get('area')
    careers = request.session.get('careers')
    status = request.session.get('status')

    # Languages - Informacion of languages from search form
    language_1 = request.session.get('language_1')
    level_1 = request.session.get('level_1')
    language_2 = request.session.get('language_2')
    level_2 = request.session.get('level_2')

    search_cvs = False
    today = datetime.now().date()

    # Pagination variables
    maximo_paginas = 1
    minimo_paginas = 0
    num_pages_visible = num_pages
    paginas_finales = 0
    link_anterior = 1
    link_siguiente = 1
    curricula_total = 0

    if request.method == 'POST':
        try:
            if request.POST['area'] == '':
                area = None
            else:
                area = Academic_Area.objects.get(id=request.POST['area'])
        except:
            area = None

        try:
            if int(request.POST['state']) <= 0:
                state_selected = None
            else :
                state_selected = State.objects.get(id=request.POST['state'])
        except:
            state_selected = None

        form_search_cvs = SearchCvForm(data=request.POST, files=request.FILES, area_selected=area, state_selected=state_selected)

        if form_search_cvs.is_valid():

            # Academic - Information of academics as per selection in form
            degrees = form_search_cvs.cleaned_data.get('degree')
            careers = form_search_cvs.cleaned_data.get('career')
            status = form_search_cvs.cleaned_data.get('status')

            # Candidate - Information of candidates as per selection in form
            gender = Gender.objects.get(id=int(request.POST['gender']))
            state = form_search_cvs.cleaned_data.get('state')
            municipal = form_search_cvs.cleaned_data.get('municipal')
            min_age = form_search_cvs.cleaned_data.get('min_age')
            min_year = date.today() - relativedelta(years=min_age)
            max_age = form_search_cvs.cleaned_data.get('max_age')
            max_year = date.today() - relativedelta(years=max_age)
            travel = form_search_cvs.cleaned_data.get('travel')
            residence = form_search_cvs.cleaned_data.get('residence')

            # Language - Information of languages as per selection in form
            language_1 = form_search_cvs.cleaned_data.get('language_1')
            level_1 = form_search_cvs.cleaned_data.get('level_1')
            language_2 = form_search_cvs.cleaned_data.get('language_2')
            level_2 = form_search_cvs.cleaned_data.get('level_2')
            
            request.session['degrees'] = degrees
            request.session['status'] = status
            request.session['area'] = area
            request.session['careers'] = careers
            request.session['state'] = state
            request.session['municipal'] = municipal
            request.session['gender'] = gender
            request.session['min_age'] = min_age
            request.session['max_age'] = max_age
            request.session['travel'] = travel
            request.session['residence'] = residence
            request.session['language_1'] = language_1
            request.session['level_1'] = level_1
            request.session['language_2'] = language_2
            request.session['level_2'] = level_2
            request.session['first_search_cvs'] = False

            search_cvs = True

    else:
        form_search_cvs = SearchCvForm()

    try:
        if request.GET['page']:
            request.session['first_search_cvs'] = False
    except:
        pass

    first_search_cvs = request.session.get('first_search_cvs')

    candidates = Candidate.objects.filter(pk__in=Curriculum.objects.filter(advance__gt=50).values('candidate')).order_by('-last_modified')
    total_candidates = len(candidates)

    if first_search_cvs:
        # If this is the firt time page is opened
        candidates = candidates[:1000]

    elif search_cvs:
        # If a search was conducted in form
        # candidates = Candidate.objects.filter(pk__in=Curriculum.objects.filter(advance__gt=50).values('candidate')).order_by('-last_modified')

        # Candidates filtering as per selection in form
        if candidates:
            if gender.codename != 'indistinct' or state or min_age != 18 or max_age != 65 or travel or residence:
                if gender and gender.codename != 'indistinct':
                    candidates = candidates.filter(gender=gender)
                if state:
                    candidates = candidates.filter(state=state)
                    if municipal:
                        candidates = candidates.filter(municipal__in=municipal)
                candidates = candidates.filter(birthday__range=[max_year, min_year])
                if travel:
                    candidates = candidates.filter(travel=travel)
                if residence:
                    candidates = candidates.filter(residence=residence)

        # Acedemic filering as per selection in form
        if degrees or area or careers or status:
            academic_objs = Academic.objects.filter(candidate__in=candidates)
            if degrees:
                academic_objs = academic_objs.filter(degree__in=degrees)
            if area:
                academic_objs = academic_objs.filter(area=area)
            if careers:
                academic_objs = academic_objs.filter(career__in=careers)
            if status:
                academic_objs = academic_objs.filter(status__in=status)

            candidates = candidates.filter(pk__in=academic_objs.all().values('candidate'))

        # Language filtering as per selection in form
        if language_1 or language_2:
            language_objs = CV_Language.objects.filter(candidate__in=candidates)
            language_objs_1 = None
            language_objs_2 = None

            # Language 1
            if language_1:
                language_objs_1 = language_objs.filter(language=language_1, level__in=level_1)
            # Language 2
            if language_2:
                language_objs_2 = language_objs.filter(language=language_2, level__in=level_2)

            if language_objs_1 and language_objs_2:
                language_objs = language_objs_1.filter(candidate__in=language_objs_2.values('candidate'))
            elif language_objs_1:
                language_objs = language_objs_1
            elif language_objs_2:
                language_objs = language_objs_2

            candidates = candidates.filter(pk__in=language_objs.all().values('candidate'))

    else:
        # If you click on the Pager, candidates obtained previously are filtered
        candidates_cvs = request.session.get('candidates_cvs')
        candidates = Candidate.objects.filter(pk__in=candidates_cvs)

    # It is stored in the list 'curricula' information pooled CV of the candidates obtained
    curricula = []
    if candidates:
        if len(candidates) > 600:
            # The number of candidates is limited to leverage the system
            candidates = candidates.all()[:600]

        candidates_cvs = []

        for candidate in candidates:
            expertises = Expertise.objects.filter(candidate=candidate)
            academics = Academic.objects.filter(candidate=candidate)
            languagues = CV_Language.objects.filter(candidate=candidate)
            softwares = CV_Software.objects.filter(candidate=candidate)
            curricula.append([candidate, expertises, academics, languagues, softwares])
            candidates_cvs.append(candidate.pk)

        curricula_total = len(curricula)

        # They are stored in the session variable only the IDs of the candidates are filtered
        request.session['candidates_cvs'] = candidates_cvs

        # Pagination
        paginator = Paginator(curricula, number_objects_page)
        page = request.GET.get('page')
        try:
            curricula = paginator.page(page)
        except PageNotAnInteger:
            curricula = paginator.page(1)
        except EmptyPage:
            curricula = paginator.page(paginator.num_pages)

        if curricula.paginator.num_pages > num_pages_visible:
            maximo_paginas=num_pages_visible
            minimo_paginas=1
        elif curricula.number > curricula.paginator.num_pages-(num_pages_visible/2):
            maximo_paginas=curricula.paginator.num_pages
            minimo_paginas=curricula.paginator.num_pages-num_pages_visible
        else:
            minimo_paginas=curricula.number-(num_pages_visible/2)
            maximo_paginas=curricula.number+(num_pages_visible/2)
        link_anterior = 1
        link_siguiente = curricula.paginator.num_pages
        if curricula.paginator.num_pages > maximo_paginas + 4:
            link_siguiente = maximo_paginas + 4
        if 1 < minimo_paginas - 4:
            link_anterior = minimo_paginas - 4
        paginas_finales = paginator.num_pages-num_pages_visible

    return render(request,'search_curricula.html',
                              {'form_search_cvs': form_search_cvs,
                               'today': today,
                               'total_candidates': total_candidates,
                               'curricula': curricula,
                               'first_search_cvs': request.session.get('first_search_cvs'),

                               # Academic - Information of Tudy collected in form
                               'degrees': request.session.get('degrees'),
                               'status': request.session.get('status'),
                               'area': request.session.get('area'),
                               'careers': request.session.get('careers'),

                               # Candidate - Information of Candidates selected in Form
                               'gender': request.session.get('gender'),
                               'state': request.session.get('state'),
                               'municipal': request.session.get('municipal'),
                               'min_age': request.session.get('min_age'),
                               'min_year': min_year,
                               'max_age': request.session.get('max_age'),
                               'max_year': max_year,

                               # Language - Information of Languages selected in form
                               'language_1': request.session.get('language_1'),
                               'level_1': request.session.get('level_1'),
                               'language_2': request.session.get('language_2'),
                               'level_2':  request.session.get('level_2'),

                               'travel': request.session.get('travel'),
                               'residence': request.session.get('residence'),

                               # Pagination
                               'maximo_paginas': maximo_paginas,
                               'minimo_paginas': minimo_paginas,
                               'paginas_finales': paginas_finales,
                               'curricula_total': curricula_total,
                               'link_siguiente': link_siguiente,
                               'link_anterior': link_anterior,
                               'num_pages_visible':num_pages_visible,
                              })
                              
@login_required
def company_wallet(request):
    """
    Displays the company's wallet information and recent wallet movements.

    This view retrieves the wallet associated with the authenticated user's company,
    fetches all wallet transactions, and renders them in the wallet template.
    """
    company = get_object_or_404(Company, user=request.user)
    company_wallet = Wallet.objects.get(company=company)
    wallet_movements = Wallet_Movements.objects.filter(company=company)
    last_movement = wallet_movements.first()
    return render(request,'company_ wallet.html',
                              {'isProfile': True,
                               'company': company,
                               'company_wallet': company_wallet,
                               'last_movement': last_movement,
                               'wallet_movements': wallet_movements})
                              
@xframe_options_exempt
def widget_jobs(request):
    """
    Renders a widget view displaying the current job vacancies for a company.

    This view checks the subdomain from the request to identify the company.
    It supports public access (no login required) and a preview mode.
    Optionally filters jobs by status if `vacancy_status_name` is provided.

    If the user is authenticated and is a recruiter, their profile is validated.
    """
    vacancy_status_name=None
    subdomain_data = subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
    if request.user.is_authenticated and request.user.profile.codename == 'recruiter':
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        except:
            return redirect('companies_record_company')
    else:
        recruiter=None
    try:
        company = Company.objects.get(subdomain__slug=subdomain_data['active_subdomain'])
    except:
        raise Http404
    if vacancy_status_name and not recruiter:
        raise Http404
    if vacancy_status_name:
        vacancy_status = Vacancy_Status.objects.filter(codename=vacancy_status_name)
        if not vacancy_status:
            raise Http404
        else:
            vacancy_status = vacancy_status[0]
    else:
        vacancy_status = Vacancy_Status.objects.get(codename='open')
    if request.GET.get('preview'):
        preview = True
    else:
        preview = False
    statuses = Vacancy_Status.objects.all()
    vacancies = Vacancy.publishedjobs.filter(company = company)
    return render(request,'vacancies/widget_summary.html',{
                                            'isVacancy':True,
                                            'vacancy_status': vacancy_status,
                                            'statuses': statuses,
                                            'vacancies': vacancies,
                                            'company': company,
                                            'preview': preview
                                            })
                                           

@login_required
def billing(request):
    """
    Handles subscription billing and payment planning for recruiter-associated companies.

    Validates user permissions (must be a recruiter admin) and retrieves the current
    subscription plan. Calculates:
    - Consolidated balance carry forward.
    - Price differences for switching plans.
    - Renewal and per-user charges.

    If a plan change is initiated (via POST or session), updates the billing info
    accordingly, handling extra user limits and providing feedback.
    """
    if not request.user.profile.codename == 'recruiter'  or not request.user.recruiter.is_admin():
        raise Http404
    recruiter = request.user.recruiter
    company = recruiter.company.all()
    if not company:
        raise Http404
    company = company[0]
    payment_min = 5
    amount_to_pay = 0.00
    carried_forward_balance = 0.00
    carried_forward_message = None
    slab = None
    future_slab = None
    try:
        subscription = company.subscription
    except:
        Subscription.objects.create(company = company,price_slab = PriceSlab.objects.get(id=2))
        company.refresh_from_db()
    current_slab = company.subscription.price_slab
    client_token = None
    hasSufficientCredit = False
    remove_users = False
    compulsary_remove = False
    renewal = 0.00
    post_payment = False
    if request.method == 'POST' or request.session.get('slab'):
        success=True
        # try:
        #     user_count = int(request.POST.get('user_count'),0)
        # except:
        #     user_count = 0

        if request.session.get('slab'):
            # raise ValueError(request.session)
            plan = request.session.get('slab')
            request.session['slab'] = None
            post_payment = True
        else:
            post_payment = False
            plan = request.POST.get('plan',0)
        user_count = company.recruiter_set.all().count()
        if plan:
            slab = PriceSlab.objects.get(id = plan)
        else:
            slab = current_slab
        try:
            future_slab = company.scheduledtransactions_set.all()[0].price_slab
        except:
            future_slab = slab
        max_users = slab.package.max_users
        consolidation_ratio = 1
        if current_slab.expiry_period:
            consolidation_ratio = Decimal((company.subscription.expiry - datetime.now()).days)/Decimal(current_slab.expiry_period)
        if consolidation_ratio < 0:
            consolidation_ratio = 1
        if current_slab != slab:
            if not max_users == 0 and user_count > max_users:
                if company.subscription.expired():
                    compulsary_remove = True
                remove_users = True  
            if not slab.amount:
                slab.amount = Decimal(0.00)
            if not current_slab.amount:
                current_slab.amount = Decimal(0.00)
            period = Decimal(current_slab.expiry_period)
            if not period:
                period = 1
            if company.subscription.expiry:
                days_left = Decimal((company.subscription.expiry - datetime.now()).days)
            else:
                days_left = 0
            carried_forward_balance = (days_left/period)*current_slab.amount
            price_diff = slab.amount - carried_forward_balance
            amount_to_pay = price_diff
                # raise ValueError()

            if amount_to_pay < 0:
                amount_to_pay = 0
            """# else:
            #     if slab.amount:
            #         amount_to_pay = slab.amount
            #     else:
            #         amount_to_pay = 0
            # DO updates
        # else:"""

        if not remove_users:
            pass
        renewal = slab.amount
        user_amount_to_pay = company.subscription.added_users * current_slab.price_per_user * consolidation_ratio
        if user_amount_to_pay > 0:
            carried_forward_message = '<span class="text-success">'
            if slab.currency:
                carried_forward_message = carried_forward_message + str(slab.currency.symbol) + str(round(carried_forward_balance,2)) + '</span> from plan subscriptions and <span class="text-success">' + str(slab.currency.symbol) + str(round(user_amount_to_pay,2)) + '</span> from additional user subscriptions'
            else:
                carried_forward_message = carried_forward_message + '$' + str(round(carried_forward_balance,2)) + '</span> from plan subscriptions and <span class="text-success"> $' + str(round(user_amount_to_pay,2)) + '</span> from additional user subscriptions'

        else:
            carried_forward_message = 'From Plan subscriptions'
        carried_forward_balance = Decimal(carried_forward_balance) + Decimal(user_amount_to_pay)
        if current_slab == slab:
            carried_forward_balance = 0.00
        # if 'new_plan' in request.session:
        #     try:
        #         new_slab_id = int(request.session['new_plan'])
        #     except:
        #         new_slab_id = 0
        #     new_slab = PriceSlab.objects.filter(id = new_slab_id)
        #     if new_slab:
        #         new_slab = new_slab[0]
        #     else:
        #         new_slab = None
        # else:
            # new_slab = None
        # if not new_slab == slab:
        #     request.session['new_plan'] = ""
        total_users = company.recruiter_set.all().count()
        max_allowed = slab.package.max_users
        if max_allowed and not max_allowed == 0:
            additional = max_allowed - slab.package.free_users
        else:
            additional = -1
        if additional > 0:
            if user_count> 0 and user_count > additional:
                messages.error(request,'You are exceeding the additional users limit of ' + str(additional) + ' users. Please recheck!')
                # raise ValueError()
                success = False
            else:
                renewal = renewal + (additional * slab.price_per_user)
    else:
        renewal = current_slab.amount
        if company.subscription.added_users > 0:
            renewal = renewal + (company.subscription.added_users * current_slab.price_per_user)
    return render(request,'company_profile.html',{
                            'isPayments': True,
                            'isBilling': True,
                            'client_token': client_token,
                            'payment_min': payment_min,
                            'slab': slab,
                            'future_slab': future_slab,
                            'current_slab': current_slab,
                            'company': company,
                            'hasSufficientCredit': hasSufficientCredit,
                            'compulsary_remove': compulsary_remove,
                            'remove_users': remove_users,
                            'amount_to_pay': Decimal(amount_to_pay),
                            'carried_forward_balance': carried_forward_balance,
                            'carried_forward_message': carried_forward_message,
                            'renewal': renewal,
                            'post_payment': post_payment,
                            })
@login_required
def template_editor(request):
    """
    Open the visual site-template editor for the recruiter’s public careers
    page.

    Workflow:
    1. Verify the logged-in user is a **recruiter** with at least *manager*
       privileges.
    2. Locate the company by its active sub-domain and confirm the recruiter
       belongs to that company.
    3. Resolve the current `site_template` (e.g. *t-1*, *t-2* …) and assert the
       underlying template file (`careers/base/t-X/jobs.html`) exists.  
       If it does **not** exist, an error message is queued and the user is
       redirected to the template-selection screen.
    4. Render *careers/site_editor.html*, which loads the WYSIWYG editor that
       lets users customise the `above_jobs`, `jobs`, and `below_jobs` partials.
    """
    if not request.user.profile.codename == 'recruiter'  or not request.user.recruiter.is_manager():
        raise Http404
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        raise Http404
    recruiter = request.user.recruiter
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    if not company in request.user.recruiter.company.all():
        raise Http404
    try:
        template = company.site_template
        template = 'careers/base/t-'+ str(template) +'/jobs.html'
        get_template(template)
    except TemplateDoesNotExist:
        messages.error(request, 'Oops! The requested template was not found. Please select a valid template to edit.')
        return redirect('companies_site_management', 'template')
    return render(request, 'careers/site_editor.html',{'company': company})

@login_required
def site_template_preview(request, template_id = None):
    """
    Display a live preview of a specific careers-site template.

    The preview shows how the company’s published vacancies will appear inside
    the selected template **without** permanently changing the active
    `site_template`.

    """
    if not request.user.profile.codename == 'recruiter'  or not request.user.recruiter.is_manager():
        raise Http404
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        raise Http404
    recruiter = request.user.recruiter
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    if not company in request.user.recruiter.company.all():
        raise Http404
    try:
        template = int(template_id)
        if not template:
            template = company.site_template
        if not template:
            messages.error(request, 'Oops! The requested template was not found. Please select a valid template to preview.')
            return redirect('companies_site_management', 'template')

        template = 'careers/base/t-'+ str(template) +'/jobs.html'
        get_template(template)
    except:
        messages.error(request, 'Oops! The requested template was not found. Please select a valid template to preview.')
        return redirect('companies_site_management', 'template')
    vacancies = Vacancy.publishedjobs.filter(company = company)
    template = 'careers/base/root.html'
    above_jobs_template = 'careers/base/t-' + str(template_id) + '/above_jobs.html'
    jobs_template = 'careers/base/t-' + str(template_id) + '/jobs.html'
    stylesheet = 'sa-ui-kit/t-' + str(template_id) + '/style.css'
    below_jobs_template = 'careers/base/t-' + str(template_id) + '/below_jobs.html'
    return render(
        request, 
        template, {
            'company': company,
            'vacancies':vacancies, 
            'isPreview': True, 
            'above_jobs_template':above_jobs_template,
            'jobs_template':jobs_template,
            'below_jobs_template': below_jobs_template,
            'stylesheet':stylesheet
        }
    )

@login_required
def get_site_template(request):
    """
    Serve the **public** careers page using the company’s current template in
    “edit” mode.

    This endpoint is called by the in-browser template editor to refresh the
    page after changes.  It embeds the three editable partials
    (`above_jobs.html`, `jobs.html`, `below_jobs.html`) as well as the template-
    specific stylesheet.
    """
    if not request.user.profile.codename == 'recruiter'  or not request.user.recruiter.is_manager():
        raise Http404
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        raise Http404
    company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
    if not company in request.user.recruiter.company.all():
        raise Http404
    template = company.site_template
    template = 'careers/base/t-'+ str(template) +'/jobs.html'
    try:
        get_template(template)
    except TemplateDoesNotExist:
        messages.error(request, 'Oops! The requested template was not found. Please select a valid template to preview.')
        raise Http404
    template = 'careers/base/root.html'
    above_jobs_template = 'careers/base/t-' + str(company.site_template) + '/above_jobs.html'
    jobs_template = 'careers/base/t-' + str(company.site_template) + '/jobs.html'
    below_jobs_template = 'careers/base/t-' + str(company.site_template) + '/below_jobs.html'
    stylesheet = 'sa-ui-kit/t-' + str(company.site_template) + '/style.css'
    vacancies = Vacancy.publishedjobs.filter(company=company)
    return render(request, template, {
        'company':company,
        'vacancies':vacancies,
        'editing':True,
        'above_jobs_template':above_jobs_template,
        'jobs_template':jobs_template,
        'below_jobs_template': below_jobs_template,
        'stylesheet':stylesheet})