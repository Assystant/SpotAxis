"""AJAX View Handlers for SpotAxis Application

This module contains Django view functions that handle asynchronous (AJAX) requests for the SpotAxis
recruitment platform. It provides endpoints for various interactive features including candidate
management, vacancy handling, form validation, and user interactions.

Key Functional Areas:
-------------------
1. Candidate Management
   - Profile filtering and search
   - Academic and career information updates
   - CV generation and management
   - Form validation for various candidate sections (personal, contact, academic, etc.)

2. Vacancy Processing
   - Vacancy application handling
   - Stage management
   - Question answering
   - Favorite/unfavorite functionality
   - Candidate comparison and filtering

3. User Interaction
   - Authentication (ajax_login)
   - Notifications
   - Comments and ratings
   - Social sharing
   - Messaging and communication

4. Company Operations
   - Member management
   - Permission updates
   - Template management
   - External referral handling

5. Scheduling and Planning
   - Interview scheduling
   - Plan management
   - Recurring updates
   - Upcoming schedule retrieval

Security Note:
------------
Many endpoints are decorated with @csrf_exempt, which disables CSRF protection. This is a potential
security risk and should be reviewed for proper CSRF protection implementation.

Dependencies:
------------
- Django framework
- Various models from candidates, companies, payments, and vacancies apps
- Custom forms and utilities
- External services for social media integration

Response Format:
--------------
Most endpoints return JSON responses (application/json) or plain text (text/plain) depending on
the data being returned. Error handling is implemented throughout the module with appropriate
HTTP status codes.

Usage:
-----
These endpoints are typically called via AJAX from the frontend JavaScript code. They expect
specific POST parameters and return structured responses that are handled by the frontend.

Example:
    POST /ajax/vacancies_postulate/
    Parameters: vacancy_id, candidate_id
    Returns: JSON response with application status

Note:
----
This module is a critical component of the application's interactive features and should be
maintained with careful consideration of security implications, especially regarding the
@csrf_exempt decorators.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import json
import traceback
from activities.utils import *
from candidates.forms import AcademicForm, CandidateForm, CvLanguageForm, ExpertiseForm, ObjectiveForm, cv_FileForm, \
    TrainingForm, CertificateForm, ProjectForm, InterestsForm, HobbiesForm, ExtraCurricularsForm, OthersForm, CandidateContactForm
from candidates.models import Academic_Status, Candidate, Curriculum, Academic, Expertise, Training, Certificate, Project, CV_Language
from common.forms import ContactForm
from common.models import Degree, send_TRM_email, User, send_email_to_TRM, SocialAuth
from common.views import revoke_token
from companies.models import Stage, Company, Subdomain, Recruiter, Ban, ExternalReferal
from customField.forms import TemplateForm, FieldFormset, TemplatedForm
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.messages import get_messages
from django.core import serializers
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from hashids import Hashids
from payments.models import *
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, Context, TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from scheduler.models import Schedule
from TRM.context_processors import subdomain
from TRM.settings import ROOT_DOMAIN, STATIC_URL
from urllib.parse import parse_qsl
from utils import validate_code, posttofbprofile, posttofbgroup,posttofbpage, posttoliprofile, posttolicompany, posttotwitter
from vacancies.forms import Public_FilesForm, diff_month
from vacancies.models import Question, VacancyStage, Vacancy, Comment, Postulate_Stage, Postulate_Score
from vacancies.models import Vacancy, Postulate, Salary_Type, Candidate_Fav , VacancyTags
from validate_email import validate_email
from utils import is_ajax

def filter_text_from_profile(arr=[], postulate_ids = [], public = False):
    """Filter candidate profiles based on text search criteria.

    Args:
        arr (list): List of search terms to filter by
        postulate_ids (list): List of postulate IDs to search within
        public (bool): Whether to search in public postulates

    Returns:
        list: List of matching postulate IDs
    """
    postulates = Postulate_Stage.objects.filter(id__in=postulate_ids)
    pps = Postulate_Stage.objects.none()
    for text in arr:
        pp = postulates.filter(Q(postulate__candidate__first_name__icontains=text) \
                            | Q(postulate__candidate__last_name__icontains = text) \
                            | Q(postulate__candidate__objective__icontains = text) \
                            | Q(postulate__candidate__interests__icontains = text) \
                            | Q(postulate__candidate__hobbies__icontains = text) \
                            | Q(postulate__candidate__others__icontains = text) \
                            | Q(postulate__candidate__skills__icontains = text) \
                            | Q(postulate__candidate__extra_curriculars__icontains = text) \
                            | Q(postulate__candidate__public_email__icontains = text) \
                            | Q(postulate__description__icontains = text) \
                            | Q(postulate__candidate__user__email__icontains = text) \
                        )
        pps = pps | pp
        ids = []
        for postulate in postulates:
            filtera = postulate.postulate.candidate.training_set.all().filter( \
                    Q(name__icontains = text) \
                    | Q(description__icontains = text) \
                )
            if filtera:
                ids = ids + [postulate.id]
                continue
            filterb = postulate.postulate.candidate.certificate_set.all().filter( \
                    Q(name__icontains = text) \
                    | Q(description__icontains = text) \
                )
            if filterb:
                ids = ids + [postulate.id]
                continue
            filterc = postulate.postulate.candidate.project_set.all().filter( \
                    Q(name__icontains = text) \
                    | Q(description__icontains = text) \
                )
            if filterc:
                ids = ids + [postulate.id]
                continue
            filterd = postulate.postulate.candidate.expertise_set.all().filter( \
                    Q(company__icontains = text) \
                    | Q(employment__icontains = text) \
                    | Q(tasks__icontains = text) \
                    | Q(industry__name__icontains = text) \
                )
            if filterd:
                ids = ids + [postulate.id]
                continue
            filtere = postulate.postulate.candidate.academic_set.all().filter( \
                    Q(area__icontains = text) \
                    | Q(course_name__icontains = text) \
                    | Q(school__icontains = text) \
                    | Q(degree__name__icontains = text) \
                )
            if filtere:
                ids = ids + [postulate.id]
                continue
            filterf = postulate.postulate.candidate.cv_language_set.all().filter( \
                    Q(language__name__icontains = text) \
                )
            if filterf:
                ids = ids + [postulate.id]
                continue
            filterg = False
            text = text.lower()
            curriculum = postulate.postulate.candidate.curriculum_set.all()[0]
            if curriculum.file:
                ftext = curriculum.file_text().lower()
                if text in ftext:
                    filterg = True
            if filterg:
                ids = ids + [postulate.id]
                continue                    
        pp = postulates.filter(id__in=ids)
        pps = pps | pp
    return list(set([p.id for p in pps]))

def companies_change_academic_area(request):
    """Update available careers based on selected academic area.

    Args:
        request: HTTP request containing area ID

    Returns:
        HttpResponse: JSON serialized career data
    """
    id_area = request.POST.get('id')
    data = ""
    try:
        careers = Academic_Career.objects.filter(area_id=id_area)
        data = serializers.serialize('json', careers, fields=('pk', 'name'))
    except:
        pass
    return HttpResponse(data, content_type='application/json')

def companies_allow_career(request):
    """Get degree codenames for selected career IDs.

    Args:
        request: HTTP request containing selected career IDs

    Returns:
        HttpResponse: JSON serialized degree data
    """
    selected_ids = request.POST.getlist('selected_ids[]')
    degree_ids = []
    for selected_id in selected_ids:
        degree_ids.append(int(selected_id))
    degrees = Degree.objects.filter(id__in=degree_ids)
    data = serializers.serialize('json', degrees, fields=('codename'))
    return HttpResponse(data, content_type='application/json')

def companies_change_state(request):
    """Get municipalities for selected state.

    Args:
        request: HTTP request containing state ID

    Returns:
        HttpResponse: JSON serialized municipality data
    """
    id_state = request.POST.get('id')
    municipals = Municipal.objects.filter(state_id=id_state)
    data = serializers.serialize('json', municipals, fields=('pk', 'name'))
    return HttpResponse(data, content_type='application/json')

def candidates_change_degree(request):
    """Get degree codename for selected degree ID.

    Args:
        request: HTTP request containing degree ID

    Returns:
        HttpResponse: Degree codename as plain text
    """
    degree = ""
    try:
        degree = Degree.objects.get(pk=request.POST.get('id')).codename
    except:
        pass
    return HttpResponse(degree, content_type="text/plain")

def candidates_change_career(request):
    """Get career codename for selected career ID.

    Args:
        request: HTTP request containing career ID

    Returns:
        HttpResponse: Career codename as plain text
    """
    career = ""
    try:
        career = Academic_Career.objects.get(pk=request.POST.get('id')).codename
    except:
        pass
    return HttpResponse(career, content_type="text/plain")

def candidates_change_academic_status(request):
    """Get academic status codename for selected status ID.

    Args:
        request: HTTP request containing status ID

    Returns:
        HttpResponse: Status codename as plain text
    """
    status = ""
    try:
        status = Academic_Status.objects.get(id=request.POST.get('id')).codename
    except:
        pass
    return HttpResponse(status, content_type="text/plain")

def get_salarytype_codename(request):
    """Get salary type codename for selected salary type ID.

    Args:
        request: HTTP request containing salary type ID

    Returns:
        HttpResponse: Salary type codename as plain text
    """
    codename = ""
    try:
        codename = Salary_Type.objects.get(id=request.POST.get('id')).codename
    except:
        pass
    return HttpResponse(codename, content_type="text/plain")

def vacancies_answer_question(request):
    """Handle candidate's answer to a vacancy question.

    Args:
        request: HTTP request containing question ID and answer

    Returns:
        HttpResponse: Success or error message
    """
    try:
        # Register Response
        question_id = request.POST.get('id')
        question = Question.objects.get(id=question_id)
        answer = request.POST.get('answer')
        question.answer = answer
        question.answer_date = datetime.now()
        question.save()

        # Send email notification
        context_email = {
            'question': question,
            'vacancy_answer_question': True,
        }
        subject_template_name = 'mails/answer_vacancy_email_subject.html',
        email_template_name = 'mails/answer_vacancy_email.html',
        send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=question.user.email)

        data = _('We have succesfully released a response.')
        # messages.info(request, message)
    except:
        tb = traceback.format_exc()
        print(tb)
        data = _('An error has occured, please try again.')
        # messages.error(request, message)

    return HttpResponse(data)

def vacancies_postulate(request):
    """Handle candidate's application to a vacancy.

    Args:
        request: HTTP request containing vacancy and candidate information

    Returns:
        HttpResponse: Application status or error message
    """
    if is_ajax(request):
        vacancy_id = request.GET.get('vacancy_id')
        referer = request.GET.get('referer')
        if referer:
            try:
                referer = Recruiter.objects.get(id=int(referer))
            except:
                referer = None
        else:
            referer = None
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        company = vacancy.company
        if not vacancy.postulate:
            return HttpResponse('not-postulate')
        candidate = get_object_or_404(Candidate, user=request.user)
        try:
            curriculum = Curriculum.objects.get(candidate=candidate)

            if curriculum.advance < 50:
                return HttpResponse('incomplete')
        except Curriculum.DoesNotExist:
            return HttpResponse('not-exist')
        e_mail = candidate.user.email
        ban1 = Ban.objects.filter(email__iexact = e_mail, company = company, ban_function = None)
        ban2 = Ban.objects.filter(email__iexact = e_mail, company = company, ban_function__iexact = vacancy.function)
        if ban1:
            ban1 = ban1[0]
            if diff_month(datetime.now(), ban1.add_now) < ban1.duration:
                messages.error(request,'You have been restricted from applying to this company\'s open positions within %s months of your last application' % ban1.duration)
        elif ban2:
            ban2 = ban2[0]
            if diff_month(datetime.now(), ban2.add_now) < ban2.duration:
                messages.error(request,'You have been restricted from applying to this company\'s open positions within %s months of your last application' % ban2.duration)
        first_stage = VacancyStage.objects.get(order=0,vacancy = vacancy)
        # pp = Public_Postulate.objects.filter(email = request.user.email, vacancy = vacancy)
        # if pp:
        #     return HttpResponse('postulated')
        postulate, created = Postulate.objects.get_or_create(vacancy=vacancy, candidate=candidate, vacancy_stage = first_stage)
        if created:
            # If you had not previously applied
            if referer:
                postulate.recruiter = referer
                postulate.save()
                text = 'Application Received for the job opening by referal'
            else:
                text = 'Application Received for the job opening'
            Comment.objects.create(postulate = postulate, comment_type=3, text=text)
            vacancy.applications += 1
            vacancy.save()
            try:
                academic = Academic.objects.filter(candidate=candidate)[:1].get()
            except:
                academic = None
            file_path = None
            if curriculum.file:
                file_path =str(curriculum.file.path)
            #  Send email to recruiter
            context_email = {
                'candidate': candidate,
                'vacancy': vacancy,
                'new_postulate': True,
                'file_path': file_path,
                'academic': academic,
            }
            subject_template_name = 'mails/new_postulate_subject.html',
            email_template_name = 'mails/new_postulate_email.html',
            send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=vacancy.email,file=file_path)
            if not referer:
                message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': postulate.get_absolute_url(),
                    }
                ]
            else:
                message_chunks = [
                    {
                        'subject': str(referer),
                        'subject_action': '',
                        'action_url': '',
                    },
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': ' and was refered by - ',
                        'action_url': postulate.get_absolute_url(),
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user, action = 'applied for job opening - ', subject = str(vacancy.employment), action_url = postulate.get_absolute_url(), activity_type = 1, postulate_id = postulate.id)
        else:
            return HttpResponse('postulated')
        # except:
        #     tb = traceback.format_exc()
        #     print(tb)
        #     return HttpResponse('error')
        return HttpResponse('success')
    else:
        raise Http404

def mark_unmark_vacancy_as_favorite(request):
    """Toggle favorite status for a vacancy.

    Args:
        request: HTTP request containing vacancy ID

    Returns:
        HttpResponse: Updated favorite status
    """
    try:
        vacancy_id = request.GET.get('id')
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        candidate = get_object_or_404(Candidate, user=request.user)
        vacancy_fav, created = Candidate_Fav.objects.get_or_create(vacancy=vacancy, candidate=candidate)
        if created:
            message_fav = 'marked'
        else:
            vacancy_fav.delete()
            message_fav = 'unmarked'
    except:
        tb = traceback.format_exc()
        print(tb)
        message_fav = 'error'
    return HttpResponse(message_fav)

def ajax_login(request):
    """Handle AJAX-based user authentication.

    Args:
        request: HTTP request containing login credentials

    Returns:
        JsonResponse: Authentication status and user data
    """
    context = {}
    context['success'] = False
    if is_ajax(request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            context['success'] = True
    return JsonResponse(context)

@csrf_exempt
def add_stage(request):
    context={}
    context['success'] = False
    context['auth'] = is_ajax(request)
    subdomain_data = subdomain(request)
    if is_ajax(request) and request.user.is_authenticated:
        stage_name = request.POST['stage_name']
        try:
            company = Company.objects.get(subdomain__slug=subdomain_data['active_subdomain'])
        except:
            company = None
        if company and company.check_service('AT_CUSTOM_HIRING_PROCESS'):
            stage = Stage.objects.create(name=stage_name, company=company)
            stage.save()
            context['success'] = True
            context['id'] = stage.id
    return JsonResponse(context)

@csrf_exempt
def update_vacancy_stage(request):
    context={}
    context['success'] = False
    if request.method == 'POST' and request.user.is_authenticated:
        vacancy = Vacancy.objects.filter(id=request.POST['vacancy'])
        if vacancy:
            vacancy = vacancy[0]
            recruiter = Recruiter.objects.filter(user=request.user,company = vacancy.company, user__is_active=True)
            if recruiter and vacancy.company.check_service('AT_CUSTOM_HIRING_PROCESS'):
                stages = request.POST.get('stage_ids',None)
                if stages:
                    stages = stages.split(',')
                vacancy_stages = VacancyStage.objects.filter(vacancy=vacancy).exclude(order__in=[0,100])
                if vacancy.postulated.all().filter(finalize = True):
                    context['msg'] = "You have Candidates in Onboarding. You cannot update the process now."
                else:      
                    locked_count = 0          
                    for stage in vacancy_stages:
                        # count0 = int(stage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count()) + int(stage.public_postulate_set.all().filter(vacancy = vacancy).exclude(discard=True).count())
                        # count1 = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count()) + int(Public_Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count())
                        # count2 = int(stage.postulate_set.all().filter(vacancy=vacancy,discard=True).count()) + int(stage.public_postulate_set.all().filter(vacancy=vacancy, discard = True).count())
                        # count3 = int(Postulate.objects.filter(vacancy=vacancy,finalize=True).count()) + int(Public_Postulate.objects.filter(vacancy=vacancy,finalize=True).count())
                        count0 = int(stage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count())
                        count1 = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count())
                        count2 = int(stage.postulate_set.all().filter(vacancy=vacancy,discard=True).count())
                        count3 = int(Postulate.objects.filter(vacancy=vacancy,finalize=True).count())
                        stage.total_count = count0 + count1 + count2
                        if stage.total_count > 0:
                            locked_count = locked_count +1
                    counter = locked_count + 1
                    context['success'] = True
                    context['timeline'] = {}
                    # if locked_count <= len(stages):
                    #     context['msg'] = "You cannot edit an Hiring Process with candidates in it."
                    #     context['success'] = False
                    # else:
                    # vstages=[]
                    if stages:
                        context['stages'] = stages
                        for stage_id in stages:
                            if stage_id:
                                # if counter <= locked_count:
                                #     if stage_id and str(stage_id) == str(vacancy_stages.filter(order=counter)[0].stage.id):
                                #         pass
                                #     else:
                                #         context['msg'] = "You cannot edit an Hiring Process with candidates in it."
                                #         context['success'] = False
                                #         break
                                # else:
                                stage = Stage.objects.get(id=stage_id)
                                vacancystage, created = VacancyStage.objects.get_or_create(vacancy=vacancy, order = counter)
                                # if created:
                                vacancystage.stage = stage
                                vacancystage.save()
                                # vstages = vstages + [vacancystage,]
                                context['timeline'][counter] = {'label':stage.name,'count':0, 'href': reverse('vacancies_get_vacancy_stage_details', kwargs={'vacancy_id': vacancy.id,'vacancy_stage':counter})}
                                counter = counter +1;
                    if context['success']:
                        context['locked'] = locked_count
                        # for vstages in vstages:
                        #     vstage.save()
                        context['counter'] = counter
                        VS = VacancyStage.objects.filter(vacancy=vacancy,order__gte=counter).exclude(order=100)
                        context['ids'] = [vs.id for vs in VS]
                        VS.delete()
                        context['msg'] = 'Hiring Process Updated'
                        messages.success(request,"Hiring Process Updated")
                        # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = [r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)])
                        message_chunks = [
                                {
                                    'subject': str(vacancy.employment),
                                    'subject_action': '',
                                    'action_url': vacancy.get_absolute_url(),
                                }
                            ]
                        post_activity(message_chunks = message_chunks, actor = request.user,action = 'updated processes for job opening - ', subject = str(vacancy.employment), subscribers = [r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)], action_url = vacancy.get_absolute_url())
                # count=1
                # context['timeline']={}
                # context['timeline']['0'] = {'label':'Applications Received','count':vacancy[0].postulated.count() + vacancy[0].public_postulated.count(), 'href': reverse('vacancies_get_vacancy_stage_details', kwargs={ 'vacancy_id' : vacancy[0].id, 'vacancy_stage' : 0 })}
                # for stage_id in stages:
                #     if stage_id:
                #         stage = Stage.objects.get(id=stage_id)
                #         vs = VacancyStage.objects.create(stage=stage, vacancy = vacancy[0], order = count)
                #         context['timeline'][count] = {'label':stage.name,'count':vs.postulate_set.count()+vs.public_postulate_set.count(), 'href': reverse('vacancies_get_vacancy_stage_details', kwargs={'vacancy_id': vacancy[0].id,'vacancy_stage':count})}
                #         count = count +1

                # context['timeline']['100'] = {'label':'Onboarding','count':vacancy[0].finalized_count(), 'href': reverse('vacancies_get_vacancy_stage_details', kwargs={'vacancy_id': vacancy[0].id,'vacancy_stage':100})}
                # context['success'] = True
                # context['msg'] = 'Hiring Process Updated'
            else:
                context['msg'] = 'Please upgrade to avail this feature.'
    return JsonResponse(context)

@csrf_exempt
def upgrade_postulate(request):
    context={}
    formdata = json.loads(request.POST.get('formdata',''))
    context['success'] = False
    if is_ajax(request) and request.method == 'POST' and request.user.is_authenticated and formdata:
        user = request.user
        try:
            vacancy = Vacancy.objects.get(id=request.POST['vacancy'])
            recruiter = Recruiter.objects.filter(user = user, company = vacancy.company, user__is_active=True)
        except:
            vacancy = None
            recruiter = None
        success_count = 0
        failed_count = 0
        try:
            cpage = request.POST.get('cpage',False)
        except:
            cpage = False
        if recruiter:
            try:
                stage = VacancyStage.objects.get(id = request.POST.get('process'))
            except:
                stage = None
            if stage:
                stageorder = stage.order
            else:
                stageorder = 0
            try:
                nextstage = VacancyStage.objects.get(vacancy = vacancy, order = stageorder+1)
            except:
                if stageorder == 100:
                    nextstage = None
                else:
                    nextstage = VacancyStage.objects.get(vacancy = vacancy, order = 100)
            if nextstage:
                for data in formdata:
                    success = False
                    # if data['public'] == '0' or data['public'] == 0:
                    #     postulate = Postulate.objects.filter(id = data['candidate'], vacancy = vacancy)
                    # elif data['public'] == '1' or data['public'] == 1:
                    try:
                        postulate = Postulate.objects.filter(id = data['candidate'], vacancy=vacancy)
                    except:
                        postulate=None
                    if postulate:
                        postulate=postulate[0]
                        postulate.vacancy_stage = nextstage
                        if nextstage.order == 100:
                            postulate.finalize = True
                        postulate.save()
                        context['success'] = True
                        success = True
                        context['msg'] = "Successfully moved <b>" + str(postulate.candidate.full_name()) + "</b> to <b>" + str(postulate.vacancy_stage) + "</b>."
                        Comment.objects.create(postulate = postulate, comment_type=3, text='Candidate Moved to ' + str(postulate.vacancy_stage) + ' by ' + str(user.get_full_name()))
                        if cpage:
                            messages.success(request,context['msg'])
                    if success:
                        success_count = success_count + 1
                    else:
                        failed_count = failed_count + 1
                if context['success']:
                    if success_count > 0 or failed_count > 0:
                        context['msg'] = ""
                        if success_count>0:
                            context['msg'] = 'Successfully moved ' + str(success_count) + ' candidates to ' + str(nextstage) + '. '
                            context['count'] = success_count
                        if failed_count>0:
                            context['msg'] = 'Failed to move ' + str(failed_count) + ' candidates. '
                    else:
                        context['msg'] ='No Profiles moved'
            else:
                context['msg'] = 'No Process to advance to.'
            if not cpage:
                messages.success(request,context['msg'])
    return JsonResponse(context)

@csrf_exempt
def downgrade_postulate(request):
    context={}
    formdata = json.loads(request.POST.get('formdata',''))
    context['success'] = False
    if is_ajax(request) and request.method == 'POST' and request.user.is_authenticated and formdata:
        user = request.user
        try:
            vacancy = Vacancy.objects.get(id=request.POST['vacancy'])
            recruiter = Recruiter.objects.filter(user = user, company = vacancy.company, user__is_active=True)
        except:
            vacancy = None
            recruiter = None
        success_count = 0
        failed_count = 0
        if recruiter:
            try:
                stage = VacancyStage.objects.get(id = request.POST.get('process'))
            except:
                stage = None
            if stage:
                stageorder = stage.order
            else:
                stageorder = 0
            if stageorder == 100:
                prevstage = VacancyStage.objects.filter(vacancy=vacancy).exclude(order=100).order_by('order').last()
            elif stageorder == 0:
                prevstage = None
            else:
                prevstage = VacancyStage.objects.filter(vacancy = vacancy, order = stageorder-1)[0]
            if prevstage:
                try:
                    cpage = request.POST.get('cpage',False)
                except:
                    cpage = False
                for data in formdata:
                    success = False
                    # if data['public'] == '0' or data['public'] == 0:
                    #     print(data['candidate'])
                    #     postulate = Postulate.objects.filter(id = data['candidate'], vacancy = vacancy)
                    # elif data['public'] == '1' or data['public'] == 1:
                    try:
                        postulate = Postulate.objects.filter(id = data['candidate'], vacancy=vacancy)
                    except:
                        postulate=None
                    if postulate:
                        postulate = postulate[0]                            
                        postulate.vacancy_stage = prevstage
                        postulate.finalize=False
                        postulate.save()
                        context['success'] = True
                        success = True
                        context['msg'] = "Successfully moved <b>" + str(postulate.candidate.full_name()) + "</b> to <b>" + str(postulate.vacancy_stage) + "</b>."
                        Comment.objects.create(postulate = postulate, comment_type=4, text='Candidate moved back to ' + str(postulate.vacancy_stage) + ' by ' + str(user.get_full_name()))
                        if cpage:
                            messages.success(request,context['msg'])
                    if success:
                        success_count = success_count + 1
                    else:
                        failed_count = failed_count + 1
                if context['success']:
                    context['count'] = success_count
                    if success_count > 0 or failed_count > 0:
                        context['msg'] = ""
                        if success_count > 0:
                            context['msg'] = "Successfully moved " + str(success_count) + " candidates back to " + str(prevstage) + ". "
                        if failed_count > 0:
                            context['msg'] = "Failed to move " + str(failed_count) + ' candidates. '
                    else:
                        context['msg'] = 'No Profiles moved'
                    if not cpage:
                        messages.success(request, context['msg'])
    return JsonResponse(context)

@csrf_exempt
def archive_postulate(request):
    context={}
    formdata = json.loads(request.POST.get('formdata',''))
    context['success'] = False
    if is_ajax(request) and request.method == 'POST' and request.user.is_authenticated and formdata:
        user = request.user
        try:
            cpage = request.POST.get('cpage',False)
        except:
            cpage = False
        try:
            vacancy = Vacancy.objects.get(id=request.POST['vacancy'])
            recruiter = Recruiter.objects.filter(user = user, company = vacancy.company, user__is_active=True)
        except:
            vacancy = None
            recruiter = None
        success_count = 0
        failed_count = 0
        if recruiter:
            for data in formdata:
                success = False
                try:
                    postulate = Postulate.objects.filter(id = data['candidate'], vacancy=vacancy)
                except:
                    postulate=None
                if postulate:
                    postulate = postulate[0]
                    # if data['public'] == '1' or data['public'] == 1:
                    #     postulate.candidate = postulate.full_name
                    #     email = postulate.email
                    # else:
                    if postulate.candidate.user:
                        email = postulate.candidate.user.email
                    else:
                        email = postulate.candidate.public_email
                    postulate.discard = True
                    postulate.save()
                    company = postulate.vacancy.company
                    text = 'Candidate archived by ' + str(user.get_full_name())
                    if request.POST.get('ban_perm') == 'true':       
                        company.ban_list = company.ban_list + ',' + email
                        company.ban_list = company.ban_list.strip(',')
                        company.save()
                        text = text + ' permanently.'
                    elif request.POST.get('ban_temp') == 'true':
                        if postulate.vacancy.ban_all:
                            function = postulate.vacancy.function
                            text = text + ' from applying to ' + postulate.vacancy.function + ' positions'
                        else:
                            function = None
                            text = text + ' from applying to all positions'
                        text = text + ' for ' + postulate.vacancy.get_ban_period_display() + '.'
                        ban,created = Ban.objects.get_or_create(email = email, ban_function = function, company = company)
                        ban.duration = postulate.vacancy.ban_period
                        ban.save()
                    context['success'] = True
                    success = True
                    Comment.objects.create(postulate = postulate, comment_type=4, text=text)
                    context['msg'] = "Successfully archived <b>" + str(postulate.candidate) + "</b>."
                    if cpage:
                        messages.success(request,context['msg'])
                if success:
                    success_count = success_count + 1
                else:
                    failed_count = failed_count + 1
            if context['success']:
                context['cont'] = success_count
                if success_count > 0 or failed_count > 0:
                    context['msg'] = ""
                    if success_count > 0:
                        context['msg'] = "Successfully archived " + str(success_count) + " candidates. "
                    if failed_count > 0:
                        context['msg'] = 'Failed to move ' + str(failed_count) + ' candidates. '
                else:
                    context['msg'] = 'No profiles moved'
                if not cpage:
                    messages.success(request,context['msg'])
    return JsonResponse(context)

@csrf_exempt
def validate_personal_form(request):
    """Validate candidate's personal information form.

    Args:
        request: HTTP request containing form data

    Returns:
        JsonResponse: Validation results
    """
    context={}
    context['success'] = False
    context['post'] = request.POST
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_candidate = CandidateForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_candidate.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    # form_candidate
                    form_candidate.save()
                    context['msg'] = "Profile Updated"
                    # context['data'] = candidate.name
            else:
                context['errors'] = form_candidate.errors
    return JsonResponse(context)

@csrf_exempt
def validate_contact_form(request):
    """Validate candidate's contact information form.

    Args:
        request: HTTP request containing form data

    Returns:
        JsonResponse: Validation results
    """
    context={}
    context['success'] = False
    context['post'] = request.POST
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_candidate_contact = CandidateContactForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_candidate_contact.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    # form_candidate_contact
                    form_candidate_contact.save()
                    context['msg'] = "Profile Contact Updated"
                    # context['data'] = candidate.name
            else:
                context['errors'] = form_candidate_contact.errors
    return JsonResponse(context)

@csrf_exempt
def validate_academic_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                academic = Academic.objects.get(id = request.POST['id'], candidate = candidate[0])
            except:
                academic = None
            form_academic = AcademicForm(instance = academic,data = request.POST, files = request.FILES)
            if form_academic.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    academic = form_academic.save()
                    if not academic.candidate:
                        academic.candidate = candidate[0]
                        academic.save()
                    context['id'] = academic.id
                    context['msg'] = "Education Updated"
            else:
                context['errors'] = form_academic.errors
        return JsonResponse(context)

    raise Http404

@csrf_exempt
def validate_experience_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                expertise = Expertise.objects.get(id = request.POST['id'], candidate = candidate[0])
            except:
                expertise = None
            form_expertise = ExpertiseForm(instance = expertise,data = request.POST, files = request.FILES)
            if form_expertise.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    expertise = form_expertise.save()
                    if not expertise.candidate:
                        expertise.candidate = candidate[0]
                        expertise.save()
                    context['id'] = expertise.id
                    context['msg'] = "Experience Updated"
            else:
                context['errors'] = form_expertise.errors
    return JsonResponse(context)

@csrf_exempt
def validate_training_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                training = Training.objects.get(id = request.POST['id'], candidate=candidate[0])
            except:
                training = None
            form_training = TrainingForm(instance = training, data = request.POST, files = request.FILES)
            if form_training.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    training = form_training.save()
                    if not training.candidate:
                        training.candidate = candidate[0]
                        training.save()
                    context['id'] = training.id
                    context['msg'] = "Training Updated"
            else:
                context['errors'] = form_training.errors
    return JsonResponse(context)

@csrf_exempt
def validate_project_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                project = Project.objects.get(id = request.POST['id'], candidate = candidate[0])
            except:
                project = None
            form_project = ProjectForm(instance = project, data = request.POST, files = request.FILES)
            if form_project.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    project = form_project.save()
                    if not project.candidate:
                        project.candidate = candidate[0]
                        project.save()
                    context['id'] = project.id
                    context['msg'] = "Project Updated"
            else:
                context['errors'] = form_project.errors
    return JsonResponse(context)

@csrf_exempt
def validate_certificate_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                certificate = Certificate.objects.get(id = request.POST['id'], candidate = candidate[0])
            except:
                certificate = None                
            form_certificate = CertificateForm(instance = certificate,data = request.POST, files = request.FILES)
            if form_certificate.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    certificate = form_certificate.save()
                    if not certificate.candidate:
                        certificate.candidate = candidate[0]
                        certificate.save()
                    context['id'] = certificate.id
                    context['msg'] = "Certificate Updated"
            else:
                context['errors'] = form_certificate.errors
    return JsonResponse(context)

@csrf_exempt
def validate_objective_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_objective = ObjectiveForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_objective.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    form_objective.save()
                    context['msg'] = "Profile Objective Updated"
            else:
                context['errors'] = form_objective.errors
    return JsonResponse(context)

@csrf_exempt
def validate_interests_form(request):
    context={}
    context['success'] = False
    # context['p']
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_interests = InterestsForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_interests.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    # raise ValueError()
                    form_interests.save()
                    context['msg'] = "Profile Interests Updated"
            else:
                context['errors'] = form_interests.errors
    return JsonResponse(context)

@csrf_exempt
def validate_hobbies_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_hobbies = HobbiesForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_hobbies.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    form_hobbies.save()
                    context['msg'] = "Profile Hobbies Updated"
            else:
                context['errors'] = form_hobbies.errors
    return JsonResponse(context)

@csrf_exempt
def validate_extra_curriculars_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_extra_curriculars = ExtraCurricularsForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_extra_curriculars.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    # raise ValueError()
                    form_extra_curriculars.save()
                    context['msg'] = "Profile Extra Curriculars Updated"
            else:
                context['errors'] = form_extra_curriculars.errors
    return JsonResponse(context)

@csrf_exempt
def validate_others_form(request):
    context={}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            form_others = OthersForm(instance = candidate[0], data = request.POST, files = request.FILES)
            if form_others.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == "false":
                    form_others.save()
                    context['msg'] = "Profile Others Updated"
            else:
                context['errors'] = form_others.errors
    return JsonResponse(context)

@csrf_exempt
def validate_language_form(request):
    context={}
    context['success'] = False
    context['post'] = request.POST
    if is_ajax(request) and request.method == 'POST':
        if request.user.is_anonymous() and request.session.get('active_applicant'):
            try:
                candidate = [SocialAuth.objects.get(id=int(request.session['active_applicant'])).user.candidate]
            except:
                candidate = None
        else:
            candidate = Candidate.objects.filter(user=request.user)
        if not candidate:
            context['msg'] = 'A valid candidate profile was not found'
            return JsonResponse(context)
        else:
            try:
                language = CV_Language.objects.get(id = request.POST['id'], candidate = candidate[0])
                context['language'] = language.id
            except:
                language = None
            form_language = CvLanguageForm(instance = language, data = request.POST, files = request.FILES)
            if form_language.is_valid():
                context['success'] = True
                context['msg'] = 'Valid'
                if request.POST['isPublic'] == 'false':
                    language = form_language.save()
                    if not language.candidate:
                        language.candidate = candidate[0]
                        language.save()
                    context['id'] = language.id
                    context['msg'] = "Language Updated"
            else:
                context['errors'] = form_language.errors
    return JsonResponse(context)

@csrf_exempt
def delete_section(request):
    context = {}
    context['success'] = False
    context['post'] = request.POST
    if is_ajax(request) and request.method == 'POST':
        try:
            section = request.POST['type']
            id = request.POST['id']
            if not section and not id:
                raise ValueError()
            if section == 'experience':
                expertise = Expertise.objects.get(id=id, candidate__user=request.user)
                expertise.delete()
                context['success'] = True
                context['msg'] = 'Experience Removed'
            elif section == 'academic':
                education = Academic.objects.get(id=id, candidate__user=request.user)
                education.delete()
                context['success'] = True
                context['msg'] = 'Education Removed'
            elif section == 'training':
                training = Training.objects.get(id=id, candidate__user=request.user)
                training.delete()
                context['success'] = True
                context['msg'] = 'Training Removed'
            elif section == 'certificate':
                certificate = Certificate.objects.get(id=id, candidate__user=request.user)
                certificate.delete()
                context['success'] = True
                context['msg'] = 'Certificate Removed'
            elif section == 'project':
                project = Project.objects.get(id=id, candidate__user=request.user)
                project.delete()
                context['success'] = True
                context['msg'] = 'Project Removed'
            elif section == 'language':
                language = CV_Language.objects.get(id=id, candidate__user=request.user)
                language.delete()
                context['success'] = True
                context['msg'] = 'Language Removed'
            else:
                raise ValueError()
        except:
            context['msg'] = 'Could not find the section you were trying to remove.'
        return JsonResponse(context)
    raise Http404

@csrf_exempt
def generate_public_cv(request):
    context={}
    # raise ValueError()
    context['errors'] = {}
    context['success'] = False
    context['post'] = json.loads(request.POST['experiences'])
    # return JsonResponse(context)
    if is_ajax(request) and request.method == 'POST':
        # try:
        # if not validate_email(request.POST['email']):
        #     context['errors'] = 'email'
        #     return JsonResponse(context)
        # raise ValueError(context['post'])
        # return JsonResponse(context)
        candidate_form = CandidateForm(data = json.loads(request.POST['personal']),isPublic = True)
        if not candidate_form.is_valid():
            context['errors'] = 'candidate'
            return JsonResponse(context)
        objective_form = ObjectiveForm(data = json.loads(request.POST['objective']))
        if not objective_form.is_valid():
            context['errors'] = 'objective'
            return JsonResponse(context)
        interests_form = InterestsForm(data = json.loads(request.POST['interests']))
        if not interests_form.is_valid():
            context['errors'] = 'interests'
            return JsonResponse(context)
        for experience in json.loads(request.POST['experiences']):
            experience_form = ExpertiseForm(data = experience)
            if not experience_form.is_valid():
                context['errors'] = 'experience'
                return JsonResponse(context)
        for academic in json.loads(request.POST['academics']):
            academic_form = AcademicForm(data = academic)
            if not academic_form.is_valid():
                context['errors'] = 'academic'
                return JsonResponse(context)
        for training in json.loads(request.POST['trainings']):
            training_form = TrainingForm(data = training)
            if not training_form.is_valid():
                context['errors'] = 'training'
                return JsonResponse(context)
        for certificate in json.loads(request.POST['certificates']):
            certificate_form = CertificateForm(data = certificate)
            if not certificate_form.is_valid():
                context['errors'] = 'certificate'
                return JsonResponse(context)
        for project in json.loads(request.POST['projects']):
            project_form = ProjectForm(data = project)
            if not project_form.is_valid():
                context['errors'] = 'projects'
                return JsonResponse(context)
        for language in json.loads(request.POST['languages']):
            language_form = CvLanguageForm(data = language)
            if not language_form.is_valid():
                context['errors'] = 'languages'
                return JsonResponse(context)
        candidate = candidate_form.save()
        # candidate.public_email = request.POST['email']
        candidate.save()
        objective_form = ObjectiveForm(data=json.loads(request.POST['objective']),files=request.FILES,instance=candidate)
        objective_form.save()
        interests_form = InterestsForm(data=json.loads(request.POST['interests']),files=request.FILES,instance=candidate)
        interests_form.save()
        for experience in json.loads(request.POST['experiences']):
            experience_form = ExpertiseForm(data = experience)
            Experience = experience_form.save()
            Experience.candidate = candidate
            Experience.save()
        for academic in json.loads(request.POST['academics']):
            academic_form = AcademicForm(data = academic)
            Academic = academic_form.save()
            Academic.candidate = candidate
            Academic.save()
        for training in json.loads(request.POST['trainings']):
            training_form = TrainingForm(data = training)
            Training = training_form.save()
            Training.candidate = candidate
            Training.save()
        for certificate in json.loads(request.POST['certificates']):
            certificate_form = CertificateForm(data = certificate)
            Certificate = certificate_form.save()
            Certificate.candidate = candidate
            Certificate.save()
        for project in json.loads(request.POST['projects']):
            project_form = ProjectForm(data = project)
            Project = project_form.save()
            Project.candidate = candidate
            Project.save()
        for language in json.loads(request.POST['languages']):
            language_form = CvLanguageForm(data = language)
            Language = language_form.save()
            Language.candidate = candidate
            Language.save()
        context['success'] = True
        context['url'] = reverse('candidates_resume_builder_templates', kwargs={'candidate_id':candidate.id})
        # context['url'] = reverse('vacancies_curriculum_to_pdf', kwargs={'candidate_id':candidate.id})
        # except:
        #     pass
    return JsonResponse(context)
    # raise Http404

@csrf_exempt
def public_application(request):
    context = {}
    # raise ValueError()
    if request.method == 'POST':
        form = Public_FilesForm(data=request.POST,files=request.FILES)
        # raise ValueError()
        if not form.is_valid():
            context['errors'] = form.errors
        else:
            context['success'] = True
    return JsonResponse(context)

@csrf_exempt
def public_contact_form(request):
    context={}
    context['success'] = False
    form = ContactForm(data=request.POST, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            context['success'] = True
            context['msg'] = "Thanks for reaching out to us. We'll get back to you wthin 24hours"
        else:
            context['errors'] = form.errors
    return JsonResponse(context)

@csrf_exempt
def update_permissions(request):
    """Update user permissions for a company or job.

    Args:
        request: HTTP request containing permission updates

    Returns:
        HttpResponse: Success or error message
    """
    context={}
    context['success'] = False
    if request.method == 'POST':
        id = request.POST.get('id',None)
        perm = request.POST.get('perm', 1)
        member = Recruiter.objects.filter(id=id, user__is_active=True)
        if member:
            member = member[0]
            if not member.is_owner():
                member.membership = int(perm)
                member.save()
                context['msg'] = "Permissions Updated"
                context['success'] = True
                if member.is_admin():
                    context['roles'] = 'Admin'
                else:
                    context['roles'] = str(member.roles())
                # vacancy = vacancy_stage.vacancy
                subscribers = list(set([member.user]))

                message_chunks = [
                        {
                            'subject': str(context['roles']),
                            'subject_action': '',
                            'action_url': reverse('companies_company_team_space'),
                        }
                    ]
                post_org_notification(message_chunks = message_chunks, actor=request.user,action = 'changed your permission level to ', subject = str(context['roles']), url=reverse('companies_company_team_space'), user = subscribers)
            else:
                context['msg'] = 'Permissions for this member cannot be updated'
        else:
            data['msg'] = "Member was not found"
    return JsonResponse(context)

@csrf_exempt
def remove_member(request):
    context={}
    context['success']=False
    if request.method=='POST':
        id = request.POST.get('id',None)
        member = Recruiter.objects.filter(id=id, user__is_active=True)
        if member:
            member=member[0]
            email = member.user.email
            password = member.user.password
            member.user.email = None
            member.user.is_active = False
            member.user.set_unusable_password()
            context_email = {
                'member': member,
                'href_url': 'https://' + ROOT_DOMAIN + '.com'
            }
            subject_template_name = 'mails/member_removed_subject.html'
            email_template_name = 'mails/member_removed.html'
            send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=email)
            member.user.save()
            context['success'] = True
            context['msg'] = 'Member Removed'
        else:
            context['msg'] = 'Member was not found'
    return JsonResponse(context)

@csrf_exempt
def change_ownership(request):
    context={}
    context['success']=False
    if request.method=='POST':
        id = request.POST.get('id',None)
        member = Recruiter.objects.filter(id=id, user__is_active=True)
        company = Company.objects.filter(user = request.user)
        if member and company:
            member=member[0]
            company = company[0]
            company.user = member.user
            company.save()
            member.team_management = True
            member.site_management = True
            member.job_management = True
            member.application_process_management = True
            member.save()
            context['msg'] = 'Ownership transfered to <b>' + member.user.first_name + ' ' + member.user.last_name + '</b>'
            messages.success(request, context['msg'])
            context['success'] = True
            context['data'] = None
        else:
            context['msg'] = 'Member was not found'
    return JsonResponse(context)

@csrf_exempt
def add_member_to_job(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        member = Recruiter.objects.get(id = request.POST.get('id',0))
        vacancy = Vacancy.objects.get(id = request.POST.get('vid',0))
        recruiter = Recruiter.objects.get(user=request.user)
        if recruiter and recruiter.is_manager():
            vacancy.recruiters.add(member)
            # for stage in vacancy.vacancystage_set.all():
            #     stage.recruiters.add(member)
            #     stage.save()
            vacancy.save()
            context['id'] = member.id
            context['img'] = str(member.user.photo)
            context['name'] = member.user.get_full_name()
            context['email'] = member.user.email
            context['msg'] = 'The member has been added.'
            context['success'] = True
            subscribers = list(set([r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)] + [member.user]))
            # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    },
                    {
                        'subject': member.user,
                        'subject_action': ' to job opening - ',
                        'action_url': '',
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user,action = 'added ', target = member.user, target_action = ' to recruitment team for job opening -  ', subject = str(vacancy.employment), subscribers = subscribers, action_url = vacancy.get_absolute_url())
        else:
            context['msg'] = 'You are not authorised to make these changes. Please contact your Admin to become Hiring Process Manager.'
    return JsonResponse(context)

@csrf_exempt
def remove_member_from_job(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        member = Recruiter.objects.get(id=request.POST.get('id',0))
        vacancy = Vacancy.objects.get(id = request.POST.get('vid',0))
        recruiter = Recruiter.objects.get(user=request.user)
        if recruiter and recruiter.is_manager():
            vacancy.recruiters.remove(member)
            for stage in vacancy.vacancystage_set.all():
                stage.recruiters.remove(member)
                stage.save()
            vacancy.save()
            context['id'] = member.id
            context['img'] = str(member.user.photo)
            context['name'] = member.user.get_full_name()
            context['email'] = member.user.email
            context['msg'] = 'The member has been removed and released of any duties as an evaluator in this job.'
            context['success'] = True
            subscribers = list(set([r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)] + [member.user]))
            # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    },
                    {
                        'subject': member.user,
                        'subject_action': ' from job opening - ',
                        'action_url': '',
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user,action = 'removed ', target = member.user, target_action = ' from recruitment team for job opening -  ', subject = str(vacancy.employment), subscribers = subscribers, action_url = vacancy.get_absolute_url())
        else:
            context['msg'] = 'You are not authorised to make these changes. Please contact your Admin to become Hiring Process Manager.'
    return JsonResponse(context)

@csrf_exempt
def add_member_to_job_process(request):
    context={}
    context['success'] = False
    if request.method=='POST':
        member = Recruiter.objects.get(id = request.POST.get('id',0))
        vacancy_stage = VacancyStage.objects.get(id = request.POST.get('vid',0))
        recruiter = Recruiter.objects.get(user = request.user)
        if recruiter and recruiter.is_manager():
            vacancy_stage.recruiters.add(member)
            vacancy_stage.save()
            vacancy = vacancy_stage.vacancy
            vacancy.recruiters.add(member)
            vacancy.save()
            context['id'] = member.id
            context['img'] = str(member.user.photo)
            context['name'] = member.user.get_full_name()
            context['email'] = member.user.email
            context['msg'] = 'The member has been added.'
            context['success'] = True
            vacancy = vacancy_stage.vacancy
            subscribers = list(set([r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)] + [r.user for r in vacancy_stage.recruiters.all()]))
            # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    },
                    {
                        'subject': str(vacancy_stage.stage),
                        'subject_action': 'for job opening - ',
                        'action_url': vacancy_stage.get_absolute_url(),
                    },
                    {
                        'subject': member.user,
                        'subject_action': ', as evaluator in process - ',
                        'action_url': '',
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user,action = 'added ', target=member.user, target_action = ', as evaluator in process - ', subject = str(vacancy_stage.stage) + ', for job opening - ' + str(vacancy.employment), subscribers = subscribers, action_url = vacancy.get_absolute_url())
        else:
            context['msg'] = 'You are not authorised to make these changes. Please contact your Admin to become Hiring Process Manager.'
    return JsonResponse(context)

@csrf_exempt
def remove_member_from_job_process(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        member = Recruiter.objects.get(id=request.POST.get('id',0))
        vacancy_stage = VacancyStage.objects.get(id = request.POST.get('vid',0))
        recruiter = Recruiter.objects.get(user=request.user)
        if recruiter and recruiter.is_manager():
            vacancy_stage.recruiters.remove(member)
            vacancy_stage.save()
            context['id'] = member.id
            context['img'] = str(member.user.photo)
            context['name'] = member.user.get_full_name()
            context['email'] = member.user.email
            context['msg'] = 'The member has been removed and released of his duties as an evaluator in this job process.'
            context['success'] = True
            vacancy = vacancy_stage.vacancy
            subscribers = list(set([r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)] + [member.user]))
            # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    },
                    {
                        'subject': str(vacancy_stage.stage),
                        'subject_action': 'for job opening - ',
                        'action_url': vacancy_stage.get_absolute_url(),
                    },
                    {
                        'subject': member.user,
                        'subject_action': ', as evaluator in process - ',
                        'action_url': '',
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user,action = 'removed ', target = member.user, target_action = ' from evaluation of ', subject = str(vacancy_stage.stage) + ', for job opening -  ' + str(vacancy.employment),  subscribers = subscribers, action_url = vacancy.get_absolute_url())
        else:
            context['msg'] = 'You are not authorised to make these changes. Please contact your Admin to become Hiring Process Manager.'
    return JsonResponse(context)

@csrf_exempt
def update_criteria(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        vacancy_stage = VacancyStage.objects.get(id=request.POST.get('vid',0))
        recruiter = Recruiter.objects.get(user = request.user)
        if recruiter and recruiter.is_manager():
            vacancy_stage.criteria = request.POST.get('criteria')
            vacancy_stage.save()
            messages.success(request,'Criteria for the process rating has been updated');
            context['success'] = True
            vacancy = vacancy_stage.vacancy
            subscribers = list(set([r.user for r in vacancy.company.recruiter_set.filter(membership__gte=2)] + [r.user for r in vacancy_stage.recruiters.all()]))
            # post_org_notification(actor=request.user,msg = n_message, url=vacancy.get_absolute_url(), user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    },
                    {
                        'subject': str(vacancy_stage),
                        'subject_action': ', for job opening - ',
                        'action_url': vacancy_stage.get_absolute_url(),
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user,action = 'updated criteria in process - ', subject = str(vacancy_stage) + ', for job opening - ' + str(vacancy.employment), subscribers = subscribers, action_url = vacancy.get_absolute_url())
        else:
            context['msg'] = 'You are not authorised to make these changes. Please contact your Admin to become Hiring Process Manager.'
    return JsonResponse(context)

@csrf_exempt
def comment(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        recruiter = Recruiter.objects.get(user = request.user)
        c_type = request.POST.get('type',0)
        if c_type == '0' or c_type == 0:
            comment = Comment.objects.create(text = request.POST.get('text'), comment_type = 1, recruiter = recruiter)
            activity = Activity.objects.get(id = request.POST.get('activity'))
            activity.subscribers.add(recruiter.user)
            activity.comments.add(comment)
            activity.save()
            if activity.message:
                post = 'post'
            else:
                post = 'activity'
            message_chunks = [
                    {
                        'subject': post,
                        'subject_action': '',
                        'action_url': activity.get_absolute_url(),
                    }
                ]

            post_org_notification(message_chunks = message_chunks, actor = request.user, action = "commented on ",target = activity.actor, subject = post, user = activity.subscribers.all().exclude(id = request.user.id), url = activity.get_absolute_url())
            context['html'] = """<div class="row bg-white no-margin border-bottom border-light pl20 pr20 comment">
                <div class="col-xs-12 pt5 pb5 text-light"><img src=\""""+recruiter.user.photo.url+"""\" class="navbar-img va-top no-margin-top card-left" data-name=\""""+recruiter.user.get_full_name()+"""\">
                    <div class="ml20 row"><h5 class="inline-block no-margin-y">"""+recruiter.user.get_full_name()+"""</h5> - <span class="text-light">"""+naturaltime(comment.logtime)+"""</span>
                    <br><small class="text-muted comment-text"><p>"""+comment.text.replace('\n','<br>')+"""</p></small></div></div></div>"""
        else:
            isPublic = int(request.POST.get('ispublic'),0)
            candidate = Postulate.objects.filter(id = request.POST.get('candidate',0))
            if candidate:
                candidate = candidate[0]
            else:
                context['msg'] = 'Candidate was not found'
                return JsonResponse(context)
            vacancy = Vacancy.objects.filter(id= request.POST.get('vacancy',0))
            if vacancy:
                vacancy = vacancy[0]
            else:
                context['msg'] = 'Job was not found'
                return JsonResponse(context)
            stage = int(request.POST.get('stage',0))
            stage = VacancyStage.objects.filter(vacancy=vacancy, order = stage)
            if stage:
                stage = stage[0]
            else:
                context['msg'] = 'Process was not found'
                # context['stage'] = stag
                return JsonResponse(context)
            stage_section = 0
            if candidate.vacancy_stage.order > stage.order:
                stage_section = 1
            elif candidate.vacancy_stage.order == stage.order:
                if candidate.discard == True:
                    stage_section = 2
                else :
                    stage_section = 0
            comment = Comment.objects.create(text= request.POST.get('text'), comment_type=int(request.POST.get('type')), recruiter=recruiter, stage = stage, stage_section = stage_section)
            # if isPublic:
            #     comment.public_postulate = candidate
            #     activity_type = 2
            #     p_id = comment.public_postulate.id
            #     target = None
            #     target_action = str(candidate.full_name) + '\'s application for job opening -  '
            # else:
            comment.postulate = candidate
            activity_type = 1
            p_id = comment.postulate.id
            target = candidate.candidate.user
            target_action = '\'s application for job opening -  '
            comment.save()
            subscribers = list(set([request.user]))
            # post_org_notification(actor=request.user,msg = n_message, user = subscribers)
            message_chunks = [
                    {
                        'subject': str(vacancy.employment),
                        'subject_action': '',
                        'action_url': vacancy.get_absolute_url(),
                    }
                ]
            post_activity(message_chunks = message_chunks, actor = request.user, action = 'commented on ', target = target, target_action = target_action, subject = str(vacancy.employment), subscribers = subscribers, activity_type = activity_type, postulate_id = p_id)
            context['html'] = """<div class="row bg-white no-margin border-bottom border-light pl20 pr20 comment"><div class="col-xs-12 pt5 pb5 text-light"><img src=\""""+recruiter.user.photo.url+"""\" class="navbar-img va-top no-margin-top card-left" data-name=\""""+recruiter.user.get_full_name()+"""\"><div class="ml20 row"><h5 class="inline-block no-margin-y">"""+recruiter.user.get_full_name()+"""</h5><small class="text-muted"> in <a href=\"""" + reverse('vacancies_get_vacancy_stage_details', kwargs={'vacancy_id':comment.stage.vacancy.id, 'vacancy_stage':comment.stage.order, 'stage_section':comment.stage_section}) + """\">""" + str(comment.stage_string()) + """</a> - <span class="text-light">"""+naturaltime(comment.logtime)+"""</span></small><br><small class="text-muted comment-text"><p>"""+comment.text.replace('\n','<br>')+"""</p></small></div></div></div>"""
        context['success'] = True
        context['msg'] = 'Comment Posted'
        # context['html'] = """<div class="row bg-white no-margin border-bottom border-light pl20 pr20 comment"><div class="col-xs-12 pt5 pb5 text-light"><img src=\""""+recruiter.user.photo.url+"""\" class="navbar-img va-top no-margin-top card-left" data-name=\""""+recruiter.user.get_full_name()+"""\"><div class="ml20 row"><h5 class="inline-block no-margin-y">"""+recruiter.user.get_full_name()+"""</h5><small class="text-muted"> in <a href=\"""" + reverse('vacancies_get_vacancy_stage_details', kwargs={'vacancy_id':comment.stage.vacancy.id, 'vacancy_stage':comment.stage.order, 'stage_section':comment.stage_section}) + """\">""" + str(comment.stage_string()) + """</a> - <span class="text-light">"""+naturaltime(comment.logtime)+"""</span></small><br><small class="text-muted comment-text"><p>"""+comment.text.replace('\n','<br>')+"""</p></small></div></div></div>"""
    return JsonResponse(context)

