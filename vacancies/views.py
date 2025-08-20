# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import ast
import json
import traceback
from activities.utils import post_activity
from candidates.models import Candidate, Curriculum, Academic, Academic_Status
from common.forms import ContactForm
from common.models import Employment_Type, Country, Gender, User, Profile, SocialAuth, send_TRM_email
from common.views import debug_token, get_fb_user_groups, get_fb_user_pages, get_li_companies
from companies.models import Company, Stage, Recruiter, Company_Industry as Industry, ExternalReferal
from customField.forms import TemplatedForm
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, NoReverseMatch, resolve
from django.db.models import Count, Q
from django.http import QueryDict, HttpResponseNotFound, JsonResponse, Http404, HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.template import RequestContext,Context, Node, Library, TemplateSyntaxError, VariableDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import urlparse
#from django.utils.timezone import utc
import datetime
utc = datetime.timezone.utc
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from hashids import Hashids
from payments.models import *
from TRM.context_processors import subdomain
from TRM.settings import days_default_search, SITE_URL, LOGO_COMPANY_DEFAULT, num_pages, number_objects_page, MEDIA_ROOT
from vacancies.forms import BasicSearchVacancyForm, QuestionVacancyForm, Public_FilesForm, Public_Files_OnlyForm, get_notice_period
from vacancies.models import Vacancy, PubDate_Search, Vacancy_Status, Postulate, Salary_Type, \
    Employment_Experience, Degree,Question, Vacancy_Files, Candidate_Fav, VacancyStage, \
    Postulate_Stage, Postulate_Score, Comment, Medium
from six.moves import range
from utils import is_ajax
referer_hash = Hashids(salt='Job Referal', min_length = 5)
external_referer_hash = Hashids(salt='Job External Referal', min_length=5)


def get_vacancy_active_status():
    """
    Retrieve the Vacancy_Status instance with codename 'open' representing active vacancies.

    Returns:
        Vacancy_Status or None: The Vacancy_Status object with codename 'open', or None if not found.
    """
    try:
        status = Vacancy_Status.objects.get(codename='open')
    except Vacancy_Status.DoesNotExist:
        return None
    return status

def first_search(request):
    """ 
    Retrieve the Vacancy_Status instance with codename 'open' representing active vacancies.

    Returns:
        Vacancy_Status or None: The Vacancy_Status object with codename 'open' or None if not found.
    """
    if request.user.is_authenticated and not request.user.email:
        # If user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

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

    # Curricula Search Sessions
    if request.user.is_authenticated:
        # profile = UserProfile.objects.get(user=request.user).profile.codename
        profile = request.user.profile
        if profile == 'recruiter':
            request.session['candidates_cvs'] = []
            request.session['first_search_cvs'] = None
            request.session['degrees'] = None
            request.session['status'] = None
            request.session['area'] = None
            request.session['careers'] = None
            request.session['state'] = None
            request.session['municipal'] = None
            request.session['gender'] = None
            request.session['min_age'] = None
            request.session['max_age'] = None
            request.session['travel'] = None
            request.session['residence'] = None
            request.session['language_1'] = None
            request.session['level_1'] = None
            request.session['language_2'] = None
            request.session['level_2'] = None
            request.session['candidates_cvs'] = []

    return redirect('vacancies_search_vacancies')

def get_comments(request):
    """
    Retrieve all Question objects representing comments.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        QuerySet: All Question objects.
    """
    all_comments =Question.objects.all()
    comments=all_comments
    return comments

def get_vacancies_and_filters(request):
    """
    Retrieve and filter vacancies based on session search parameters, and prepare filter data for the sidebar.

    This includes filtering vacancies by industry, area, state, employment type, publication date,
    and search text. It also computes aggregated counts for publication dates, industries, states,
    and employment types to populate filter options.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        QuerySet: The filtered vacancies queryset.
    """
    #### Section Vacancies ####
    all_vacancies = Vacancy.publishedjobs.all()
    vacancies = all_vacancies

    # The filters are added to vacancies based on search parameters
    vacancies_search_industry = request.session.get('vacancies_search_industry')
    vacancies_search_area = request.session.get('vacancies_search_area')
    vacancies_search_state = request.session.get('vacancies_search_state')
    vacancies_search_employment_type = request.session.get('vacancies_search_employment_type')
    vacancies_search_pub_date = request.session.get('vacancies_search_pub_date')
    vacancies_search_text = request.session.get('vacancies_search_text')

    del_filters = False

    if vacancies_search_industry:
        vacancies = vacancies.filter(industry_id=vacancies_search_industry)
        del_filters = True
    if vacancies_search_area:
        vacancies = vacancies.filter(area_id=vacancies_search_area)
        del_filters = True
    if vacancies_search_state:
        vacancies = vacancies.filter(state_id=vacancies_search_state)
        del_filters = True
    if vacancies_search_employment_type:
        vacancies = vacancies.filter(employmentType_id=vacancies_search_employment_type)
        del_filters = True
    if vacancies_search_text:
        vacancies = vacancies.filter(Q(employment__icontains=vacancies_search_text) |
                                     Q(description__icontains=vacancies_search_text))
        del_filters = True

    request.session['del_filters'] = del_filters

    ####  Home section filters the side panel ####

    # Starts section date Published #
    pubDates = PubDate_Search.objects.all()
    pub_dates = []
    for pubDate in pubDates:
        vacancy_pub_dates = all_vacancies
        # Right way to get the current date and avoid warning
        # (DateTimeField received a naive datetime while time zone support is active)
        now = datetime.utcnow().replace(tzinfo=utc)
        search_date = now - timedelta(days=pubDate.days)


        # State, Type of Employment
        if vacancies_search_state and vacancies_search_employment_type:
            vacancy_pub_dates = vacancy_pub_dates.filter(state_id=vacancies_search_state,
                                                         employmentType_id=vacancies_search_employment_type)
        # State
        elif vacancies_search_state:
            vacancy_pub_dates = vacancy_pub_dates.filter(state_id=vacancies_search_state)
        # Type of Employment
        elif vacancies_search_employment_type:
            vacancy_pub_dates = vacancy_pub_dates.filter(employmentType_id=vacancies_search_employment_type)
        else:
            pass
        # Words from search form
        if vacancies_search_text:
            vacancy_pub_dates = vacancy_pub_dates.filter(Q(employment__icontains=vacancies_search_text) |
                                                         Q(description__icontains=vacancies_search_text))

        vacancy_pub_dates = vacancy_pub_dates.filter(pub_date__gte=search_date)

        if vacancy_pub_dates:
            pub_dates.append([pubDate, vacancy_pub_dates.count()])

    if not vacancies_search_pub_date:
        now = datetime.utcnow().replace(tzinfo=utc)
        vacancies_search_pub_date = now - timedelta(days=days_default_search)
        request.session['vacancies_search_pub_date_days'] = get_object_or_404(PubDate_Search,
                                                                              days=days_default_search)

    vacancies = vacancies.filter(pub_date__gte=vacancies_search_pub_date)
    # End section Date Published #

    # Start Section Industries #
    vacancy_industries = all_vacancies

    # State, Type of Employment
    if vacancies_search_state and vacancies_search_employment_type:
        vacancy_industries = vacancy_industries.filter(state_id=vacancies_search_state,
                                                       employmentType_id=vacancies_search_employment_type). \
            order_by('industry').values('industry').annotate(count=Count('industry'))
    # State
    elif vacancies_search_state:
        vacancy_industries = vacancy_industries.filter(state_id=vacancies_search_state). \
            order_by('industry').values('industry').annotate(count=Count('industry'))
    # Type of Employment
    elif vacancies_search_employment_type:
        vacancy_industries = vacancy_industries.filter(employmentType_id=vacancies_search_employment_type). \
            order_by('industry').values('industry').annotate(count=Count('industry'))
    else:
        vacancy_industries = vacancy_industries.filter(status=get_vacancy_active_status()). \
            order_by('industry').values('industry').annotate(count=Count('industry'))
    # Words from Search Form
    if vacancies_search_text:
        vacancy_industries = vacancy_industries.filter(Q(employment__icontains=vacancies_search_text) |
                                                       Q(description__icontains=vacancies_search_text))

    vacancy_industries = vacancy_industries.filter(pub_date__gte=vacancies_search_pub_date)

    industries = []
    for industry in vacancy_industries:
        if industry['industry']:
            count = industry['count']
            industry = get_object_or_404(Industry, pk=industry['industry'])
            industries.append([industry, count])
    # End of section Industries #

    # Start of section States #
    vacancy_states = all_vacancies

    # Industries, Type of Employment
    if vacancies_search_industry and vacancies_search_employment_type:
        vacancy_states = vacancy_states.filter(industry_id=vacancies_search_industry,
                                               employmentType_id=vacancies_search_employment_type). \
            order_by('state').values('state').annotate(count=Count('state'))
    # Industries
    elif vacancies_search_industry:
        vacancy_states = vacancy_states.filter(industry_id=vacancies_search_industry). \
            order_by('state').values('state').annotate(count=Count('state'))
    # Type of Employment
    elif vacancies_search_employment_type:
        vacancy_states = vacancy_states.filter(employmentType_id=vacancies_search_employment_type). \
            order_by('state').values('state').annotate(count=Count('state'))
    else:
        vacancy_states = vacancy_states.filter(status=get_vacancy_active_status()). \
            order_by('state').values('state').annotate(count=Count('state'))
    # Words from Search Form
    if vacancies_search_text:
        vacancy_states = vacancy_states.filter(Q(employment__icontains=vacancies_search_text) |
                                               Q(description__icontains=vacancies_search_text))

    vacancy_states = vacancy_states.filter(pub_date__gte=vacancies_search_pub_date)

    states = []
    for state in vacancy_states:
        if state['state']:
            count = state['count']
            # state = get_object_or_404(State, pk=state['state'])
            states.append([state, count])
    # End of section States #

    # Start of section Types of Employment #
    vacancy_employment_types = all_vacancies

    # Industries, State
    if vacancies_search_industry and vacancies_search_state:
        vacancy_employment_types = vacancy_employment_types.filter(industry_id=vacancies_search_industry,
                                                                   state_id=vacancies_search_state). \
            order_by('employmentType').values('employmentType').annotate(count=Count('employmentType'))
    # Industries
    elif vacancies_search_industry:
        vacancy_employment_types = vacancy_employment_types.filter(industry_id=vacancies_search_industry). \
            order_by('employmentType').values('employmentType').annotate(count=Count('employmentType'))
    # State
    elif vacancies_search_state:
        vacancy_employment_types = vacancy_employment_types.filter(state_id=vacancies_search_state). \
            order_by('employmentType').values('employmentType').annotate(count=Count('employmentType'))
    else:
        vacancy_employment_types = vacancy_employment_types.filter(status=get_vacancy_active_status()). \
            order_by('employmentType').values('employmentType').annotate(count=Count('employmentType'))
    # Words from Search Form
    if vacancies_search_text:
        vacancy_employment_types = vacancy_employment_types.filter(Q(employment__icontains=vacancies_search_text) |
                                                                   Q(description__icontains=vacancies_search_text))

    vacancy_employment_types = vacancy_employment_types.filter(pub_date__gte=vacancies_search_pub_date)

    employment_types = []
    for employment_type in vacancy_employment_types:
        if employment_type['employmentType']:
            count = employment_type['count']
            employmenType = get_object_or_404(Employment_Type, pk=employment_type['employmentType'])
            employment_types.append([employmenType, count])
    # End of section Types of Employment #

    # The results are assigned to the session variable
    request.session['pub_dates'] = pub_dates
    request.session['industries'] = industries
    request.session['states'] = states
    request.session['employment_types'] = employment_types

    return vacancies