@csrf_exempt
def retreive_comments(request):
    pass

@csrf_exempt
def rate(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        recruiter = Recruiter.objects.get(user = request.user)
        isPublic = int(request.POST.get('ispublic'))
        candidate = Postulate.objects.filter(id = request.POST.get('candidate',0))
        if candidate:
            candidate = candidate[0]
        else:
            context['msg'] = 'Candidate was not found'
            return JsonResponse(context)
        vacancy = Vacancy.objects.filter(id= request.POST.get('vacancy',0))
        if vacancy:
            vacancy = vacancy[0]
        else:
            context['msg'] = 'Vacancy was not found'
            return JsonResponse(context)
        stage = int(request.POST.get('stage',0))
        stage = VacancyStage.objects.filter(vacancy=vacancy, order = stage)
        if stage:
            stage = stage[0]
        else:
            context['msg'] = 'Process was not found'
            return JsonResponse(context)
        text = request.POST.get('text')
        ratings_dump = request.POST.getlist('ratings[]')
        ratings = []
        for rating in ratings_dump:
            name,value = rating.split(' -&&- ')
            ratings+=[(name,value),]
        if stage.criteria:
            clist = stage.criteria_as_list()
            for rating in ratings:
                if rating[0] in clist:
                    if rating[1] == 0:
                        break
                    clist.remove(rating[0])
                else:
                    break
            if clist:
                context['msg'] = 'Please provide complete ratings to proceed'
                return JsonResponse(context)    
        comment = Comment.objects.create(text= request.POST.get('text'), comment_type=int(request.POST.get('type')), recruiter=recruiter, stage = stage)
        comment.postulate = candidate
        application,created = Postulate_Stage.objects.get_or_create(vacancy_stage=stage,postulate=candidate)
        old_scores = application.scores.all().filter(recruiter=recruiter)
        if old_scores:
            comment = old_scores[0].get_comment()
            comment.delete()
            for score in old_scores:
                score.delete()
        for rating in ratings:
            score = Postulate_Score.objects.create(name=rating[0],score=rating[1], recruiter = recruiter)
            score.save()
            application.scores.add(score)
            application.save()
        comment.save()
        messages.success(request,'Rating Posted')
        tags_dump = request.POST.getlist('tags[]')
        candidate.tags.clear()
        for tag in tags_dump:
            if not tag.startswith('__'):
                tagobject = VacancyTags.objects.get(id=int(tag), vacancy = candidate.vacancy)
            else:
                tagobject, created = VacancyTags.objects.get_or_create(name=tag.strip('_'), vacancy = candidate.vacancy)
            candidate.tags.add(tagobject)
        context['success'] = True
        messages.success(request, 'Tags Updated')
    return JsonResponse(context)

@csrf_exempt
def retreive_ratings(request):
    pass

@csrf_exempt
def tag(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        recruiter = Recruiter.objects.get(user = request.user)
        candidate = Postulate.objects.filter(id = request.POST.get('candidate',0))
        if candidate:
            candidate = candidate[0]
        else:
            context['msg'] = 'Candidate was not found'
            return JsonResponse(context)
        tags_dump = request.POST.getlist('tags[]')
        candidate.tags.clear()
        for tag in tags_dump:
            if not tag.startswith('__'):
                tagobject = VacancyTags.objects.get(id=int(tag), vacancy = candidate.vacancy)
            else:
                tagobject, created = VacancyTags.objects.get_or_create(name=tag.strip('_'), vacancy = candidate.vacancy)
            candidate.tags.add(tagobject)
        context['success'] = True
        context['msg'] = 'Tags Updated'
        activity_type = 1
        p_id = candidate.id
        target = candidate.candidate.user
        target_action = '\'s application for job opening -  '
        subscribers = list(set([request.user]))
        message_chunks = [
                {
                    'subject': ', '.join([str(tag) for tag in candidate.tags.all() ]),
                    'subject_action': '',
                    'action_url': '',
                },
                {
                    'subject': str(candidate.vacancy.employment),
                    'subject_action': ' as ',
                    'action_url': candidate.vacancy.get_absolute_url(),
                }
            ]
        post_activity(
                message_chunks = message_chunks, 
                actor = request.user, 
                action = 'tagged ', 
                target = target, 
                target_action = target_action, 
                subject = str(candidate.vacancy.employment), 
                subscribers = subscribers, 
                activity_type = activity_type, 
                postulate_id = p_id
            )
        messages.success(request, context['msg'])
        context['tagcount'] = candidate.tags.count()

    return JsonResponse(context)

@csrf_exempt
def withdraw(request):
    context={}
    context['success'] = False
    if request.user.is_authenticated and request.method=='POST':
        try:
            postulate = Postulate.objects.get(id = request.POST.get('id'), candidate__user=request.user)
            if postulate.vacancy_stage.order != 100:
                postulate.discard = True
                postulate.withdraw = True
                postulate.save()
                context['success'] = True
                text = "Application withdrawn by candidate and archived."
                Comment.objects.create(postulate = postulate, comment_type=4, text=text)
                messages.success(request,'Application Withdrawn')
            else:
                messages.error(request, 'You are already in Onboarding. You cannot withdraw application.')
        except:
            context['msg'] = 'No existing/active application found'
    return JsonResponse(context)

@csrf_exempt
def pricing_request(request):
    context ={}
    context['success'] = False
    if request.method == 'POST' and request.POST.get('phone'):
        msg = 'Phone: ' + request.POST.get('phone') + '\nName: ' + request.user.get_full_name() + '\nEmail: ' + request.user.email + '\nCompany: ' + str(request.user.recruiter.company.all()[0])
        send_email_to_TRM(subject = "Pricing Requested", body_email=msg, notify = True)
        context['success'] = True
        context['msg'] = 'We have received your inquiry and will get back to you soon.'
    return JsonResponse(context)

@csrf_exempt
def compare_candidates(request):
    context={}
    if request.method == 'POST' or request.method == 'GET':
        if request.method == 'POST':
            vacancy_stage_id = request.POST.get('vsid',0)
            Candidates = request.POST.get('cids',None)
            if Candidates:
                Candidates = Candidates.split(',')
            # Public_candidates = request.POST.get('pcids',None)
            # if Public_candidates:
            #     Public_candidates = Public_candidates.split(',')
        else:            
            vacancy_stage_id = request.GET.get('vsid',0)
            Candidates = request.GET.get('cids')
            if Candidates:
                Candidates = Candidates.split(',')
            # Public_candidates = request.GET.get('pcids')
            # if Public_candidates:
            #     Public_candidates = Public_candidates.split(',')
        context['current_process'] = None
        # context['public_candidates'] = None
        context['candidates'] = None
        subdomain_data = subdomain(request)
        # candidate processes
        if request.user.is_authenticated:
            # raise ValueError()
            try:
                recruiter = Recruiter.objects.get(user=request.user, user__is_active=True, company__subdomain__slug=subdomain_data['active_subdomain'])
            except:
                raise ValueError()
            if vacancy_stage_id:
                # try:
                vacancy_stage = VacancyStage.objects.get(id = vacancy_stage_id)
                context['current_process'] = vacancy_stage
                candidates = []
                count = 0
                if Candidates:
                    for candidate in Candidates:
                        count += 1
                        postulate = Postulate.objects.filter(id = int(candidate.strip()))
                        if postulate:
                            postulate = postulate[0]
                            postulate.processes = postulate.postulate_stage_set.all()
                            postulate.process = postulate.processes.filter(vacancy_stage = vacancy_stage)
                            postulate.checkbox_id = '-0-'+str(postulate.id)
                            candidates += [postulate]
                        else:
                            raise ValueError()
                # if Public_candidates:
                #     for candidate in Public_candidates:
                #         count += 1
                #         postulate = Public_Postulate.objects.filter(id = int(candidate.strip()))
                #         if postulate:
                #             postulate = postulate[0]
                #             postulate.processes = postulate.public_postulate_stage_set.all()
                #             postulate.process = postulate.processes.filter(vacancy_stage = vacancy_stage)
                #             postulate.checkbox_id = '-1-'+str(postulate.id)
                #             candidates += [postulate]
                #         else:
                #             raise ValueError()
                context['candidates'] = candidates
                context['count'] = count
                user = request.user
                # except:
                #     raise ValueError()
                
            else:
                raise ValueError()
    else:
        raise ValueError()
    return render(request, 'compare_candidates.html', context)
   
@csrf_exempt
def filter_candidates(request):
    context = {}
    context['success'] = False
    context['msg'] = ''
    # raise ValueError()
    if request.method == 'POST':
        filters = request.POST.get('filter','')
        try:
            filters = filters.split(',')
        except:
            pass
        if filters[0].strip() == "":
            filters = None
        try:
            process_id = int(request.POST.get('process',0))
            process = VacancyStage.objects.get(id = process_id)
        except:
            process = None
        if process:
            # raise ValueError(filters)
            section = request.POST.get('section', 0)
            # raise ValueError(section)
            if section == '2' or section == 2:
                postulates = process.postulate_stage_set.all().filter(postulate__discard = True)
                # public_postulates = process.public_postulate_stage_set.all().filter(postulate__discard = True)
            elif section == '1' or section == 1:
                postulates = Postulate_Stage.objects.filter(vacancy_stage__id__gte= process.id)
                # public_postulates = Public_Postulate_Stage.objects.filter(process__id__gte=process.id)
            else:
                postulates = process.postulate_stage_set.all().filter(postulate__discard = False)
                # public_postulates = process.public_postulate_stage_set.all().filter(postulate__discard = False)
            # raise ValueError([p.id for p in postulates] + [p.id for p in public_postulates])
            filter5 = []
            filter3 = []
            filter2 = []
            filter1 = []
            filter0 = []
            # raise ValueError(postulates)
            min = None
            max = None
            text = ""
            pids = []
            # raise ValueError()
            if filters:
                for filter in filters:

                    # raise ValueError(filters)
                    splitArray = filter.split('-')
                    type = splitArray[0]
                    splitArray[0] = ""
                    if len(splitArray)<2:
                        # contex
                        return JsonResponse(context)
                    else:
                        splitArray[1] = '-'.join(splitArray).strip('-')
                        # raise ValueError(splitArray[1])
                        if type == '5':
                            val = int(splitArray[1])
                            filter5 = filter5 + [val]
                        elif type == '3':
                            val = int(splitArray[1])
                            filter3 = filter3 + [val]
                            # except:
                                # context['msg'] = 'no recruiter in type 3 for ' + splitArray[1]
                                # return JsonResponse(context)
                        elif type == '2':
                            # try:
                            # raise ValueError(splitArray[1])
                            val = int(splitArray[1])
                            filter2 = filter2 +[val]
                            # except:
                            #     context['msg'] = 'no recruiter in type 2'
                            #     return JsonResponse(context)
                        elif type == '1':
                            arr = splitArray[1].split('-')
                            arr[0] = ""
                            filter1 = filter1 + [arr]
                        elif type == '0':
                            filter0 = filter0 + [str(splitArray[1])]
            if filter5:
                tags = VacancyTags.objects.filter(id__in = filter5, vacancy = process.vacancy)
                for tag in tags:
                    ids = [p.id for p in tag.postulate_set.all()]
                    pids = pids + [p.id for p in postulates.filter(postulate__id__in=ids)]
            if filter3:
                # for postulate in postulates:
                pids = pids + [pp.id for pp in postulates.filter(postulate__recruiter__id__in = filter3)]
                context['msg'] = pids
            if filter2:
                ids=[]
                for postulate in postulates:
                    if postulate.postulate.comment_set.all().filter(recruiter__id__in = filter2):
                        ids = ids + [postulate.id]
                pids = pids + ids
                # postulates = postulates.exclude(id__in = ids)
                ids = []
                # for postulate in public_postulates:
                #     if postulate.postulate.comment_set.all().filter(recruiter__id__in = filter2):
                #         ids = ids + [postulate.id]
                # public_postulates = public_postulates.exclude(id__in = ids)
            if filter0:
                postulate_ids = filter_text_from_profile(filter0,[p.id for p in postulates],False)
                # public_postulate_ids = filter_text_from_profile(filter0, [p.id for p in public_postulates],True)
                # postulates = postulates.filter(id__in=postulate_ids)
                pids = pids + postulate_ids
                postulate_ids = []
                
                # public_postulates = public_postulates.filter(id__in=public_postulate_ids)
                # ppids = ppids + public_postulate_ids
            if filter1:
                ids = []
                for f in filter1:
                    min = int(f[1])
                    max = int(f[2]) 
                    if min >= 0 and max >= 0:
                        for postulate in postulates:
                            if postulate.avg_score() >= min and postulate.avg_score() <= max:
                                ids = ids + [postulate.id]           
                # postulates = postulates.filter(id__in=ids)
                pids = pids + ids
                ids = []
                # for f in filter1:
                #     min = int(f[1])
                #     max = int(f[2])
                #     if min>=0 and max >= 0:
                        # for postulate in public_postulates:
                        #     if postulate.avg_score() >= min and postulate.avg_score() <= max:
                        #         ids = ids + [postulate.id] 
                # public_postulates = public_postulates.filter(id__in=ids)
                # ppids = ppids + ids
            candidates = []
            # raise ValueError()
            if filters:
                if postulates:
                    postulates = postulates.filter(id__in = pids)
                # if public_postulates:
                #     public_postulates = public_postulates.filter(id__in = ppids)
            # context['msg'] = filter3
            for postulate in postulates:
                candidates = candidates + [{'public':0,'candidate':postulate.postulate.id}]
            # for postulate in public_postulates:
            #     candidates = candidates + [{'public':1,'candidate':postulate.postulate.id}]
            context['candidates'] = candidates
            context['success'] = True
            # raise ValueError()
        else:
            context['msg'] = 'No process to apply filter'
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)

def notifications(request):
    response = HttpResponse("", content_type="text/event-stream")
    if request.user.is_authenticated:
        msg = ""
        if not 'last_notification' in request.session:
            last_notification = 0
        else:
            last_notification = int(request.session['last_notification'])
        new_notifications = Notification.objects.filter(id__gt=last_notification, user = request.user)
        try:
            last_shown = Notification.objects.filter(user = request.user).latest('id').id
        except:
            last_shown = 0
        notifications = []
        for notification in new_notifications:
            html = """<li class="border-bottom border-light unseen" data-notification='"""+ str(notification.id) +"""'>
                <p class="pt10 pb10 pr10 has-img text-muted">"""
            if notification.actor:
                html = html + """<img src='"""+notification.actor.photo.url+"""' class="img-card ml10 mr10 card-left" data-name='"""+str(notification.actor.get_full_name())+"""'><b>"""
                if notification.actor == request.user:
                    html = html + """You """
                else:
                    html = html + str(notification.actor) + ' '
                html = html + '</b>'
            if notification.action:
                html = html + str(notification.action) + ' '
            if notification.target:
                html = html +'<b>'
                if notification.target == request.user:
                    if notification.target_action:
                        html = html + "you "
                    else:
                        html =html + "your "
                else:
                    if notification.actor == notification.target:
                        html = html + "their "
                    else:
                        html = html + str(notification.target)
                        if not notification.target_action:
                            html = html + "'s "
                        else:
                            html = html + " "
                html = html + "</b>"
            if notification.target_action:
                html = html + str(notification.target_action) + ' '
            if notification.subject:
                html = html + "<a "
                if notification.action_url:
                    html = html + "href='" + str(notification.action_url) + "'"
                html = html + " target = '_blank'>" + str(notification.subject) + '</a> '
                if notification.subject_action:
                    html = html + str(notification.subject_action)
            if notification.message:
                html = html + '<br>' + str(notification.message)
            html = html + '<br><i><small>' + naturaltime(notification.timestamp) + '</small></i></p></li>'
            data = {
                'id': str(notification.id),
                'actor': str(notification.actor).strip(),
                'message': str(notification.message).strip(),
                'action_url': str(notification.action_url).strip(),
                'last_updated': str(notification.timestamp).strip(),
                'html': html
                }
            notifications.append(data)
        msg = msg + 'data: '+ json.dumps(notifications) + ' \n'
        msg = msg + '\n'
        if last_shown > request.session['last_notification']:
            request.session['last_notification'] = last_shown
        response.write(msg)
    else:
        response.write('Unauthorised access')
    return response

@csrf_exempt
def post_message_to_stream(request):
    """Post a message to the activity stream.

    Args:
        request: HTTP request containing message data

    Returns:
        JsonResponse: Post status
    """
    context = {}
    context['success'] = False
    if request.method == 'POST':
        data = request.POST.get('message','')
        if data:
            subscribers = request.user.recruiter.company.all()[0].recruiter_set.all()
            activity = Activity.objects.create(actor = request.user, message = data)
            for subscriber in subscribers:
                activity.subscribers.add(subscriber.user)
            context['success'] = True
            context['msg'] = 'Posted Successfully'
            context['post_html'] = """ <div class="comment-card mb10 activity-comment" data-activity=\"""" + str(activity.id) + """\">
                                            <div class="bg-white border-bottom border-light pl10 pr10 pb10 pt10 mh60">
                                                <div class="ml40"> 
                                                    <img class="navbar-img navbar-img-hg card-left ml20 mt3 pl5" src='""" +activity.actor.photo.url+"""' data-name='"""+str(activity.actor)+"""'>
                                                    <a class="text-muted mb10" href="">
                                                        <b>You</b> <i></i>
                                                    </a>
                                                    <span class="pull-right"><i>"""+ str(naturaltime(activity.timestamp)) +"""</i></span>
                                                    <p class="no-margin">"""+str(activity.message)+"""</p>
                                                </div>
                                            </div>
                                            <div class="row bg-white border-bottom border-light no-margin pl20">
                                                <a class="btn btn-xs spot_activity no-padding"><span class="spot_label"><i class="fa fa-circle-thin text-light spot"></i> Spot </span> <small class="badge badge-light ml5 spot-count hidden">0</small></a>
                                                <span class="text-light spot_list"></span>
                                                <a class="btn btn-xs show-comments ml5"><i class="glyphicon glyphicon-comment"></i> Comment <small class="badge badge-light ml2 comment-count">"""+str(activity.comments.count())+"""</small></a>
                                            </div>
                                            <div class="collapse fade comment-cards" id="comment-a-"""+str(activity.id)+"""\">
                                                <div class="row text-center bg-white no-margin pl20 pr20 comment collapse fade in">
                                                </div>
                                                <form class="row bg-white no-margin bordered border- pt5 pl5 pr5 pb5 comment-section">
                                                    <div class="col-xs-12 pt5 pb5">
                                                        <textarea class="form-control autosize" required></textarea>
                                                        <a class="clickable mt5 hide-all" data-toggle="collapse" data-target="#comment-a-"""+str(activity.id)+"""\">Hide Comments</a>
                                                        <button class="btn btn-sm pull-right mt5 btn-info">Comment</button> 
                                                    </div>
                                                </form>
                                            </div>
                                        </div>"""
            message_chunks = [
                    {
                        'subject': 'post',
                        'subject_action': '',
                        'action_url': activity.get_absolute_url(),
                    }
                ]
            post_org_notification(message_chunks = message_chunks, user = "all", actor = activity.actor, action = "made a new ", subject = "post", url = activity.get_absolute_url())
        else:
            context['msg'] = "No data found to be posted"
    return JsonResponse(context)

@csrf_exempt
def mark_as_read(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        notification_id = request.POST.get('n_id',0)
        notification = Notification.objects.get(id = notification_id)
        notification.seen = True;
        notification.save()
        context['success'] = True
    return JsonResponse(context)

@csrf_exempt
def set_plan(request):
    context = {}
    context['success'] = False
    if is_ajax(request) and request.method == 'POST':
        plan = request.POST['plan']
        slab = PriceSlab.objects.get(id = plan)
        company = request.user.recruiter.company.all()[0]
        current_slab = company.subscription.price_slab
        user_count = company.recruiter_set.all().count()
        max_users = slab.package.max_users
        context['compulsary_remove'] = False
        context['remove_users'] = False
        if not max_users == 0 and user_count > max_users:
            if company.subscription.expired():
                context['compulsary_remove'] = True
            context['remove_users'] = True  
        if slab.amount and current_slab.amount and slab.amount > current_slab.amount:
            period = current_slab.expiry_period
            days_left = (company.subscripton.expiry - datetime.now()).days
            price_diff = slab.amount - current_slab.amount
            balance = (days_left/period)*price_diff
        else:
            balance = 0
        context['next_cycle'] = str(slab.currency.symbol) + str(company.subscription.bill_amount() - current_slab.amount + slab.amount)
        context['package'] = str(slab.package)
        context['price'] = str(slab.currency.symbol) + str(slab.amount)
        context['period'] = '/month' if slab.slab_period == 'M' else '/annum'
        context['expiry'] = str(company.subscription.expiry) 
        if balance > 0:
            context['balance'] = balance
        else:
            context['balance'] = False
        request.session['new_plan'] = slab.id
        # if slab.package.max_users == slab.package.free_users:
        #     context['free'] = True
        #     request.session['new_plan'] = ""
        # else:
            # context['free'] = False
            # request.session['new_plan'] = slab.id
            # context['slab_id'] = slab.id
            # context['package'] = str(slab.package)
            # context['period'] = str(slab.get_slab_period_display())
            # context['package_price'] = str(slab.amount)
            # context['rate'] = str(slab.price_per_user)
            # context['user_count'] = request.user.recruiter.company.all()[0].subscription.added_users
            # context['currency'] = str(slab.currency.symbol)
            # if not slab.package.max_users == 0 and slab.package.free_users == slab.package.max_users:
            #     context['no_aditional_users'] = True
            # else:
            #     context['no_additional_users'] = False
            # context['auto_proceed'] = False
            # diff = slab.package.max_users - slab.package.free_users
            # if diff < 0:
            #     diff = 0 
            # tcount = request.user.recruiter.company.all()[0].recruiter_set.all().count()
            # if tcount < slab.package.max_users and diff == 0:
            #     context['auto_proceed'] = True
        context['success'] = True
    return JsonResponse(context)

@csrf_exempt
def verify_code(request):
    context = {}
    context['success'] = False
    if request.method == 'POST':
        code = request.POST.get('code')
        slab = request.POST.get('plan')
        plan = PriceSlab.objects.get(id=int(slab))
        amount_to_pay = Decimal(request.POST.get('amount_to_pay'))
        company = request.user.recruiter.company.all()[0]
        discount_amount = 0
        #verify code exists
        # raise ValueError(validate_code(code,plan,company))
        if validate_code(code,plan,company):
            discount = Discount.objects.filter(label__iexact = code.strip())
            if not discount:
                context['msg'] = 'Invalid Code'
            else:
                discount = discount[0]
                if discount.transaction_type == 'S':
                    context['old'] = False
                    if discount.type == 'V':
                        discount_amount = discount.amount
                    elif discount.type == 'P':
                        discount_amount = amount_to_pay *(discount.amount/100)
                    context['msg'] = ''
                    amount_to_pay = discount_amount
                else:
                    context['old'] = True
                    if discount.type == 'V':
                        discount_amount = discount.amount
                    elif discount.type == 'P':
                        discount_amount = amount_to_pay *(discount.amount/100)
                    context['msg'] = 'Code Valid'
                    if discount_amount > 0:
                        discount_amount = '$' + str(round(Decimal(discount_amount),2))
                        amount_to_pay = 0
                    context['msg'] = discount_amount + ' credit will be updated post payment.'
                context['success'] = True
                context['amount'] = amount_to_pay
        else:
            context['msg'] = 'Invalid Code for current plan and company'
    return JsonResponse(context)

@csrf_exempt
def update_recurring(request):
    context = {}
    context['success'] = False
    if request.method == 'POST' and request.user.recruiter.is_admin():
        recur  = request.POST.get('recur')
        subscription = request.user.recruiter.company.all()[0].subscription
        if recur == 'true':
            subscription.auto_renew = True
        else:
            subscription.auto_renew = False
        subscription.save()
        context['success'] = True
        context['msg'] = 'Renewal Updated'
    else:
        context['msg'] = 'Could not Update. Please check your permissions'
    return JsonResponse(context)

@csrf_exempt
def renew_now(request):
    context={}
    context['success'] = False
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.profile.codename == 'recruiter' and request.user.recruiter.is_admin():
            company = request.user.recruiter.company.all()[0]
            if not company.subscription.expiry:
                context['msg'] = 'Your current Plan is not renewable.'
            else:
                renewal = company.subscription.price_slab.amount + (company.subscription.price_slab.price_per_user * company.subscription.added_users)
                if renewal > company.wallet.available:
                    context['msg'] = 'Insufficient balance to renew'
                else:
                    subscription = company.subscription
                    wallet = company.wallet
                    subscription.expiry = subscription.expiry + timedelta(days = subscription.price_slab.expiry_period)
                    subscription.save()
                    reason = str(subscription.price_slab)
                    if subscription.price_slab.get_slab_period_display():
                        reason = reason + ' ' + str(subscription.price_slab.get_slab_period_display())
                    reason = reason + ' plan'
                    if subscription.added_users:
                        reason = reason + ' with ' + str(subscription.added_users) + ' additional users'
                    reason = reason + ' renewed.'
                    wallet.available = wallet.available - renewal
                    wallet.save()
                    Transactions.objects.create(user = request.user, company = company, type="R", amount=renewal, reason = reason, balance = wallet.available)
                    messages.success(request, 'Plan renewed. Current plan will expire on ' + str(subscription.expiry.date()))
                    context['success'] = True
        else:   
            context['msg'] = 'Unauthorised Transaction'
    return JsonResponse(context)

@csrf_exempt
def spot(request):
    context = {}
    context['success'] = False
    if request.method == 'POST':
        # raise ValueError()
        activity_id = request.POST.get('activity_id')
        # try:
        activity = Activity.objects.get(id = activity_id)
        if request.user in activity.spotters.all():
            activity.spotters.remove(request.user)
            context['success'] = True
            context['type'] = '0'
            context['msg'] = 'Activity Unspotted'
            if activity.spotters.count():
                context['spot_list'] = 'Spotted by ' + str(activity.spotters.all()[0].first_name)
            else:
                context['spot_list'] = ''
            
        else:
            activity.spotters.add(request.user)
            context['success'] = True
            context['type'] = '1'
            context['msg'] = 'Activity Spotted'
            context['spot_list'] = 'by You '
        if activity.spotters.count() > 1:
                context['spot_list'] = context['spot_list'] + """and <button class="btn btn-trans-info no-padding va-base clickable"
                                 data-toggle="popover" title="Spotters" data-placement="right" data-content='"""
                for spotter in activity.spotters.all():
                    context['spot_list'] = context['spot_list'] + """<div class="bg-white pl15 pr15 pt10">
                            <img src=\"""" + spotter.photo.url + """\" class="navbar-img va-top no-margin-top card-left ml15" data-name=\"""" + spotter.get_full_name() + """\">
                            <div class="ml25 mt2 pt5 pb10 pr20 pl10 border-bottom border-light">
                                <h5 class="no-margin-y text-muted">""" + spotter.get_full_name() + """</h5>
                            </div>
                            <span class="clearfix"></span>
                        </div>"""
                context['spot_list'] = context['spot_list'] + """' data-trigger="focus"/>""" + str(activity.spotters.count()-1) + "others</button>"
        activity.save()
        # except:
        #     context['msg'] = 'Activity was not found'
    return JsonResponse(context)

@csrf_exempt
def smart_share(request,id):
    try:
        recruiter_social_profile = Recruiter.objects.get(user = request.user)
        vacancy = Vacancy.objects.get(id=id,company__in=recruiter_social_profile.company.all())
    except:
        raise Http404
    if not is_ajax(request) or not request.method == 'POST':
        raise Http404
    recruiter_social_profile.listatus = 0
    recruiter_social_profile.fbstatus = 0
    recruiter_social_profile.twstatus = 0
    from utils import posttofbprofile, posttofbgroup, posttofbpage, posttoliprofile, posttolicompany, posttotwitter
    recruiter_social = recruiter_social_profile.user.socialauth_set.all()
    from common.views import debug_token, get_fb_user_groups, get_fb_user_pages, get_li_companies
    for profile in recruiter_social.all():
        debug_data = debug_token(profile.oauth_token,profile.social_code)
        if profile.social_code == 'fb':
            recruiter_social_profile.fb = profile
            if 'data' in debug_data and 'error' not in debug_data['data']:
                recruiter_social_profile.fbstatus = 2
                if 'user_managed_groups' in debug_data['data']['scopes']:
                    recruiter_social_profile.fbgroups = get_fb_user_groups(request.user)['data']
                else:
                    recruiter_social_profile.fbgroups = "Not permitted"
                if 'manage_pages' in debug_data['data']['scopes'] and 'publish_pages' in debug_data['data']['scopes']:
                    recruiter_social_profile.fbpages = get_fb_user_pages(request.user)['data']
                else:
                    recruiter_social_profile.fbpages = "Not permitted"
                request.session['fbpages'] = json.dumps(recruiter_social_profile.fbpages)
                request.session['fbgroups'] = json.dumps(recruiter_social_profile.fbgroups)
            else:
                recruiter_social_profile.fbstatus = 1
        elif profile.social_code == 'li':
            recruiter_social_profile.li = profile
            if 'id' in debug_data:
                recruiter_social_profile.listatus = 2
                comp = get_li_companies(request.user)
                if comp['_total'] > 0:
                    recruiter_social_profile.licompanies = comp['values']
                    request.session['licompanies'] = json.dumps(recruiter_social_profile.licompanies)
                else:
                    request.session['licompanies'] = json.dumps([])
            else:
                recruiter_social_profile.listatus = 1
        elif profile.social_code == 'tw':
            recruiter_social_profile.tw = profile    
            if 'id' in debug_data:
                recruiter_social_profile.twstatus = 2
            else:
                recruiter_social_profile.twstatus = 1
    return render(request,'smart_share.html',{'recruiter_social_profile':recruiter_social_profile,'vacancy':vacancy})

def socialshare(request):
    """Handle social media sharing functionality.

    Args:
        request: HTTP request containing share parameters

    Returns:
        HttpResponse: Share status
    """
    context = {}
    context['success'] = False
    context['msg'] = 'Unauthorised access'
    if request.method == 'POST' and request.user.is_authenticated and hasattr(request.user,'recruiter'):
        context['msg'] = 'Unauthorised access.'

        code = request.POST.get('social_code')
        message = request.POST.get('message','')
        vacancy_id = int(request.POST.get('vid'))
        vacancy = Vacancy.objects.filter(id=vacancy_id, company__in = request.user.recruiter.company.all())

        recruiter_social = request.user.socialauth_set.all()
        if vacancy and code:
            context['msg'] = 'Unauthorised access..'
            vacancy = vacancy[0]
            og={}
            referer_hash = Hashids(salt='Job Referal', min_length = 5)
            myreferal = 'ref-' + referer_hash.encode(request.user.recruiter.id)
            link = str(vacancy.get_absolute_url()).replace('http://','').replace('https://','')
            if request.POST.get('add_referal_link', False):
                link = link.strip('/') + '/' + myreferal + '/'
            if code.startswith('fbpersonal'):
                context['msg'] = 'Unauthorised access...'
                fbtoken = recruiter_social.filter(social_code='fb')
                if fbtoken:
                    fbtoken = fbtoken[0]
                    post_response = posttofbprofile(fbtoken,message,link)
                    if post_response.status_code == 200:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False
            elif code.startswith('fbgroup'):
                code = code.replace('fbgroup-','')
                fbtoken = recruiter_social.filter(social_code='fb')
                if fbtoken:
                    fbtoken = fbtoken[0]
                    post_response = posttofbgroup(fbtoken, code, message, link)
                    if post_response.status_code == 200:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False
            elif code.startswith('fbpage'):
                context['msg'] = 'Unauthorised access...'
                code = code.replace('fbpage-','')
                fbtoken = recruiter_social.filter(social_code='fb')
                if fbtoken:
                    fbtoken = fbtoken[0]
                    post_response = posttofbpage(fbtoken, code, message, link)
                    if post_response.status_code == 200:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False
                
            elif code.startswith('lipersonal'):
                og['title'] = str(vacancy.employment) + ' - ' + str(vacancy.function)
                og['description'] = str(strip_tags(vacancy.description))
                og['image'] = str(vacancy.company.logo.url)
                og['url'] = link
                litoken = recruiter_social.filter(social_code='li')
                if litoken:
                    litoken = litoken[0]
                    post_response = posttoliprofile(litoken, message, og)
                    if post_response.status_code == 201:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False
            elif code.startswith('licompany'):
                code = code.replace('licompany-','')
                og['title'] = str(vacancy.employment) + ' - ' + str(vacancy.function)
                og['description'] = str(strip_tags(vacancy.description))
                og['image'] = str(vacancy.company.logo.url)
                og['url'] = link
                litoken = recruiter_social.filter(social_code='li')
                if litoken:
                    litoken = litoken[0]
                    post_response = posttolicompany(litoken, code, message, og)
                    if post_response.status_code == 201:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False
            elif code.startswith('twpersonal'):
                twtoken = recruiter_social.filter(social_code='tw')
                if twtoken:
                    twtoken = twtoken[0]
                    post_response = posttotwitter(twtoken,message,link)
                    if post_response.status_code == 200:
                        context['success'] = True
                        context['msg'] = True
                    else:
                        context['success'] = True
                        context['msg'] = False

    return JsonResponse(context)

def revoke_social_auth(request, social_code):
    context = {}
    context['success'] = False
    if request.user.is_authenticated:
        # try:
            socialUser = SocialAuth.objects.get(user = request.user,social_code = social_code)
            result = revoke_token(socialUser.oauth_token,social_code)
            context['msg'] = 'Failed to revoke access'
            if result:
                context['msg'] = 'Access Revoked'
                context['success'] = True
        # except:
        #     context['msg'] = 'Social Authentication does not exist'
    else:
        context['msg'] = 'Unauthorised access'
    return JsonResponse(context)

@csrf_exempt
def schedule(request):
    """Create or update a schedule entry.

    Args:
        request: HTTP request containing schedule data

    Returns:
        JsonResponse: Schedule status
    """
    context={}
    json_context = {}
    candidate = Postulate.objects.filter(id = int(request.POST.get('candidate', 0)))
    if candidate:
        candidate = candidate[0]
        schedule = Schedule.objects.filter(application = candidate, status = 0, user=request.user)
        if schedule:
            schedule = schedule[0]
        else:
            schedule = None
        new_schedule = request.POST.get('schedule',None)
        if new_schedule:
            offset = int(request.POST.get('offset'),0)
            new_schedule = datetime.strptime(new_schedule, "%m/%d/%Y %I:%M %p")
            created = False
            if not schedule:
                schedule, created = Schedule.objects.get_or_create(status=0,application = candidate, user = request.user)
            schedule.scheduled_on = new_schedule + timedelta(minutes = int(offset)) + timedelta(minutes=330)
            schedule.offset = offset
            schedule.save()
            if created:
                json_context['msg'] = "Schedule Added"
            else:
                json_context['msg'] = "Schedule Updated"
        context['schedule'] = schedule
    else:
        candidate = None
        context['error_message'] = "No matching Candidate Profiles were found."
    context['candidate'] = candidate
    context['time_now'] = datetime.now()
    json_context['html_response'] = render_to_string('scheduler.html', context)
    return JsonResponse(json_context)

@csrf_exempt
def remove_schedule(request):
    """Remove a scheduled event.

    Args:
        request: HTTP request containing schedule ID

    Returns:
        JsonResponse: Removal status
    """
    context = {}
    context['success'] = False
    if request.method == 'POST' and is_ajax(request) and request.user.is_authenticated:
        candidate = Postulate.objects.filter(id = int(request.POST.get('candidate', 0)))
        if candidate:
            candidate = candidate[0]
            schedule = Schedule.objects.filter(application = candidate, status = 0, user=request.user)
            if schedule:
                schedule = schedule[0]
                schedule.status = 1
                schedule.save()
                context['success'] = True
                context['msg'] = 'Schedule Removed'
            else:
                context['msg'] = 'No Schedule to Remove.'
        else:
            context['msg'] = 'Candidate was not found'
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)

@csrf_exempt
def get_upcoming_schedule(request):
    """Retrieve upcoming scheduled events.

    Args:
        request: HTTP request containing filter parameters

    Returns:
        JsonResponse: List of upcoming events
    """
    context={}
    json_context = {}
    if is_ajax(request) and request.method == 'POST' and request.user.is_authenticated:
        context['recruiter'] = request.user.recruiter
        json_context['html_response'] = render_to_string('scheduled_widget.html',context)
    return JsonResponse(json_context)


def custom_template(request):
    """Handle custom template operations.

    Args:
        request: HTTP request containing template data

    Returns:
        HttpResponse: Template operation status
    """
    context={}
    context['success'] = False
    context['msg'] = ""
    context['html'] = ""
    context['preview'] = ""
    try:
        recruiter = Recruiter.objects.get(user = request.user)
    except:
        recruiter = None
    if is_ajax(request) and recruiter and recruiter.company.all()[0].check_service('JM_CUSTOM_APPLICATION_FORM'):
        form = TemplateForm()
        formset = FieldFormset()
        if request.method == 'POST':
            form = TemplateForm(request.POST)
            formset = FieldFormset(request.POST)
            if form.is_valid() and formset.is_valid():
                if len(formset.forms):
                    if not request.POST.get('preview',0):
                        instance = form.save()
                        instance.belongs_to = recruiter.company.all()[0]
                        instance.save()
                        formset = FieldFormset(request.POST,instance=instance)
                        if formset.is_valid():
                            fs = formset.save()
                            context['success'] = True
                            context['id'] = instance.id
                            context['name'] = instance.name
                    else:
                        context['success'] = True
                        context['preview'] = render(request,'templated_form.html',{'form':formset.templated_form(formClasses = "form-control"),'preview':True}).__dict__['_container']
                else:
                    form.add_error('name','At least one field is required in a template')
            context['html'] = render(request,'template_form.html', {'template_form':form,'template_formset':formset}).__dict__['_container']
        elif request.method == 'GET':
            try:
                template = Template.objects.get(id = int(request.GET.get('template',0)))
            except:
                template = None
            if template:
                context['html'] = template.rendered_form(preview = True)
    else:
        context['msg'] = 'Unauthorised Access!'
    return JsonResponse(context)

@csrf_exempt
def update_site_template(request):
    """Update the site's template settings.

    Args:
        request: HTTP request containing template update data

    Returns:
        JsonResponse: Update status
    """
    context={}
    context['success'] = False
    if request.user.is_authenticated and request.user.recruiter.is_manager() and is_ajax(request) and request.method == 'POST':
        template_id = request.POST.get('template_id', None)
        template = 'careers/base/t-'+ str(template_id) +'/jobs.html'
        valid = False
        try:
            get_template(template)
            valid = True
        except TemplateDoesNotExist:
            context['msg'] = 'Please select a valid template to continue.'
        if valid:
            subdomain_data = subdomain(request)
            if not subdomain_data['active_host']:
                context['msg'] = 'Unauthorised access'
                return JsonResponse(context)
            company = Company.objects.filter(subdomain__slug=subdomain_data['active_subdomain'])
            if not company or not company[0] in request.user.recruiter.company.all():
                context['msg'] = 'Unauthorised access'
                return JsonResponse(context)
            company = company[0]
            company.site_template = template_id
            above_job = str(get_template('careers/base/t-'+ str(template_id) +'/above_jobs.html').render(Context({'STATIC_URL':STATIC_URL})))
            company.above_jobs = above_job
            below_job = str(get_template('careers/base/t-'+ str(template_id) +'/below_jobs.html').render(Context({'STATIC_URL':STATIC_URL})))
            company.below_jobs = below_job
            company.save()
            context['msg'] = 'Template Updated'
            context['success'] = True
    else:
        context['msg'] = 'Unauthorised access'
    return JsonResponse(context)

@csrf_exempt
def save_template(request):
    """Save a new or updated template.

    Args:
        request: HTTP request containing template data

    Returns:
        JsonResponse: Save operation status
    """
    context = {}
    context['success'] = False
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = Company.objects.filter(subdomain__slug=subdomain_data['active_subdomain'])
    if not company or not company[0] in request.user.recruiter.company.all():
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = company[0]
    if request.user.is_authenticated and request.user.recruiter.is_manager() and is_ajax(request) and request.method == 'POST':
        above_jobs = request.POST.get('above_jobs');
        below_jobs = request.POST.get('below_jobs');
        if above_jobs and below_jobs:
            company.above_jobs = above_jobs
            company.below_jobs = below_jobs
            company.save()
            context['success'] = True
        else:
            context['msg'] = 'Save data not provided.'
    else:
        context['msg'] = 'Unauthorised access'
    return JsonResponse(context)

@csrf_exempt
def get_evaluators(request):
    context = {}
    context['success'] = False
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = Company.objects.filter(subdomain__slug=subdomain_data['active_subdomain'])
    if not company or not company[0] in request.user.recruiter.company.all():
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = company[0]
    if request.user.is_authenticated and request.user.recruiter.is_manager() and is_ajax(request) and request.method == 'POST':
        try:
            vstage = VacancyStage.objects.get(id = request.POST.get('vid'))
        except:
            vstage = None
        if vstage:
            context['recruiters'] = [r.id for r in vstage.recruiters.all()]
            context['success'] = True
    else:
        context['msg'] = 'Unauthorised access'
    return JsonResponse(context)

@csrf_exempt
def get_process_criterias(request):
    context = {}
    context['success'] = False
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = Company.objects.filter(subdomain__slug=subdomain_data['active_subdomain'])
    if not company or not company[0] in request.user.recruiter.company.all():
        context['msg'] = 'Unauthorised access'
        return JsonResponse(context)
    company = company[0]
    if request.user.is_authenticated and request.user.recruiter.is_manager() and is_ajax(request) and request.method == 'POST':
        try:
            vstage = VacancyStage.objects.get(id = request.POST.get('vid'))
        except:
            vstage = None
        if vstage:
            context['criteria_modal_content'] = render_to_string('vacancy_stage_criteria_modal_content.html',{
                    'current_process': vstage
                })
            context['criteria_list'] = render_to_string('vacancy_stage_criteria_content.html',{
                    'current_process': vstage
                })
            context['success'] = True
    else:
        context['msg'] = 'Unauthorised access'
    return JsonResponse(context)


@csrf_exempt 
def resolve_conflicts_delete(request):
    """Handle deletion of conflicting entries.

    Args:
        request: HTTP request containing conflict resolution data

    Returns:
        JsonResponse: Resolution status
    """
    context = {}
    context['success'] = False
    context['reload'] = True
    if request.user.is_authenticated and request.user.profile.codename == 'candidate' and is_ajax(request) and request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        card_type = request.POST.get('card_type')
        length = 0
        if card_type == '1':
            academics = Academic.objects.filter(id__in=ids)
            length = len(academics)
            for academic in academics:
                if not academic.candidate.parent_profile:
                    context['reload'] = True
                academic.delete()
                print('DELETED')
        elif card_type == '2':
            expertises = Expertise.objects.filter(id__in=ids)
            length = len(expertises)
            for expertise in expertises:
                if not expertise.candidate.parent_profile:
                    context['reload'] = True
                expertise.delete()
                print('DELETED')
        context['msg'] = str(length) + ' cards removed.'
        if context['reload']:
            messages.success(request,context['msg'])
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)