def filter_vacancies_by_industry(request, industry_id=None):
    """
    Stores the selected industry filter in the session based on the provided industry_id.
    
    If industry_id is not zero, it fetches the corresponding Industry object and stores it in the session.
    If industry_id is zero, it clears the industry filter from the session.

    Args:
        request (HttpRequest): The incoming HTTP request.
        industry_id (int or None): ID of the industry to filter vacancies by.

    Returns:
        HttpResponseRedirect: Redirects to the vacancies search results page.
    """
    if industry_id:
        if int(industry_id) != 0:
            request.session['vacancies_search_industry'] = get_object_or_404(Industry, pk=int(industry_id))
        elif int(industry_id) == 0:
            request.session['vacancies_search_industry'] = None
    return redirect('vacancies_search_vacancies')

def filter_vacancies_by_state(request, state_id=None):
    """
    Stores the selected state filter in the session based on the provided state_id.

    If state_id is not zero, it fetches the corresponding State object and stores it in the session.
    If state_id is zero, it clears the state filter from the session.

    Args:
        request (HttpRequest): The incoming HTTP request.
        state_id (int or None): ID of the state to filter vacancies by.

    Returns:
        HttpResponseRedirect: Redirects to the vacancies search results page.
    """
    if state_id:
        if int(state_id) != 0:
            request.session['vacancies_search_state'] = get_object_or_404(State, pk=int(state_id))
        elif int(state_id) == 0:
            request.session['vacancies_search_state'] = None
    return redirect('vacancies_search_vacancies')

def filter_vacancies_by_employment_type(request, employmentType_id):
    """
    Stores the selected employment type filter in the session based on the provided employmentType_id.

    If employmentType_id is not zero, it fetches the corresponding Employment_Type object and stores it.
    If employmentType_id is zero, it clears the employment type filter from the session.

    Args:
        request (HttpRequest): The incoming HTTP request.
        employmentType_id (int): ID of the employment type to filter vacancies by.

    Returns:
        HttpResponseRedirect: Redirects to the vacancies search results page.
    """
    if employmentType_id:
        if int(employmentType_id) != 0:
            request.session['vacancies_search_employment_type'] = get_object_or_404(Employment_Type,
                                                                                    pk=employmentType_id)
        elif int(employmentType_id) == 0:
            request.session['vacancies_search_employment_type'] = None
    return redirect('vacancies_search_vacancies')

def filter_vacancies_by_pub_date(request, days):
    """
    Stores the publication date filter in the session based on the provided number of days.

    If days is between 1 and 30, filters vacancies published within that range.
    Otherwise, applies a default day range (defined in days_default_search).

    Args:
        request (HttpRequest): The incoming HTTP request.
        days (int): Number of days to filter vacancies by publication date.

    Returns:
        HttpResponseRedirect: Redirects to the vacancies search results page.
    """
    if days:
        now = datetime.utcnow().replace(tzinfo=utc)
        if int(days) > 0 < 30:
            request.session['vacancies_search_pub_date'] = now - timedelta(days=int(days))
            request.session['vacancies_search_pub_date_days'] = get_object_or_404(PubDate_Search, days=days)
        else:
            request.session['vacancies_search_pub_date'] = now - timedelta(days=days_default_search)
            request.session['vacancies_search_pub_date_days'] = get_object_or_404(PubDate_Search,
                                                                                  days=days_default_search)
    return redirect('vacancies_search_vacancies')

def search_vacancies(request, template_name):
    """ Seen search for vacancy and currently also """
    """
    Handles vacancy search logic, including filtering, form processing, session storage, and pagination.

    If the request method is POST, it validates and processes the submitted form.
    If GET, it retrieves vacancies using existing filters stored in the session.
    Renders the appropriate template with filtered vacancy results and auxiliary data.

    Args:
        request (HttpRequest): The incoming HTTP request.
        template_name (str): The template to render, e.g., 'index.html' or search results page.

    Returns:
        HttpResponse: Rendered HTML page with context including vacancies, filters, and UI components.
    """
    # raise ValueError()
    subdomain_data = subdomain(request)

    
    if not subdomain_data['active_subdomain'] and not subdomain_data['isRoot']:
        # raise ValueError()
        raise Http404
        # pass
    if request.user.is_authenticated and not request.user.email:
        # If user is logged in and has no email...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    vacancies = None
    # Search Form
    if request.method == 'POST':
        try:
            if int(request.POST['industry']) <= 0:
                request.session['industry_selected'] = None
            else:
                request.session['industry_selected'] = Industry.objects.get(id=request.POST['industry'])
        except:
            request.session['industry_selected'] = None

        form = BasicSearchVacancyForm(data=request.POST, files=request.FILES,
                                      industry_selected=request.session.get('industry_selected'))

        if form.is_valid():
            request.session['vacancies_search_state'] = form.clean_state()
            request.session['vacancies_search_industry'] = form.clean_industry()
            request.session['vacancies_search_area'] = form.clean_area()
            pubDateSearch = form.clean_vacancyPubDateSearch()
            gender = form.clean_gender()
            degree = form.clean_degree()
            now = datetime.utcnow().replace(tzinfo=utc)
            request.session['vacancies_search_pub_date'] = now - timedelta(days=pubDateSearch.days)
            request.session['vacancies_search_pub_date_days'] = pubDateSearch
            if len(form.data['search']) > 4:
                request.session['vacancies_search_text'] = form.data['search']
            else:
                request.session['vacancies_search_text'] = None
            vacancies = get_vacancies_and_filters(request)
            if gender.codename != 'indistinct':
                vacancies = vacancies.filter(gender_id=gender)
            if degree.codename != 'indistinct':
                vacancies = vacancies.filter(degree_id=degree)
            if vacancies:
                form = BasicSearchVacancyForm(initial={'vacancyPubDateSearch': PubDate_Search.objects.get(days=days_default_search)})
            else:
                messages.error(request, _('No vacancy that meets the criteria found in selected search '))
    else:
        form = BasicSearchVacancyForm(initial={'vacancyPubDateSearch': PubDate_Search.objects.get(days=days_default_search)})
        if template_name != 'index.html':
            vacancies = get_vacancies_and_filters(request)

    total_vacancies = 0
    if vacancies:
        total_vacancies = vacancies.count()

    if not request.session.get('vacancies_search_state'):
        search_state = _('All')
    else:
        search_state = request.session.get('vacancies_search_state')
    if not request.session.get('vacancies_search_industry'):
        search_industry = _('All Industries')
    else:
        search_industry = request.session.get('vacancies_search_industry')
    if not request.session.get('vacancies_search_area'):
        search_area = _('All Areas')
    else:
        search_area = request.session.get('vacancies_search_area')
        request.session['vacancies_search_area'] = None
    if not request.session.get('vacancies_search_employment_type'):
        search_employment_type = _('Any Kind')
    else:
        search_employment_type = request.session.get('vacancies_search_employment_type')

    if template_name == 'index.html':
        isIndex = True
        isSearchVacancies = False
        latest_vacancies = Vacancy.publishedjobs.all()[:20]
        form_contact = ContactForm(request=request)
        packages = Package.objects.all()
        service_categories = ServiceCategory.objects.all()
    else:
        packages = None
        service_categories = None
        form_contact = None
        isIndex = False
        isSearchVacancies = True
        latest_vacancies = None

    try:
        # Get Favourite Vacancies and Applications
        candidate = Candidate.objects.get(user=request.user)
        postulates = Postulate.objects.filter(candidate_id=candidate.id)
        vacancy_favs_ids = Candidate_Fav.objects.filter(candidate_id=candidate.id).values_list('vacancy_id', flat=True).order_by('-vacancy_id')
    except:
        postulates = None
        vacancy_favs_ids = None

    # Pagination
    link_anterior = 1
    link_siguiente = 1
    maximo_paginas = 1
    minimo_paginas = 0
    num_pages_visible = num_pages
    paginas_finales = 0

    if template_name != 'index.html':
        paginator = Paginator(vacancies, number_objects_page)
        page = request.GET.get('page')
        try:
            vacancies = paginator.page(page)
        except PageNotAnInteger:
            vacancies = paginator.page(1)
        except EmptyPage:
            vacancies = paginator.page(paginator.num_pages)

        if vacancies.paginator.num_pages > num_pages_visible:
            if vacancies.number <= num_pages_visible/2:
                maximo_paginas = num_pages_visible
                minimo_paginas = 1
            elif vacancies.number > vacancies.paginator.num_pages - (num_pages_visible/2):
                maximo_paginas = vacancies.paginator.num_pages
                minimo_paginas = vacancies.paginator.num_pages - num_pages_visible
            else:
                minimo_paginas = vacancies.number - (num_pages_visible/2)
                maximo_paginas = vacancies.number + (num_pages_visible/2)
        paginas_finales = paginator.num_pages - num_pages_visible

        link_anterior = 1
        link_siguiente = vacancies.paginator.num_pages
        if vacancies.paginator.num_pages > maximo_paginas + 4:
            link_siguiente = maximo_paginas + 4

        if 1 < minimo_paginas - 4:
            link_anterior = minimo_paginas - 4

    del_filters = request.session.get('del_filters')

    return render(request,template_name,
                              {'isIndex': isIndex,
                               'latest_vacancies': latest_vacancies,
                               'isSearchVacancies': isSearchVacancies,
                               'form': form,
                               'packages': packages,
                               'service_categories': service_categories,
                               'form_contact':form_contact,
                               'postulates': postulates,
                               'vacancy_favs_ids': vacancy_favs_ids,
                               'del_filters': del_filters,
                               'search_industry': search_industry,
                               'search_area': search_area,
                               'search_state': search_state,
                               'search_employment_type': search_employment_type,
                               'vacancies': vacancies,
                               'total_vacancies': total_vacancies,
                               'maximo_paginas':maximo_paginas,
                               'minimo_paginas':minimo_paginas,
                               'link_siguiente': link_siguiente,
                               'link_anterior': link_anterior,
                               'num_pages_visible':num_pages_visible,
                               'paginas_finales':paginas_finales,
                               'industries': request.session.get('industries'),
                               'states': request.session.get('states'),
                               'pub_dates': request.session.get('pub_dates'),
                               'employment_types': request.session.get('employment_types'),
                               'vacancies_search_state': request.session.get('vacancies_search_state'),
                               'vacancies_search_industry': request.session.get('vacancies_search_industry'),
                               'vacancies_search_employment_type': request.session.get('vacancies_search_employment_type'),
                               'vacancies_search_pub_date_days': request.session.get('vacancies_search_pub_date_days'),
                               }) 

@csrf_exempt
def vacancy_details(request, vacancy_id=None, referer = None, external_referer = None, social_code=None):
    """
    Handles the display and interaction logic for a specific job vacancy page.

    This view is responsible for:
    - Authenticating and authorizing access for recruiters, candidates, and anonymous users.
    - Managing social login and application flows through social networks.
    - Handling GET/POST requests related to:
        * Submitting questions about the vacancy.
        * Applying publicly to the vacancy.
        * Uploading files (photo or CV) for social applicants.
        * Posting the vacancy to social networks.
    - Loading context data for the vacancy details page including:
        * Vacancy metadata, files, and custom application forms.
        * Social sharing configuration and tokens.
        * Recruiter/candidate-specific views.
        * Referral tracking from recruiters or external referrers.

    Parameters:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int, optional): ID of the vacancy to fetch details for.
        referer (str, optional): Encoded recruiter referral identifier.
        external_referer (str, optional): Encoded external referral identifier.
        social_code (str, optional): Identifier for social network authentication (e.g., 'fb', 'li', 'tw').

    Returns:
        HttpResponse: Renders the vacancy detail template or redirects as needed for social auth, access errors,
                      completed applications, or invalid references.

    Raises:
        Http404: If the vacancy does not exist or access is unauthorized.
    """
    error_message = _('The job opening you are trying to find does not exist or has ended')
    redirect_type = None
    socialUser = None
    templated_form = None
    review=None
    today = date.today()
    postulate = False
    form_question = None
    my_vacancy = None
    fill_template = None
    is_favorite = None
    subdomain_data = subdomain(request)
    # if not subdomain_data['active_host'] and not social_code:
    #     raise Http404
    context = {}
    context['success'] = False
    # global recruiter
    recruiter = None
    if request.user.is_authenticated:
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        except:
            recruiter = None
    # raise ValueError()
    # if social_code and not social_code in settings.social_application_list or social_code and request.user.is_authenticated() and not :
    #     raise Http404
    if not recruiter:
        if request.user.is_authenticated and social_code or request.user.is_anonymous and social_code and not social_code in settings.social_application_list:
            raise Http404
    callback_url = None
    if vacancy_id:
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except:
            raise Http404
        # try:
        user = request.user
        if recruiter:
            if user == vacancy.user or vacancy.company in recruiter.company.all():
                my_vacancy = True
        # if not my_vacancy and not vacancy in Vacancy.publishedjobs.all():
        #     messages.error(request, error_message)
        #     raise Http404


        if social_code and not recruiter:
            socialUser = request.session.get('socialUser')
            review = request.session.get('review')
            if request.method == 'POST' and request.session.get('active_applicant'):
                socialUser = request.session.get('active_applicant')
            if not socialUser:
                request.session['active_applicant'] = ""
                return redirect('social_login', social_code=social_code, vacancy_id=vacancy_id)
            request.session['active_applicant'] = socialUser

            # raise ValueError(request.COOKIES)
            #get user access token
            #request information
            socialUser = SocialAuth.objects.filter(id = socialUser)
            if not socialUser:
                raise Http404
            socialUser = socialUser[0]  
            if request.method == 'POST':
                if request.POST.get('isimage'):
                    from common.forms import UserPhotoForm
                    photoForm = UserPhotoForm(instance= socialUser.user, data=request.POST,files=request.FILES)
                    if photoForm.is_valid():
                        photoForm.save()
                        messages.success(request,"Successfully updated photo")
                    else:
                        for error in photoForm.errors['photo']:
                            messages.error(request, error)
                elif request.POST.get('isfile'):
                    from candidates.forms import cv_FileForm
                    curriculum = Curriculum.objects.get(candidate = socialUser.user.candidate)
                    fileForm = cv_FileForm(instance = curriculum, data = request.POST, files = request.FILES)
                    if request.POST.get('del-actual-cv') == '1':
                        curriculum.file = None
                        curriculum.save()
                    elif not request.FILES:
                        messages.error(request, 'No file to update')
                    elif fileForm.is_valid():

                        fileForm.save()
                    else:
                        for error in fileForm.errors['file']:
                            messages.error(request,error)
                elif request.POST.get('proceed'):
                    # Applying via social user
                    candidate = socialUser.user.candidate
                    first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
                    new_cv_public, created = Postulate.objects.get_or_create(vacancy=vacancy, candidate = candidate)
                    if not created:
                        messages.error(request,'You have aleady applied for this position previously')
                    else:
                        new_cv_public.vacancy_stage = first_stage
                        new_cv_public.save()
                        request.session['socialApplication'] = True
                        request.session.pop('socialUser')
                        request.session.pop('review')
                        request.session.pop('active_applicant')
                        return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)                    

        elif social_code and recruiter:
            socialUser = SocialAuth.objects.filter(user = recruiter.user, social_code = social_code)
            if not socialUser or request.GET.get('reauth') == 'True':
                return redirect('social_login',social_code=social_code, vacancy_id=vacancy_id, recruiter_id=recruiter.id)
            socialUser = socialUser[0]
            debug_data = debug_token(socialUser.oauth_token,socialUser.social_code)
            if socialUser.social_code == 'fb':
                if 'data' not in debug_data or 'data' in debug_data and 'error' in debug_data['data']:
                    return redirect('social_login',social_code=social_code, vacancy_id=vacancy_id, recruiter_id=recruiter.id)
            elif socialUser.social_code == 'li':
                if 'id' not in debug_data:
                    return redirect('social_login',social_code=social_code, vacancy_id=vacancy_id, recruiter_id=recruiter.id)
            elif socialUser.social_code == 'tw':
                if 'id' not in debug_data:
                    return redirect('social_login',social_code=social_code, vacancy_id=vacancy_id, recruiter_id=recruiter.id)
            return redirect('vacancies_get_vacancy_details',vacancy_id=vacancy_id)

        user_profile = None
        if recruiter:
            myreferal = 'ref-' + referer_hash.encode(recruiter.id)
        else:
            myreferal = None
        if recruiter:
            if referer or external_referer:
                return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)
        else:
            if referer:
                # Find referer
                referer_id = referer_hash.decode(referer)
                if referer_id:
                    try:
                        referer = Recruiter.objects.get(id = referer_id[0], company = vacancy.company)
                    except:
                        return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)
                else:
                    return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)
            elif external_referer:
                # Find External referer
                external_referer_id =external_referer_hash.decode(external_referer)
                if external_referer_id:
                    try:
                        external_referer = ExternalReferal.objects.get(id=external_referer_id[0])
                        if not external_referer.company == vacancy.company and not external_referer.company == None:
                            raise Exception()
                    except:
                        return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)
                else:
                    return redirect('vacancies_get_vacancy_details', vacancy_id = vacancy_id)
            else:
                cookie = request.COOKIES.get('referer-'+ str(vacancy.id))
                if cookie:
                    try:
                        referer = Recruiter.objects.get(id = int(cookie))
                    except:
                        referer = None
                if not referer:
                    cookie = request.COOKIES.get('exreferer-' + str(vacancy.id))
                    if cookie:
                        try:
                            external_referer = ExternalReferal.objects.get(id=external_referer_id[0], company = vacancy.company)
                        except:
                            external_referer = None
        if user.is_authenticated:
            user_profile = user.profile.codename
            if user_profile == 'candidate':
                # Obtain info that has to do with relation Vacancy/Candidate
                candidate = get_object_or_404(Candidate, user=request.user)
                try:
                    postulate = Postulate.objects.get(candidate=candidate, vacancy=vacancy)
                except Postulate.DoesNotExist:
                    pass
                try:
                    is_favorite = Candidate_Fav.objects.get(candidate=candidate, vacancy=vacancy)
                except Candidate_Fav.DoesNotExist:
                    pass
        if user.is_anonymous or user_profile == 'candidate':
            # If a candidate or an anonymous user, increases seen counter
            vacancy.seen += 1
            vacancy.save()
        files = Vacancy_Files.objects.filter(vacancy=vacancy)
        questions = Question.objects.filter(vacancy=vacancy)
        # Shows and validates the form to send qestions if the job allows them
        if vacancy.questions and user.is_authenticated and user.profile.codename == 'candidate':
            if request.method == 'POST':
                form_question = QuestionVacancyForm(data=request.POST)
                if form_question.is_valid():
                    # The question is created, notification sent to company
                    candidate = get_object_or_404(Candidate, user=request.user)
                    question = request.POST.get('question')
                    form_question.save(vacancy=vacancy, user=user, question=question)

                    context_email = {
                        'question': question,
                        'candidate': candidate,
                        'vacancy': vacancy,
                        'vacancy_new_question':True,
                    }

                    subject_template_name = 'mails/question_vacancy_email_subject.html',
                    email_template_name = 'mails/question_vacancy_email.html',
                    send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=vacancy.email)
                    url = '%s#questions' % reverse('vacancies_get_vacancy_details',args=[vacancy.pk])
                    return redirect(url)
            else:
                form_question = QuestionVacancyForm()
        # Public Application
        if user.is_anonymous or recruiter:
            if request.method == 'POST' and not request.session.get('active_applicant') and not request.POST.get('socialshare'):
                save_response = save_public_application(request, vacancy, recruiter, referer, external_referer, array=True)
                public_form = save_response[0]
                # if save_response[1] and vacancy.form_template and vacancy.company.check_service('JM_CUSTOM_APPLICATION_FORM'):
                if save_response[1] and vacancy.form_template:
                    required = False
                    for field in vacancy.form_template.field_set.all():
                        required|=field.is_required
                    if required:
                        request.session['fill_template'] = vacancy.id
                    request.session['applicant'] = save_response[2].id
                    fill_template = vacancy.id
                if is_ajax(request):
                    return JsonResponse(context)
            else:
                public_form = Public_Files_OnlyForm()
        else:
            public_form = Public_Files_OnlyForm()
        # Application Form End Post
        # except Http404:
        #     raise Http404
        # except Exception as ex:
        #     template = "An exception of type {0} occured. Arguments:\n{1!r}"
        #     message = template.format(type(ex).__name__, ex.args)
        #     print message
        #     tb = traceback.format_exc()
        #     print(tb)
        #     messages.error(request, error_message)
        #     return redirect('TRM-Subindex')
    else:
        messages.error(request, error_message)
        return redirect('TRM-Subindex')
    # To indicate whether a question was raised in the vacancy
    question_published = None
    if request.method == 'GET' and 'q' in request.GET:
        question_published = True
    # try:
    #     company = Company.objects.get(user=request.user)
    # except:
    #     company = None
    stages = VacancyStage.objects.filter(vacancy=vacancy)
    stageids=[]
    for stage in stages:
        stageids.append(stage.stage.id)
    allstages = Stage.objects.filter(company=vacancy.company).exclude(id__in=stageids)
    notice_period = get_notice_period()
    vacancy.notice_period = notice_period[int(vacancy.notice_period)]
    import ast
    if review:
        review = ast.literal_eval(review)

    og = {}
    og['title'] = str(vacancy.employment) + ' - ' + str(vacancy.function)
    og['description'] = str(strip_tags(vacancy.description))
    og['image'] = str(vacancy.company.logo.url)
    og['url'] = str(vacancy.company.geturl()).replace('http://','').replace('https://','')
    recruiter_social_profile = recruiter
    if recruiter:
        recruiter_social_profile.listatus = 0
        recruiter_social_profile.fbstatus = 0
        recruiter_social_profile.twstatus = 0
        from utils import posttofbprofile, posttofbgroup, posttofbpage, posttoliprofile, posttolicompany, posttotwitter
        recruiter_social = recruiter.user.socialauth_set.all()
        if request.method == 'POST' and request.POST.get('socialshare'):
            message = request.POST.get('message')
            link = request.build_absolute_uri()
            success_message_prefix = "Posted to: "
            success_message = ""
            error_message_prefix = "Posting failed for: "
            error_message = ""
            social_count = {
                'fb': {
                    'profile': {
                        'success': 0,
                        'error': 0,
                    },
                    'group': {
                        'success': 0,
                        'error': 0,
                    },
                    'page': {
                        'success': 0,
                        'error': 0,
                    }
                },
                'li': {
                    'profile': {
                        'success': 0,
                        'error': 0,
                    },
                    'company': {
                        'success': 0,
                        'error': 0,
                    },
                },
                'tw': {
                    'profile': {
                        'success': 0,
                        'error': 0,
                    },
                },
            }
            if len(request.POST)<3 or len(request.POST)==3 and message:
                messages.error(request, 'Please select at least one media to post')
            else:
                fbfail = False
                lifail = False
                twfail = False
                for key,value in list(request.POST.items()):
                    if not fbfail and key.startswith('fb'):
                        fbtoken = recruiter_social.filter(social_code = 'fb')
                        if fbtoken:
                            fbtoken = fbtoken[0]
                            if key == 'fbpersonal':
                                post_response = posttofbprofile(fbtoken,message,link)
                                if post_response.status_code == 200:
                                    social_count['fb']['profile']['success'] += 1
                                else:
                                    social_count['fb']['profile']['error'] += 1
                            elif key.startswith('fbgroup'):
                                key = key.replace('fbgroup-','')
                                post_response = posttofbgroup(fbtoken, key, message, link)

                                if post_response.status_code == 200:
                                    social_count['fb']['group']['success'] += 1
                                else:
                                    social_count['fb']['group']['error'] += 1
                            elif key.startswith('fbpage'):
                                key = key.replace('fbpage-','')
                                post_response = posttofbpage(fbtoken, key, message, link)
                                if post_response.status_code == 200:
                                    social_count['fb']['page']['success'] += 1
                                else:
                                    social_count['fb']['page']['error'] += 1
                        else:
                            fbfail = True
                            messages.error(request, 'Failed to authenticate with your Facebook Account. Reauthorisation may be required.')
                    elif not lifail and key.startswith('li'):
                        litoken = recruiter_social.filter(social_code = 'li')
                        if litoken:
                            litoken = litoken[0]
                            if key == 'lipersonal':
                                post_response = posttoliprofile(litoken,message,og)
                                if post_response.status_code == 201:
                                    social_count['li']['profile']['success'] += 1
                                else:
                                    messages.error(request,str(post_response.content))
                                    social_count['li']['profile']['error'] += 1
                            elif key.startswith('licompany'):
                                key = key.replace('licompany-','')
                                post_response = posttolicompany(litoken, key, message, og)
                                if post_response.status_code == 201:
                                    social_count['li']['company']['success'] +=1
                                else:
                                    social_count['li']['company']['error'] += 1
                        else:
                            litoken = True
                            messages.error(request, 'Failed to authenticate with your Linkedin Account. Reauthorisation may be required.')
                    elif not twfail and key.startswith('tw'):
                        twtoken = recruiter_social.filter(social_code = 'tw')
                        if twtoken:
                            twtoken = twtoken[0]
                            if key == 'twpersonal':
                                post_response = posttotwitter(twtoken, message, link)
                                if post_response.status_code == 200:
                                    social_count['tw']['profile']['success'] += 1
                                else:
                                    social_count['tw']['profile']['error'] += 1
                        else:
                            twtoken = True
                            messages.error(request, 'Failed to authenticate with your Twitter Account. Reauthorisation may be required.')

                if social_count['fb']['profile']['success'] > 0:
                    success_message = "Facebook Wall, "
                if social_count['fb']['group']['success'] > 0:
                    success_message += str(social_count['fb']['group']['success']) + " Facebook Groups, "
                if social_count['fb']['page']['success'] > 0:
                    success_message += str(social_count['fb']['page']['success']) + " Facebook Pages, "
                if social_count['li']['profile']['success'] > 0:
                    success_message += "Linkedin Stream, "
                if social_count['tw']['profile']['success'] > 0:
                    success_message += "Twitter, "
                if social_count['li']['company']['success'] > 0:
                    success_message += str(social_count['li']['company']['success']) + "Linkedin Company Pages, "
                if social_count['fb']['profile']['error'] > 0:
                    error_message = "Facebook Wall, "
                if social_count['fb']['group']['error'] > 0:
                    error_message += str(social_count['fb']['group']['error']) + " Facebook Groups, "
                if social_count['fb']['page']['error'] > 0:
                    error_message += str(social_count['fb']['page']['error']) + " Facebook Pages, "
                if social_count['li']['profile']['error'] > 0:
                    error_message += "Linkedin Stream, "
                if social_count['li']['company']['error'] > 0:
                    error_message += str(social_count['li']['company']['error']) + "Linkedin Company Pages, "
                if social_count['tw']['profile']['error'] > 0:
                    error_message += "Twitter, "
                if success_message:
                    messages.success(request,success_message_prefix + success_message.strip(', '))
                if error_message:
                    messages.error(request,error_message_prefix + error_message.strip(', '))

        # for profile in recruiter_social.all():
        #     print(profile)
        #     debug_data = debug_token(profile.oauth_token,profile.social_code)
        #     if profile.social_code == 'fb':
        #         if debug_data.has_key('data') and not debug_data['data'].has_key('error'):
        #             recruiter_social_profile.fbstatus = 2
        #             if 'user_managed_groups' in debug_data['data']['scopes']:
        #                 recruiter_social_profile.fbgroups = get_fb_user_groups(request.user)['data']
        #             else:
        #                 recruiter_social_profile.fbgroups = "Not permitted"
        #             if 'manage_pages' in debug_data['data']['scopes'] and 'publish_pages' in debug_data['data']['scopes']:
        #                 recruiter_social_profile.fbpages = get_fb_user_pages(request.user)['data']
        #             else:
        #                 recruiter_social_profile.fbpages = "Not permitted"
        #             request.session['fbpages'] = json.dumps(recruiter_social_profile.fbpages)
        #             request.session['fbgroups'] = json.dumps(recruiter_social_profile.fbgroups)
        #         else:
        #             recruiter_social_profile.fbstatus = 1
        #     elif profile.social_code == 'li':
        #         if debug_data.has_key('id'):
        #             recruiter_social_profile.listatus = 2
        #             recruiter_social_profile.licompanies = get_li_companies(request.user)['values']
        #             request.session['licompanies'] = json.dumps(recruiter_social_profile.licompanies)
        #         else:
        #             recruiter_social_profile.listatus = 1
        #     elif profile.social_code == 'tw':
        #         if debug_data.has_key('id'):
        #             recruiter_social_profile.twstatus = 2
        #         else:
        #             recruiter_social_profile.twstatus = 1
        # raise ValueError(debug_data)
    socialApplication = request.session.pop('socialApplication', False)
    if request.session.get('fill_template', 0) == vacancy.id or fill_template == vacancy.id:
        # if vacancy.form_template and vacancy.company.check_service('JM_CUSTOM_APPLICATION_FORM'):
        if vacancy.form_template and vacancy.form_template.has_required_fields():
            templated_form = TemplatedForm(template = vacancy.form_template, formClasses="form-control mt2")
        else:
            request.session.pop('fill_template')
    popshare = request.session.pop('enableshare', None)
    response = render(request,'vacancy_details.html',
                              {'isSearchVacancies': True,
                               'og': og,
                               'vacancy': vacancy,
                               'recruiter_social_profile':recruiter_social_profile,
                               'objFiles': files,
                               'is_favorite': is_favorite,
                               'my_vacancy': my_vacancy,
                               'questions': questions,
                               'postulate': postulate,
                               'referer': referer,
                               'external_referer': external_referer,
                               'myreferal': myreferal,
                               'today': today,
                               'stages': stages,
                               'allstages': allstages,
                               'question_published': question_published,
                               'form_question': form_question,
                               'public_form': public_form,
                               'socialUser': socialUser,
                               'reviews':review,
                               'social_code': social_code,
                               'socialApplication': socialApplication,
                               'fill_template': fill_template,
                               'templated_form': templated_form,
                               'talent_only': True,
                               'popshare': popshare,
                               }
                     )
    if referer:
        response.set_cookie('referer-'+str(vacancy.id),str(referer.id))
    if external_referer:
        response.set_cookie('exreferer-'+str(vacancy.id),str(external_referer.id))
    return response