def template_form(request):
    context = {}
    context['success'] = False
    context['msg'] = ""
    context['html'] = ""
    try:
        vacancy = Vacancy.objects.get(id = int(request.POST['vacancy']))
        postulate = Postulate.objects.get(id=int(request.session.get('applicant',0)))
    except:
        vacancy = None
        postulate = None
    if is_ajax(request) and request.method == 'POST' and vacancy and postulate and postulate.vacancy == vacancy and vacancy.form_template and vacancy.company.check_service('JM_CUSTOM_APPLICATION_FORM'):
        form = TemplatedForm(request.POST, template = vacancy.form_template, formClasses="form-control")
        if form.is_valid():
            fields = form.save()
            postulate.has_filled_custom_form = True
            for field in fields:
                postulate.custom_form_application.add(field)
            postulate.save()
            context['success'] = True
            request.session.pop('fill_template')
            request.session.pop('applicant')
            messages.success(request, 'Successfully completed application')
        else:
            context['html'] = render_to_string('templated_form',{'form':form})
    else:
        messages.error(request, 'Unauthorised access')
    return JsonResponse(context)

@csrf_exempt
def template_form_data(request):
    context = {}
    context['html'] = ""
    context['msg'] = ''
    try:
        recruiter = Recruiter.objects.get(user = request.user)
    except:
        recruiter = None
    if recruiter and is_ajax(request) and request.method == 'POST':
        candidate = Postulate.objects.filter(id = int(request.POST.get('candidate', 0)))
        if candidate:
            candidate = candidate[0]
            context['html'] = render_to_string('template_form_data.html',{'candidate':candidate})
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)

@csrf_exempt 
def resolve_conflicts_unconflict(request):
    """Mark conflicts as resolved without merging.

    Args:
        request: HTTP request containing conflict data

    Returns:
        JsonResponse: Resolution status
    """
    context = {}
    context['success'] = False
    context['reload'] = True
    if request.user.is_authenticated and request.user.profile.codename == 'candidate' and is_ajax(request) and request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        card_type = request.POST.get('card_type')
        length = 0
        if card_type == '1':
            academics = Academic.objects.filter(id__in=ids)
            length = len(academics)
            for academic in academics:
                academic.candidate = request.user.candidate
                acadmemic.save()
                print('UNCONFLICTED')
        elif card_type == '2':
            expertises = Expertise.objects.filter(id__in=ids)
            length = len(expertises)
            for expertise in expertises:
                expertise.candidate = request.user.candidate
                expertise.save()
                print('UNCONFLICTED')
        context['msg'] = str(length) + ' cards updated.'
        if context['reload']:
            messages.success(request,context['msg'])
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)

@csrf_exempt
def resolve_conflicts_merge(request):
    """Merge conflicting entries.

    Args:
        request: HTTP request containing merge parameters

    Returns:
        JsonResponse: Merge operation status
    """
    context = {}
    context['success'] = False
    context['reload'] = False
    if request.user.is_authenticated and request.user.profile.codename == 'candidate' and is_ajax(request) and request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        card_type = request.POST.get('card_type')
        length = 0
        if card_type == '1':
            academics = Academic.objects.filter(id__in=ids)
            length = len(academics)
            merge_data = {
                'degree': {'more_options': [], 'values': []},
                'area': {'more_options': [], 'values': []},
                'status': {'more_options': [], 'values': []},
                'course_name': {'more_options': [], 'values': []},
                'school':{'more_options': [], 'values': []},
                'country':{'more_options': [], 'values': []},
                'state': {'more_options': [], 'values': []},
                'city': {'more_options': [], 'values': []},
                'start_date': {'more_options': [], 'values': []},
                'end_date': {'more_options': [], 'values': []},
            }
            for academic in academics:
                if academic.degree and academic.degree.name not in merge_data['degree']['values']:
                    merge_data['degree']['values'].append(academic.degree.name)
                if academic.area and academic.area not in merge_data['area']['values']:
                    merge_data['area']['values'].append(academic.area)
                if academic.status and academic.status.name not in merge_data['status']['values']:
                    merge_data['status']['values'].append(academic.status.name)
                if academic.course_name and academic.course_name not in merge_data['course_name']['values']:
                    merge_data['course_name']['values'].append(academic.course_name)
                if academic.school and academic.school not in merge_data['school']['values']:
                    merge_data['school']['values'].append(academic.school)
                if academic.country and academic.country.name not in merge_data['country']['values']:
                    merge_data['country']['values'].append(academic.country.name)
                if academic.state and academic.state not in merge_data['state']['values']:
                    merge_data['state']['values'].append(academic.state)
                if academic.city and academic.city not in merge_data['city']['values']:
                    merge_data['city']['values'].append(academic.city)
                if academic.start_date and academic.start_date not in merge_data['start_date']['values']:
                    merge_data['start_date']['values'].append(academic.start_date)
                if academic.end_date and academic.end_date not in merge_data['end_date']['values']:
                    merge_data['end_date']['values'].append(academic.end_date)
            if len(merge_data['degree']['values'])>1 or len(merge_data['area']['values'])>1 or len(merge_data['status']['values'])>1 or len(merge_data['course_name']['values'])>1 or len(merge_data['school']['values'])>1 or len(merge_data['country']['values'])>1 or len(merge_data['state']['values'])>1 or len(merge_data['city']['values'])>1 or len(merge_data['start_date']['values'])>1 or len(merge_data['end_date']['values'])>1:
                merge_data['degree']['more_options'] = list(Degree.objects.exclude(name__in=merge_data['degree']['values']).values_list('name', flat= True))
                merge_data['status']['more_options'] = list(Academic_Status.objects.exclude(name__in=merge_data['status']['values']).values_list('name', flat= True))
                merge_data['country']['more_options'] = list(Country.objects.exclude(name__in=merge_data['country']['values']).values_list('name', flat= True))
                context['merge_fields'] = merge_data
                context['merge_field_template'] = render_to_string('conflict_merge_fields.html',{'data':merge_data,'card_type':card_type,'old_cards':ids})
            else:
                try:
                    degree = Degree.objects.get(name = merge_data['degree']['values'][0])
                except:
                    degree = None
                try:
                    status = Academic_Status.objects.get(name = merge_data['status']['values'][0])
                except:
                    status = None
                try:
                    country = Country.objects.get(name = merge_data['country']['values'][0])
                except:
                    country = None
                merged_entry = Academic.objects.create(
                        degree = degree, 
                        area = ','.join(merge_data['area']['values']), 
                        status = status,
                        course_name = ','.join(merge_data['course_name']['values']), 
                        school = ','.join(merge_data['school']['values']), 
                        country = country,
                        state = ','.join(merge_data['state']['values']), 
                        city = ','.join(merge_data['city']['values']), 
                        start_date = ','.join(merge_data['start_date']['values']), 
                        end_date = ','.join(merge_data['end_date']['values']), 
                        candidate = request.user.candidate
                    )
                academics.delete()
                print("CREATED NEW AND DELETED OLD")
                context['reload'] = True
                context['msg'] = "Cards Merged"
        elif card_type == '2':
            expertises = Expertise.objects.filter(id__in=ids)
            length = len(expertises)
            merge_data = {
                'company': {'more_options': [], 'values': []},
                'industry': {'more_options': [], 'values': []},
                'employment': {'more_options': [], 'values': []},
                # 'present': {'more_options': [], 'values': []},
                'tasks':{'more_options': [], 'values': []},
                # 'country':{'more_options': [], 'values': []},
                # 'state': {'more_options': [], 'values': []},
                # 'city': {'more_options': [], 'values': []},
                'start_date': {'more_options': [], 'values': []},
                'end_date': {'more_options': [], 'values': []},
            }
            for expertise in expertises:
                if expertise.company and expertise.company not in merge_data['company']['values']:
                    merge_data['company']['values'].append(expertise.company)
                if expertise.employment and expertise.employment not in merge_data['employment']['values']:
                    merge_data['employment']['values'].append(expertise.employment)
                if expertise.tasks and expertise.tasks not in merge_data['tasks']['values']:
                    merge_data['tasks']['values'].append(expertise.tasks)
                if expertise.start_date and expertise.start_date not in merge_data['start_date']['values']:
                    merge_data['start_date']['values'].append(expertise.start_date)
                if expertise.end_date and expertise.end_date not in merge_data['end_date']['values']:
                    merge_data['end_date']['values'].append(expertise.end_date)
                # if expertise.present and expertise.present not in merge_data['present']['values']:
                #     merge_data['present']['values'].append(str(expertise.present))
                if expertise.industry and expertise.industry.name not in merge_data['industry']['values']:
                    merge_data['industry']['values'].append(expertise.industry.name)
            if len(merge_data['company']['values'])>1 or len(merge_data['employment']['values'])>1 or len(merge_data['tasks']['values'])>1 or len(merge_data['start_date']['values'])>1 or len(merge_data['end_date']['values'])>1 or len(merge_data['industry']['values'])>1:
                merge_data['industry']['more_options'] = list(Company_Industry.objects.exclude(name__in=merge_data['industry']['value']).values_list('name', flat= True))
                context['merge_fields'] = merge_data
                context['merge_field_templates'] = render_to_string('conflict_merge_fields.html', {'data':merge_data,'card_type':card_type, 'old_cards':ids})
            else:
                try:
                    industry = Company_Industry.objects.get(name = merge_data['industry']['values'][0])
                except:
                    industry = None
                merged_entry = Expertise.objects.create(
                        company = ','.join(merge_data['company']['values']), 
                        employment = ','.join(merge_data['employment']['values']), 
                        tasks = ','.join(merge_data['tasks']['values']), 
                        industry = industry, 
                        start_date = ','.join(merge_data['start_date']['values']), 
                        end_date = ','.join(merge_data['end_date']['values']), 
                        candidate = request.user.candidate
                    )
                expertises.delete()
                context['reload'] = True
                context['msg'] = "Cards Merged"
        if context['reload']:
            messages.success(request,context['msg'])
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)