# @login_required
def vacancy_stage_details(request, vacancy_id=None, vacancy_stage=None, stage_section=0):
    """
    View that displays detailed information about candidates in a specific stage of a vacancy.
    - Checks if the subdomain and recruiter are valid.
    - Verifies if the authenticated user has access to the vacancy.
    - Displays candidate lists segmented by stage section:
        - Section 0: Candidates in the current stage.
        - Section 1: Candidates who have passed this stage.
        - Section 2: Discarded candidates.
    - Includes recruiter rating, comments, and interview schedule data per candidate.
    - Gathers additional data like form questions, counts per section, available stages, etc.
    Args:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int, optional): The primary key of the vacancy.
        vacancy_stage (int or str, optional): The order of the stage in the pipeline.
        stage_section (int, optional): Section filter (0=current, 1=next/finalized, 2=discarded).

    Returns:
        HttpResponse: Rendered HTML response for the vacancy stage details view.
    """
    error_message = _('The job opening you are trying to find does not exist or has ended')
    today = date.today()
    postulate = False
    form_question = None
    my_vacancy = None
    is_favorite = None
    context = {}
    context['success'] = False
    subdomain_data = subdomain(request)
    if not subdomain_data['active_subdomain']:
        raise Http404
    if request.user.is_authenticated:
        # raise ValueError()
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True, company__subdomain__slug=subdomain_data['active_subdomain'])
        except:
            raise Http404
    else:
        raise Http404
    # raise ValueError()
    if vacancy_id:
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
            user = request.user

            if user.recruiter.company.all()[0] == vacancy.company:
                my_vacancy = True

            if not my_vacancy and not vacancy in Vacancy.publishedjobs.all():
                messages.error(request, error_message)
                raise Http404

            user_profile = None

            if user.is_authenticated:
                user_profile = user.profile.codename
                       
        except Http404:
            raise Http404

        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            tb = traceback.format_exc()
            print(tb)
            messages.error(request, error_message)
            return redirect('TRM-Subindex')

    else:
        messages.error(request, error_message)
        return redirect('TRM-Subindex')

    # Public Application
    if recruiter:
        if request.method == 'POST':
            public_form = save_public_application(request, vacancy, recruiter)
            if is_ajax(request):
                return JsonResponse(context)
        else:
            public_form = Public_Files_OnlyForm()
    else:
        public_form = Public_Files_OnlyForm()
    finalize=False
    if not stage_section==0 or not stage_section ==1 or not stage_section ==2:
        stage_section == 0
    if vacancy_stage and vacancy_stage!='100':
        # print('vacancy_stage')
        # print(vacancy_stage)
        # print(vacancy)
        vacancystage = get_object_or_404(VacancyStage, vacancy = vacancy,order = int(vacancy_stage))
        # print(vacancystage.id)
        if stage_section == '1':
            candidates = Postulate.objects.filter(Q(vacancy=vacancy), Q(finalize=True)|Q(vacancy_stage__order__gt=vacancy_stage))
            # public_candidates = Public_Postulate.objects.filter(Q(vacancy=vacancy), Q(finalize=True)|Q(vacancy_stage__order__gt=vacancy_stage))
        elif stage_section =='2':
            candidates = vacancystage.postulate_set.all().filter(vacancy=vacancy,discard=True)
            # public_candidates = vacancystage.public_postulate_set.all().filter(vacancy=vacancy, discard = True)
        else:
            candidates = vacancystage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True)
            # public_candidates = vacancystage.public_postulate_set.all().filter(vacancy = vacancy).exclude(discard=True)
        section0_count = int(vacancystage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count()) 
        section1_count = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=vacancy_stage).count()) 
        section2_count = int(vacancystage.postulate_set.all().filter(vacancy=vacancy,discard=True).count()) 
        # section0_count = int(vacancystage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count()) + int(vacancystage.public_postulate_set.all().filter(vacancy = vacancy).exclude(discard=True).count())
        # section1_count = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=vacancy_stage).count()) + int(Public_Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=vacancy_stage).count())
        # section2_count = int(vacancystage.postulate_set.all().filter(vacancy=vacancy,discard=True).count()) + int(vacancystage.public_postulate_set.all().filter(vacancy=vacancy, discard = True).count())
                # raise Http404
            # except:
                # raise Http404
            # except:
    # elif vacancy_stage == '100':  
        #     if stage_section == '1':
        #         candidates = Postulate.objects.filter(Q(vacancy = vacancy), Q(finalize=True)|~Q(vacancy_stage=None))
        #         public_candidates = Public_Postulate.objects.filter(Q(vacancy = vacancy), Q(finalize=True)|~Q(vacancy_stage=None))
        #     elif stage_section == '2':
        #         candidates = Postulate.objects.filter(vacancy = vacancy, discard=True, vacancy_stage=None)
        #         public_candidates = Public_Postulate.objects.filter(vacancy = vacancy, discard=True, vacancy_stage=None)
        #         # raise ValueError()
        #     else:
        #         candidates = Postulate.objects.filter(Q(vacancy = vacancy), vacancy_stage=None, finalize=False).exclude(discard = True)
        #         public_candidates = Public_Postulate.objects.filter(Q(vacancy = vacancy), vacancy_stage=None, finalize=False).exclude(discard=True)
        #     section0_count = int(Postulate.objects.filter(Q(vacancy = vacancy), vacancy_stage=None, finalize=False).exclude(discard = True).count()) + int(Public_Postulate.objects.filter(Q(vacancy = vacancy), vacancy_stage=None, finalize=False).exclude(discard=True).count())
        #     section1_count = int(Postulate.objects.filter(Q(vacancy = vacancy), Q(finalize=True)|~Q(vacancy_stage=None)).count()) + int(Public_Postulate.objects.filter(Q(vacancy = vacancy), Q(finalize=True)|~Q(vacancy_stage=None)).count())
        #     section2_count = int(Postulate.objects.filter(Q(vacancy = vacancy), discard=True, finalize=False, vacancy_stage=None).count()) + int(Public_Postulate.objects.filter(Q(vacancy = vacancy), discard=True, finalize=False, vacancy_stage=None).count())
    else:
        section0_count = None
        section1_count = None
        section2_count = None
        candidates=None
        public_candidates = None
        finalize=True
        candidates = Postulate.objects.filter(vacancy = vacancy, finalize=True, discard = False)
        # public_candidates = Public_Postulate.objects.filter(vacancy = vacancy, finalize=True, discard = False)

    # To indicate whether a question was raised in the vacancy
    question_published = None
    if request.method == 'GET' and 'q' in request.GET:
        question_published = True
    try:
        company = Company.objects.get(user=request.user)
    except:
        company = None
    stages = VacancyStage.objects.filter(vacancy=vacancy)
    for stage in stages:
        # count0 = int(stage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count()) + int(stage.public_postulate_set.all().filter(vacancy = vacancy).exclude(discard=True).count())
        # count1 = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count()) + int(Public_Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count())
        # count2 = int(stage.postulate_set.all().filter(vacancy=vacancy,discard=True).count()) + int(stage.public_postulate_set.all().filter(vacancy=vacancy, discard = True).count())
        # count3 = int(Postulate.objects.filter(vacancy=vacancy,finalize=True).count()) + int(Public_Postulate.objects.filter(vacancy=vacancy,finalize=True).count())
        count0 = int(stage.postulate_set.all().filter(vacancy =vacancy).exclude(discard=True).count())
        count1 = int(Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count())
        count2 = int(stage.postulate_set.all().filter(vacancy=vacancy,discard=True).count())
        count3 = int(Postulate.objects.filter(vacancy=vacancy,finalize=True).count())
        stage.total_count = count0 + count1 + count2
    finalized_count = Postulate.objects.filter(vacancy=vacancy, finalize = True).count()
    stageids=[]
    for stage in stages:
        stageids.append(stage.stage.id)
    allstages = Stage.objects.filter(company=vacancy.company).exclude(id__in=stageids)
    try: 
        process = VacancyStage.objects.get(vacancy = vacancy, order = vacancy_stage)
        
    except:
        process = None
    for candidate in candidates:
        candidate.process,created = Postulate_Stage.objects.get_or_create(postulate=candidate, vacancy_stage=process)
        candidate.processes = candidate.postulate_stage_set.all()
        candidate.comments = candidate.comment_set.all().filter(comment_type__lt=2)
        candidate.timeline = candidate.comment_set.all().filter(comment_type__gte=2)
        rated = candidate.process.scores.all().filter(recruiter=recruiter)
        if rated:
            candidate.hasRated = True
        else:
            candidate.hasRated = False
        if candidate.hasRated:
            candidate.comment = rated[0].get_comment
        else:
            candidate.comment=None
    for candidate in candidates:
         candidate.schedule = candidate.schedule_set.filter(user=request.user,status=0)
         if candidate.schedule:
            candidate.schedule = candidate.schedule[0]
    # for candidate in public_candidates:
        #     candidate.process,created = Public_Postulate_Stage.objects.get_or_create(postulate=candidate, vacancy_stage=process)
        #     candidate.processes = candidate.public_postulate_stage_set.all()
        #     candidate.comments = candidate.comment_set.all().filter(comment_type__lt=2)
        #     candidate.timeline = candidate.comment_set.all().filter(comment_type__gte=2)
        #     rated = candidate.process.scores.all().filter(recruiter=recruiter)
        #     if rated:
        #         candidate.hasRated = True
        #     else:
        #         candidate.hasRated = False
        #     if candidate.hasRated:
        #         candidate.comment = rated[0].get_comment
        #     else:
        #         candidate.comment=None
    if process and request.user.recruiter in process.recruiters.all():
        isProcessMember = True
    else:
        isProcessMember = False


    # vacancies = Vacancy.objects.filter(company = company)
    # for vacancy in vacancies:
    #     vacancy.stages = VacancyStage.objects.filter(vacancy=vacancy)
    return render(request,'vacancies_stage_details.html',
                              {'isSearchVacancies': True,
                               'vacancy': vacancy,
                               'public_form': public_form,
                               'is_favorite': is_favorite,
                               'my_vacancy': my_vacancy,
                               'isProcessMember': isProcessMember,
                               'postulate': postulate,
                               'allstages': allstages,
                               'current_process': process,
                               'candidates': candidates,
                               'finalize_count': finalized_count,
                               # 'public_candidates': public_candidates,
                               'today': today,
                               'finalize': finalize,
                               'stages': stages,
                               'section0_count': section0_count,
                               'section1_count': section1_count,
                               'section2_count': section2_count,
                               'question_published': question_published,
                               'form_question': form_question,
                               'company': company,
                               'vacancy_stage': vacancy_stage,
                               'stage_section': str(stage_section)})
                               # 'vacancies': vacancies},
                               # 'public_form': public_form})
                            

def vacancy_to_pdf(request, vacancy_id):
    """
    Generates a PDF version of the vacancy details.

    - Validates user ownership to determine if it's their vacancy.
    - Renders a template with company logo and media info into a PDF.

    Args:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int): The ID of the vacancy to generate the PDF for.

    Returns:
        HttpResponse: A PDF file download response.
    """
    from TRM.settings import MEDIA_URL
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
    logo_pdf = 'logos_TRM/logo_pdf.png'
    user = request.user
    # user_profile = None
    my_vacancy = False
    if user.is_authenticated():
        if request.user == vacancy.user:
            my_vacancy = True

    pdf_name = '%s_%s.pdf' % (vacancy.employment[:30].replace(' ', '_'), vacancy.pk)
    html_string = render_to_string('vacancy_details_pdf.html',
                                    context={'vacancy': vacancy,
                                             'MEDIA_URL': MEDIA_URL,
                                             'logo_pdf': logo_pdf,
                                             'my_vacancy': my_vacancy,
                                             'LOGO_COMPANY_DEFAULT': LOGO_COMPANY_DEFAULT,
                                             })

    # Create PDF response using WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % pdf_name
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
    return response


def vacancies_by_company(request, company_id):
    """
    Displays all published vacancies for a given company.

    - Paginates the result set.
    - Adjusts pagination display controls (next, previous, max/min pages).
    - Loads the company and its user.

    Args:
        request (HttpRequest): The HTTP request object.
        company_id (int): The ID of the company whose vacancies are being shown.

    Returns:
        HttpResponse: Rendered HTML page listing all active non-confidential vacancies.
    """
    total_vacancies = 0
    company = get_object_or_404(Company, pk=company_id)
    vacancies = Vacancy.publishedjobs.filter(company=company, confidential=False)
    company_user = get_object_or_404(User, pk=company.user.pk)
    # Pagination
    if vacancies:
        total_vacancies = vacancies.count()
    link_anterior = 1
    link_siguiente = 1
    maximo_paginas = 1
    minimo_paginas = 0
    num_pages_visible = num_pages
    paginas_finales = 0
    paginator = Paginator(vacancies, number_objects_page)
    page = request.GET.get('page')
    try:
        vacancies = paginator.page(page)
    except PageNotAnInteger:
        vacancies = paginator.page(1)
    except EmptyPage:
        vacancies = paginator.page(paginator.num_pages)

    if vacancies.paginator.num_pages > num_pages_visible:
        if vacancies.number <= num_pages_visible/2:
            maximo_paginas = num_pages_visible
            minimo_paginas = 1
        elif vacancies.number > vacancies.paginator.num_pages - (num_pages_visible/2):
            maximo_paginas = vacancies.paginator.num_pages
            minimo_paginas = vacancies.paginator.num_pages - num_pages_visible
        else:
            minimo_paginas = vacancies.number - (num_pages_visible/2)
            maximo_paginas = vacancies.number + (num_pages_visible/2)
    paginas_finales = paginator.num_pages - num_pages_visible

    link_anterior = 1
    link_siguiente = vacancies.paginator.num_pages
    if vacancies.paginator.num_pages > maximo_paginas + 4:
        link_siguiente = maximo_paginas + 4

    if 1 < minimo_paginas - 4:
        link_anterior = minimo_paginas - 4

    return render(request,'vacancies_by_company.html',
                              {'company': company,
                               'company_user': company_user,
                               'vacancies': vacancies,
                               'total_vacancies': total_vacancies,
                               'maximo_paginas':maximo_paginas,
                               'minimo_paginas':minimo_paginas,
                               'link_siguiente': link_siguiente,
                               'link_anterior': link_anterior,
                               'num_pages_visible':num_pages_visible,
                               'paginas_finales':paginas_finales,
                               })
                         