@csrf_exempt
def add_external_referal(request):
    context = {}
    context['success'] = False
    context['reload'] = False
    if request.user.is_authenticated and request.user.profile.codename == 'recruiter' and is_ajax(request) and request.method == 'POST' and request.user.recruiter.is_manager():
        reftype = request.POST.get('reftype')
        refname = request.POST.get('refname')
        vacancy_id = request.POST.get('vid')
        try:
            vacancy = Vacancy.objects.get(id = vacancy_id)
        except: 
            vacancy = None
        try:
            company = request.user.recruiter.company.all()[0]
        except: 
            company = None
        if company:
            if refname:
                try:
                    newref = ExternalReferal(company = company, name = refname, referal_type = reftype)
                    newref.save()
                except:
                    newref = None
                    context['msg'] = 'Could not create New Referal. Please check the name and try again.'
            else:
                newref = None
                context['msg'] = 'Could not create New Referal. Please check the name and try again.'
            if newref:
                context['success'] = True
                if vacancy:
                    context['html'] = render_to_string('external_referer_subblock.html',{'x':newref,'vacancy':vacancy})
                else:
                    context['html'] = render_to_string('external_referer_subblock.html',{'x':newref,'label_only':True})
        else:
            context['msg'] = 'Unauthorised Access'
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)

@csrf_exempt
def remove_external_referal(request):
    context = {}
    context['success'] = False
    context['reload'] = False
    if request.user.is_authenticated and request.user.profile.codename == 'recruiter' and is_ajax(request) and request.method == 'POST' and request.user.recruiter.is_manager():
        refid= request.POST.get('refid')
        try:
            company = request.user.recruiter.company.all()[0]
        except: 
            company = None
        try:
            referal = ExternalReferal.objects.get(id=refid)
        except: 
            referal = None
        if company and referal and referal.company == company:
            referal.delete()
            context['success'] = True
            context['msg'] = 'Referal Removed.'
        else:
            context['msg'] = 'Unauthorised Access'
    else:
        context['msg'] = 'Unauthorised Access'
    return JsonResponse(context)