def create_vacancies(request):
    """
    Generates multiple random vacancies across different states and industries for Mexico.

    - Loops through Mexican states and selects random municipalities.
    - Chooses a random company, area, and other properties.
    - Randomly fills vacancy fields such as salary, age, and experience.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        None
    """
    import random
    industries = Industry.objects.all()
    country_mex = Country.objects.get(iso2_code__exact='MX')
    states = State.objects.filter(country=country_mex)  # Id 142 Mexico
    for state in states:
        # Select a random City
        for x in range(1, 3):
            municipal = Municipal.objects.filter(state_id=state).order_by('?')[:1]
            municipal = municipal.first()
            for industry in industries:
                # Select a random area
                area = Area.objects.filter(industry_id=industry).order_by('?')[:1]
                area = area.first()
                company = Company.objects.all().order_by('?')[:1]
                company = company.first()
                pub_date = (date.today() - timedelta(days=1)) - timedelta(days=random.randint(0, 30))
                hiring_date = (date.today() - timedelta(days=1)) - timedelta(days=random.randint(0, 30))
                salary_type = Salary_Type.objects.get(pk=random.randint(1, 6))
                if salary_type.codename == 'fixed':
                    min_salary = random.randint(8000, 14000)
                    max_salary = random.randint(16000, 50000)
                else:
                    min_salary = None
                    max_salary = None
                new_vacancy = Vacancy.objects.create(
                    company=company,
                    user=company.user,
                    status=get_vacancy_active_status(),
                    employment='%s solicits personal' % company.name,
                    description='This job opening was generated automatically This job opening was generated automatically '
                                'This job opening was generated automatically This job opening was generated automatically '
                                'This job opening was generated automatically This job opening was generated automatically ',
                    state=state,
                    municipal=municipal,
                    industry=industry,
                    area=area,
                    gender=Gender.objects.get(pk=random.randint(1, 3)),
                    employmentType=Employment_Type.objects.get(pk=random.randint(2, 7)),
                    employmentExperience=Employment_Experience.objects.get(pk=random.randint(1, 7)),
                    degree=Degree.objects.get(pk=random.randint(1, 10)),
                    min_age=random.randint(18, 25),
                    max_age=random.randint(26, 64),
                    vacancies_number=random.randint(1, 10),
                    salaryType=salary_type,
                    min_salary=min_salary,
                    max_salary=max_salary,
                    seen=0,
                    postulate=random.choice([True, False]),
                    applications=0,
                    confidential=random.choice([True, False]),
                    questions=random.choice([True,False]),
                    pub_after=False,
                    pub_date=pub_date,
                    hiring_date=hiring_date,
                    editing_date=pub_date + timedelta(days=5),
                    end_date=pub_date + timedelta(30),
                    email='contact.travelder@gmail.com'
                )
                new_vacancy.employment = str(new_vacancy.id) + " - " + new_vacancy.employment
                if new_vacancy.confidential:
                    new_vacancy.data_contact = False
                else:
                    new_vacancy.data_contact = random.choice([True, False])
                new_vacancy.save()
    return redirect('TRM-Subindex')

def public_apply(request, vacancy_id = None, referer = None, external_referer=None):
    """
    Handles the public job application process for a given vacancy.

    This view renders a public application form for anonymous users or non-logged-in candidates.
    It supports application tracking via recruiter or external referer hashes.
    If a valid application is submitted, the candidate's profile and curriculum are saved,
    and appropriate tracking (referer, recruiter, etc.) is recorded.

    Args:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int, optional): ID of the vacancy being applied to.
        referer (str, optional): Encoded hash representing an internal recruiter referer.
        external_referer (str, optional): Encoded hash representing an external referer.

    Returns:
        HttpResponse: Rendered application form, or redirect on success/error.
    """
    error_message = _('The job opening you are trying to find does not exist or has ended')
    today = date.today()
    postulate = False
    form_question = None
    my_vacancy = None
    is_favorite = None
    subdomain_data = subdomain(request)
    if not subdomain_data['active_host']:
        raise Http404
    try:
        company = Company.objects.get(subdomain__slug = subdomain_data['active_subdomain'])
    except:
        raise Http404

    if not company.check_service('CSM_ONSITE_APPLY'):
        raise Http404
    context = {}
    context['success'] = False
    # global recruiter
    recruiter = None
    if request.user.is_authenticated:
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        except:
            recruiter = None
    if vacancy_id:
        try:
            vacancy = Vacancy.objects.get(pk=vacancy_id)
        except:
            messages.error(request, error_message)
            raise Http404
        user = request.user
        if not vacancy.public_cvs and not vacancy.postulate:
            messages.error(request, error_message)
            raise Http404
        if recruiter:
            if user == vacancy.user or vacancy.company in recruiter.company.all():
                my_vacancy = True
        if not my_vacancy and not vacancy in Vacancy.publishedjobs.all():
            messages.error(request, error_message)
            raise Http404
        user_profile = None
        if recruiter:
            if referer or external_referer:
                return redirect('vacancies_public_apply', vacancy_id = vacancy_id)
        else:
            if referer:
                # Find referer
                referer_id = referer_hash.decode(referer)
                if referer_id:
                    try:
                        referer = Recruiter.objects.get(id = referer_id[0], company = vacancy.company)
                    except:
                        return redirect('vacancies_public_apply', vacancy_id = vacancy_id)
                else:
                    return redirect('vacancies_public_apply', vacancy_id = vacancy_id)
            elif external_referer:
                # Find External referer
                external_referer_id =external_referer_hash.decode(external_referer)
                if external_referer_id:
                    try:
                        external_referer = ExternalReferal.objects.get(id=external_referer_id[0])
                        if not external_referer.company == vacancy.company and not external_referer.company == None:
                            raise Exception()
                    except:
                        return redirect('vacancies_public_apply', vacancy_id = vacancy_id)
                else:
                    return redirect('vacancies_public_apply', vacancy_id = vacancy_id)
            else:
                cookie = request.COOKIES.get('referer-'+ str(vacancy.id))
                if cookie:
                    try:
                        referer = Recruiter.objects.get(id = int(cookie))
                    except:
                        referer = None
                if not referer:
                    cookie = request.COOKIES.get('exreferer-' + str(vacancy.id))
                    if cookie:
                        try:
                            external_referer = ExternalReferal.objects.get(id=external_referer_id[0], company = vacancy.company)
                        except:
                            external_referer = None
        if user.is_authenticated:
            user_profile = user.profile.codename
            if user_profile == 'candidate':
                # Obtain info that has to do with relation Vacancy/Candidate
                candidate = get_object_or_404(Candidate, user=request.user)
                try:
                    postulate = Postulate.objects.get(candidate=candidate, vacancy=vacancy)
                except Postulate.DoesNotExist:
                    pass
                try:
                    is_favorite = Candidate_Fav.objects.get(candidate=candidate, vacancy=vacancy)
                except Candidate_Fav.DoesNotExist:
                    pass
        if user.is_anonymous or user_profile == 'candidate':
            # If a candidate or an anonymous user, increases seen counter
            vacancy.seen += 1
            vacancy.save()

        files = Vacancy_Files.objects.filter(vacancy=vacancy)

        # Public Application
        if user.is_anonymous or recruiter:
            if request.method == 'POST':
                public_form = save_public_application(request, vacancy, recruiter, referer, external_referer)

                if is_ajax(request):
                    return JsonResponse(context)
            else:
                public_form = Public_Files_OnlyForm()
        else:
            public_form = Public_Files_OnlyForm()
    else:
        messages.error(request, error_message)
        return redirect('TRM-Subindex')
    response =  render(request,'job_public_apply.html',{
        'company': company,
        'vacancy': vacancy,
        'referer': referer,
        'external_referer': external_referer,
        'public_form': public_form,
        })  
    if referer:
        response.set_cookie('referer-'+str(vacancy.id),str(referer.id))
    if external_referer:
        response.set_cookie('exreferer-'+str(vacancy.id),str(external_referer.id))
    return response

def save_public_application(request,vacancy, recruiter, referer = None, external_referer=None, array = False):
    """
    Saves a public job application submitted by a user without a candidate account.

    Creates a new `Candidate`, `Curriculum`, and `Postulate` instance based on uploaded files
    and form data. Attaches referer, external referer, or recruiter if present and logs a comment.

    Args:
        request (HttpRequest): The HTTP request containing form data and uploaded files.
        vacancy (Vacancy): The vacancy object to which the application is being submitted.
        recruiter (Recruiter): Optional recruiter submitting the application on behalf of the candidate.
        referer (Recruiter, optional): Referring recruiter (internal).
        external_referer (ExternalReferal, optional): External referral source.
        array (bool, optional): If True, returns a list containing form, saved flag, and postulate.

    Returns:
        Public_FilesForm or list: The submitted form or [form, saved (bool), new_cv_public (Postulate)]
    """
    saved = False
    new_cv_public = None
    try:
        public_form = Public_FilesForm(data=request.POST, files=request.FILES, v_id = vacancy.id)
        if public_form.is_valid():
            if request.FILES:
                email = request.POST.get('email')
                old_cv_files = Postulate.objects.filter(vacancy=vacancy, candidate__public_email=email)
                if not old_cv_files:
                    full_name = request.POST.get('full_name').strip().split(' ')
                    first_name = full_name[0]
                    last_name = ' '.join(full_name[1:])
                    description = request.POST.get('description')
                    file = public_form.clean_file()
                    first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
                    candidate = Candidate.objects.create(first_name = first_name, last_name = last_name, public_email = email)
                    curriculum = Curriculum.objects.create(candidate = candidate, file = file)
                    new_cv_public = Postulate.objects.create(vacancy=vacancy, candidate = candidate, description=description, vacancy_stage=first_stage)
                    if request.session.get('referral_source'):
                        medium, created = Medium.objects.get_or_create(name=request.session.pop('referral_source'))
                        new_cv_public.medium= medium
                        new_cv_public.save()
                    if recruiter:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.recruiter = recruiter
                        new_cv_public.is_recruiter = True
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Application Added by '+ str(recruiter.user.get_full_name()))
                    elif referer:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.recruiter = referer
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Refered by '+ str(referer.user.get_full_name()))                        
                    elif external_referer:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.external_reference = external_referer
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Reference by '+ str(external_referer.name))                        
                    else:
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Application Received for the job opening')
                        # file_path = str(new_cv_public.file.path)
                        # Send Mail
                        # context_email = {
                        #     'vacancy': vacancy,
                        #     'full_name': new_cv_public.full_name,
                        #     'email': email,
                        #     'salary': new_cv_public.salary,
                        #     'age': new_cv_public.age,
                        #     'description': new_cv_public.description,
                        #     'file_path': file_path,
                        #     'public_postulate': True,
                        # }

                        # subject_template_name = 'mails/public_postulate_subject.html',
                        # email_template_name = 'mails/public_postulate_email.html',
                         # Mail to company
                        # send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=vacancy.email,file=file_path)

                        # Mail to candidate
                        # send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=email,file=file_path)
                        # public_form = Public_FilesForm()
                    if recruiter:
                        messages.success(request,'Candidate Profile added to the job opening "%s"' % vacancy.employment)
                        # context['msg'] = u'Candidate Profile added to the job opening "%s"' % vacancy.employment
                    else:
                        messages.success(request,'We have successfully submitted your profile to the job opening "%s"' % vacancy.employment)
                        # context['msg'] = u'We have successfully submitted your profile to the job opening "%s"' % vacancy.employment
                    saved = True
                else:
                    messages.error(request, 'Already Applied')
                    # context['msg'] = u'Already Applied'
        else:
            # context['errors'] = public_form.errors
            pass
    except:
        tb = traceback.format_exc()
        print(tb)
        messages.error(request,  'Failed to apply to this job opening, please try again...')
        # context['msg'] = u'Failed to apply to this job opening, please try again...'
        public_form = Public_FilesForm()
        new_cv_public = None
        saved = False
    if not array:
        return public_form
    else:
        return [public_form, saved, new_cv_public]

def extract_public_form_content(public_form):
    """
    Parses uploaded resume content from the public form and generates a minimal candidate profile.

    Utilizes a resume parsing library to extract structured information such as name, email,
    phone, skills, and education history from the uploaded file. Creates corresponding
    Candidate, Curriculum, and Academic objects in the database.

    Args:
        public_form (Public_FilesForm): The validated form containing the uploaded resume.

    Returns:
        list: A list containing the created Candidate and Curriculum instances.
    """

    from resume_parser.resume_parser import extract_file_content
    file = public_form.clean_file()
    candidate = Candidate.objects.create()
    # first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
    curriculum = Curriculum.objects.create(candidate = candidate, file = file)
    # new_cv_public = Postulate.objects.create(vacancy=vacancy, candidate = candidate, description=description, vacancy_stage=first_stage)
    # dat = read_file_content_directly(uploaded_file)
    dat = extract_file_content(curriculum.file.path, 'json')
    if isinstance(dat, str):
        dat = json.loads(dat)
    print(dat)
    if dat['name']:
        names = dat['name'][0].split(' ')
        candidate.first_name = names[0]
        try:
            candidate.save()
        except:
            pass
        if len(names) > 1:
            candidate.last_name = ' '.join(names[1:])
            try:
                candidate.save()
            except:
                pass
    if len(dat['phones']) > 0:
        candidate.phone = dat['phones'][0]
        try:
            candidate.save()
        except:
            pass
    if len(dat['emails']) > 0:
        candidate.public_email = dat['emails'][0]
        try:
            candidate.save()
        except:
            pass
    candidate.skills = ','.join(dat['skills'])
    try:
        candidate.save()
    except:
        pass
    max_i = max(len(dat['education']['education-degrees']), len(dat['education']['school-college']))
    # for i, degree in enumerate(dat['education']['education-degrees']):
    i = 0
    while i < max_i:
        try:
            degree = dat['education']['education-degrees'][i]
        except:
            degree = ""
        try:
            school = dat['education']['school-college'][i]
        except:
            school = ""
        try:
            dates = dat['education']['education-dates'][i].split('-')
        except:
            dates = None
        start_date = None
        end_date=None
        status = 'complete'
        try:
            if len(dates) > 1 :
                start_date = date(int(dates[0]),1,1)
                if not dates[1] == 'Present':
                    end_date = date(int(dates[1]),1,1)
                else:
                    status = 'progress'
            else:
                end_date = date(int(dates[0]),1,1)
        except:
            pass
        new_academic = Academic.objects.create(
                candidate = candidate,
                course_name = degree,
                status = Academic_Status.objects.get(codename=status)
            )
        new_academic.school = school
        try:
            new_academic.save()
        except:
            pass
        if start_date:
            new_academic.start_date = start_date
        if end_date:
            new_academic.end_date = end_date
        try:
            new_academic.save()
        except:
            pass
        i = i+1
    # Add work parsing
    return [candidate, curriculum]

def new_application(request, vacancy_id):
    """
    Handles a new job application process, including file upload and structured candidate input.

    This view supports both anonymous applications (with resume upload) and authenticated
    candidate profiles. It validates duplicate applications, parses resume data, and allows
    form-based editing of candidate profile, academic history, and expertise.

    Args:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int): ID of the vacancy the user is applying to.

    Returns:
        HttpResponse: A redirect on success or error, or form re-render on validation failure.
    """
    from candidates.forms import CandidateMiniForm, ExpertiseFormset, AcademicFormset
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    # Check Vacancy status
    advanced_error = False
    initial_missing = False
    sa_profile = None
    conflicts = None
    recruiter_upload = False
    fresh_application = False
    referer_path = request.POST.get('refering_page', None)
    if referer_path:
        request.session['referer'] = referer_path
        fresh_application = True
    else:
        referer_path = request.session.get('referer', None)
    if request.user.is_authenticated and request.user.profile.codename == 'recruiter' and vacancy.company in request.user.recruiter.company.all():
        recruiter_upload = True
    if request.user.is_anonymous or recruiter_upload:
        if fresh_application:
            if request.method == 'POST':
                public_form = Public_Files_OnlyForm(data=request.POST, files = request.FILES, v_id=vacancy.id)
                if public_form.is_valid():
                    candidate, curriculum = extract_public_form_content(public_form)
                    request.session['candidate'] = candidate.id
                    if candidate.public_email:
                        if Postulate.objects.filter(candidate__public_email = candidate.public_email, vacancy = vacancy) or Postulate.objects.filter(candidate__user__email = candidate.public_email, vacancy = vacancy):
                            if recruiter_upload:
                                messages.error(request,'This person has an existing application for this position.')
                            else:
                                messages.error(request,'You have already applied for this position.')
                            curriculum.delete()
                            candidate.delete()
                            try:
                                return redirect(referer_path, vacancy.id)
                            except:
                                return redirect('vacancies_get_vacancy_details', vacancy.id)
                else:
                    messages.error(request, 'Invalid upload! ' + str(public_form.errors))
                    try:
                        return redirect(referer_path, vacancy.id)
                    except:
                        return redirect('vacancies_get_vacancy_details', vacancy.id)
            else:
                raise Http404
        else:
            candidate = request.session.get('candidate', None)
            if candidate:
                try:
                    candidate = Candidate.objects.get(id = candidate)
                except:
                    candidate = None
            if not candidate:
                messages.error(request, 'Invalid upload')
                try:
                    return redirect(referer_path, vacancy.id)
                except:
                    return redirect('vacancies_get_vacancy_details', vacancy.id)
            curriculum = Curriculum.objects.get(candidate = candidate)
            if request.user.is_anonymous:
                sa_profile = Candidate.objects.filter(~Q(user=None), user__email = candidate.public_email)
    elif request.user.is_authenticated and request.user.profile.codename == 'candidate':
        candidate = request.user.candidate
        curriculum = Curriculum.objects.get(candidate=candidate)
        if Postulate.objects.filter(candidate = candidate, vacancy = vacancy) or Postulate.objects.filter(candidate__public_email = candidate.user.email, vacancy = vacancy):
            messages.error(request,'You have already applied for this position.')
            try:
                return redirect(referer_path, vacancy.id)
            except:
                return redirect('vacancies_get_vacancy_details', vacancy.id)
        old_candidate = request.session.pop('candidate', None)
        if old_candidate:
            try:
                old_candidate = Candidate.objects.get(id=old_candidate)
            except:
                old_candidate = None
            if old_candidate:
                old_candidate.parent_profile = candidate
                old_candidate.save()
    else:
        raise Http404
    if request.method == 'POST' and not fresh_application:
        candidate_form = CandidateMiniForm(instance = candidate, data=request.POST)
        expertise_forms = ExpertiseFormset(prefix="expertise", queryset=candidate.expertise_set.all(), data=request.POST)
        academic_forms = AcademicFormset(prefix="academic", queryset=candidate.academic_set.all(), data=request.POST)
        if candidate_form.is_valid():
            candidate_form.save()
            candidate.refresh_from_db()
            candidate_form = CandidateMiniForm(instance = candidate)
            if request.user.is_authenticated and not recruiter_upload and candidate.public_email:
                if Postulate.objects.filter(candidate = candidate, vacancy = vacancy) or Postulate.objects.filter(candidate__public_email = candidate.user.email, vacancy = vacancy):
                    messages.error(request,'Already applied for this position.')
                    try:
                        return redirect(referer_path, vacancy.id)
                    except:
                        return redirect('vacancies_get_vacancy_details', vacancy.id)
            else:
                if Postulate.objects.filter(candidate__public_email = candidate.public_email, vacancy = vacancy) or Postulate.objects.filter(candidate__user__email = candidate.public_email, vacancy = vacancy):
                    messages.error(request,'Already applied for this position.')
                    candidate.delete()
                    try:
                        return redirect(referer_path, vacancy.id)
                    except:
                        return redirect('vacancies_get_vacancy_details', vacancy.id)
        if expertise_forms.is_valid():
            expertises = expertise_forms.save()
            for expertise in expertises:
                expertise.candidate = candidate
                expertise.save()
            expertise_forms = ExpertiseFormset(prefix="expertise", queryset=candidate.expertise_set.all())
        else:
            for form in expertise_forms:
                if form.errors:
                    advanced_error = True
                    break
        if academic_forms.is_valid():
            # pdb.set_trace()
            academics = academic_forms.save()
            for academic in academics:
                academic.candidate = candidate
                academic.save()
            academic_forms = AcademicFormset(prefix="academic", queryset=candidate.academic_set.all())
        else:
            if not advanced_error:
                for form in academic_forms:
                    if form.errors:
                        advanced_error = True
                        break
    else:
        candidate_form = CandidateMiniForm(instance = candidate)
        expertise_forms = ExpertiseFormset(prefix="expertise", queryset=candidate.expertise_set.all())
        academic_forms = AcademicFormset(prefix="academic", queryset=candidate.academic_set.all())
    conflicts = candidate.find_conflicts()
    today = datetime.now().date()
    applicant = candidate
    if recruiter_upload:
        candidate = None
    return render(request,'new_application.html', {
            'vacancy' : vacancy,
            'applicant': applicant,
            'candidate': candidate,
            'uploaded_file': curriculum.filename,
            'candidate_form': candidate_form,
            'expertise_forms': expertise_forms,
            'academic_forms': academic_forms,
            'advanced_error': advanced_error,
            'initial_missing': initial_missing,
            'sa_profile': sa_profile,
            'conflicts': conflicts,
            'talent_only': True,
            'today': today
        })  

def new_application_resolve_conflicts(request, vacancy_id, card_type):
    """
    Handles resolution of conflicting candidate application data (academic or professional) during the application process.

    This view is accessible only to authenticated users with a 'candidate' profile. Based on the card type, it updates or replaces
    either academic qualifications or work experiences. After modifications, it identifies any remaining conflicts in the candidate's profile.

    Args:
        request (HttpRequest): The HTTP request object containing user and form data.
        vacancy_id (int): The ID of the vacancy the candidate is applying to.
        card_type (int or str): Indicates the type of data being updated ('1' for academic, '2' for professional experience).

    Returns:
        HttpResponse: A rendered HTML page ('resolve_conflicts.html') with conflict resolution results.

    Raises:
        Http404: If the user is not authenticated or is not a candidate.
    """
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    if request.user.is_authenticated:
        if not request.user.profile.codename == 'candidate':
            raise Http404
        candidate = request.user.candidate
        cookie = request.COOKIES.get('applying', False)
        # if not cookie or not cookie == vacancy_id:
        #     return redirect('vacancies_new_application', vacancy_id)
        if request.method == 'POST':
            if card_type == 1 or card_type == '1':
                course_name = request.POST.get('course_name','').strip()
                school = request.POST.get('school','').strip()
                degree = request.POST.get('degree','').strip()
                try:
                    degree = Degree.objects.get(name=degree)
                except:
                    degree = ""
                area = request.POST.get('area','').strip()
                country = request.POST.get('country','').strip()
                try:
                    country = Country.objects.get(name = country)
                except:
                    country = ""
                state = request.POST.get('state','').strip()
                city = request.POST.get('city','').strip()
                status = request.POST.get('status','').strip()
                try:
                    status = Academic_Status.objects.get(name=status)
                except:
                    status = Academic_Status.objects.get(name="Completed")
                start_date = request.POST.get('start_date','').strip()
                end_date = request.POST.get('end_date','').strip()
                old_cards = request.POST.get('old_cards')
                try:
                    old_academics = Academic.objects.filter(id__in=old_cards)
                except:
                    old_academics = Academic.objects.none()
                new_academics = Academic.objects.create(candidate = request.user.candidate, course_name = course_name, degree = degree, area = area, school = school, country = country, state = state, city = city, status = status, start_date = start_date, end_date = end_date)
                old_academics.delete()
            elif card_type == 2 or card_type == '2':
                employment = request.POST.get('employment','').strip()
                company = request.POST.get('company','').strip()
                tasks = request.POST.get('tasks','').strip()
                start_date = request.POST.get('start_date','').strip()
                end_date = request.POST.get('end_date','').strip()
                industry = request.POST.get('industry','').strip()
                try:
                    industry = Company_Industry.objects.filter(id__in=industry)
                except:
                    industry = Company_Industry.objects.none()
                old_cards = request.POST.get('old_cards')
                try:
                    old_expertises = Expertise.objects.filter(id__in=old_cards)
                except:
                    old_expertises = Expertise.objects.none()
                new_expertises = Expertise.objects.create(candidate = request.user.candidate, employment = employment, company = company, tasks = tasks, industry = industry, start_date = start_date, end_date = end_date)
                old_expertises.delete()

        candidate.refresh_from_db()
        conflicts = candidate.find_conflicts()
        today = datetime.now().date()
        return render(request, 'resolve_conflicts.html', {
                'card_type': card_type,
                'vacancy': vacancy,
                'candidate': candidate,
                'user': request.user,
                'conflicts': conflicts,
                'today': today
            })
    else:
        raise Http404

def complete_application(request, vacancy_id):
    """
    Finalizes and submits a job application for a specific vacancy.

    Depending on the user's role (candidate or recruiter), this view processes form submissions, manages custom templated forms,
    handles referral information, and creates or updates a Postulate instance (application). It also logs application source details
    and optional cover letter.

    Args:
        request (HttpRequest): The HTTP request object, potentially containing form POST data.
        vacancy_id (int): The ID of the vacancy being applied to.

    Returns:
        HttpResponse: Redirects to the vacancy detail page on successful application or re-renders 'complete_application.html' if not.
    
    Raises:
        Http404: If the user is neither a candidate nor a valid recruiter.
    """
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    # Check if vacancy is open
    vacancy_has_form_template = vacancy.form_template
    referer_path = request.META.get('HTTP_REFERER', None)
    recruiter_upload = False
    if request.user.is_authenticated and request.user.profile.codename=='recruiter' and vacancy.company in request.user.recruiter.company.all():
        recruiter_upload = True
        vacancy_has_form_template = False
    try:
        referer_name = resolve(urlparse(referer_path).path).url_name
    except:
        referer_name = None
    referer_path = request.session.get('referer', None)
    if request.user.is_authenticated and not recruiter_upload:
        if not request.user.profile.codename == 'candidate':
            raise Http404
        candidate = request.user.candidate
    else:
        candidate = request.session.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate)
        if not candidate.public_email:
            messages.error(request,'Email is required and missing.')
            return redirect('vacancies_new_application', vacancy.id)
    curriculum  = Curriculum.objects.get(candidate = candidate)
    templated_form = None
    coverletter = None
    # if referer_name and referer_name == 'vacancies_new_application' and request.method == 'POST':
    if request.method == 'POST' and request.path == reverse(referer_name,args=[vacancy.pk]):
        coverletter = request.POST.get('coverletter','')
        if vacancy_has_form_template:
            templated_form = TemplatedForm(request.POST, template = vacancy_has_form_template, formClasses="form-control")
        if vacancy_has_form_template and templated_form.is_valid() or coverletter is not None:
            # create postulate
            first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
            application, created = Postulate.objects.get_or_create(vacancy=vacancy, candidate = candidate, vacancy_stage=first_stage)
            cookie = request.COOKIES.get('referer-'+ str(vacancy.id))
            if request.session.get('referral_source'):
                medium, created = Medium.objects.get_or_create(name=request.session.pop('referral_source'))
                application.medium= medium
                application.save()
            if cookie:
                try:
                    referer = Recruiter.objects.get(id = int(cookie))
                except:
                    referer = None
            else:
                referer = None
            if not referer:
                cookie = request.COOKIES.get('exreferer-'+ str(vacancy.id))
                if cookie:
                    try:
                        external_referer = None
                    except:
                        external_referer = None
                else:
                    external_referer = None
            if referer:
                # application.isRecruiter = True
                application.recruiter = referer
                application.save()
                Comment.objects.create(postulate = application, comment_type=3, text='Refered by '+ str(referer.user.get_full_name())) 
            elif external_referer:
                # application.isRecruiter = True
                application.external_referer = external_referer
                application.save()
                Comment.objects.create(postulate = application, comment_type=3, text='Reference by '+ str(referer.user.get_full_name()))                        
            elif recruiter_upload:
                application.is_recruiter = True
                application.recruiter = request.user.recruiter
                application.save()
                Comment.objects.create(postulate = application, comment_type=3, text='Application Added by '+ str(request.user.get_full_name()))
            else:
                Comment.objects.create(postulate = application, comment_type=3, text='Application Received for the job opening')
            if vacancy_has_form_template and templated_form.is_valid():
                fields = templated_form.save()
                for field in fields:
                    if field.value:
                        application.has_filled_custom_form = True
                        application.custom_form_application.add(field)
                application.save()
            if coverletter:
                application.description = coverletter
                application.save()
            if recruiter_upload:
                messages.success(request,'New application has been added.')
            else:
                messages.success(request,'Your application has been received.')
            request.session.pop('referer')
            request.session.pop('candidate')
            return redirect('vacancies_get_vacancy_details', vacancy.id)
    if vacancy_has_form_template and not templated_form :
        templated_form = TemplatedForm(template = vacancy_has_form_template, formClasses="form-control mt2")
    return render(request, 'complete_application.html', {
            'candidate': candidate,
            'vacancy': vacancy,
            'templated_form': templated_form,
        })

def vacancy_talent_sourcing(request, vacancy_id):
    """
    Displays the talent sourcing page for a specific vacancy, accessible only to manager recruiters of the associated company.

    Validates that the user has the appropriate permissions and that the company's job post service is active.
    Retrieves associated external referers for the company to assist in talent sourcing.

    Args:
        request (HttpRequest): The HTTP request object.
        vacancy_id (int): The ID of the vacancy being sourced.

    Returns:
        HttpResponse: A rendered HTML page ('vacancy_talent_sourcing.html') with relevant sourcing details.

    Raises:
        Http404: If the subdomain is inactive, user is not a manager recruiter, or the company/service validation fails.
    """
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
    external_referers = ExternalReferal.objects.filter(company=company, referal_type='ER')
    return render(request,'vacancy_talent_sourcing.html', {
        'vacancy': vacancy,
        'isVacancy': True,
        'vacancy_id': vacancy_id,
        'user': request.user,
        'company': company,
        'external_referers': external_referers,
    })
