# -*- coding: utf-8 -*-

from __future__ import absolute_import
import datetime
from datetime import date
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import RequestContext
import autodoc
from django.utils.translation import gettext as _
from common.models import Employment_Type, Degree
from companies.models import Company_Industry as Industry, Company
from vacancies.models import Vacancy, Salary_Type, Employment_Experience as Experience
from vacancies.forms import BasicSearchVacancyForm
#from django.utils.timezone import utc
import datetime
utc = datetime.timezone.utc
from TRM.context_processors import subdomain
from TRM import settings
from django.db.models import Q, Max
from common.forms import ContactForm, EarlyAccessForm
from payments.models import Package

def index(request):
    if request.method == 'POST':
        try:
            if int(request.POST['industry']) <= 0:
                industry_selected = None
            else:
                industry_selected = Industry.objects.get(id=request.POST['industry'])
        except:
            industry_selected = None
        form = BasicSearchVacancyForm(data=request.POST, files=request.FILES, industry_selected=industry_selected)

        if form.is_valid():
            vacancies_search_state = form.clean_state()
            vacancies_search_industry = form.clean_industry()
            vacancies_search_area = form.clean_area()
            pubDateSearch = form.clean_vacancyPubDateSearch()
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            vacancies_search_pub_date = now - datetime.timedelta(days=pubDateSearch.days)
            vacancies_search_pub_date_days = pubDateSearch
            return redirect('vacancies_first_search_vacancies')
    else:
        form = BasicSearchVacancyForm()
        return render(request,'index.html', {'isIndex': True, 'form': form})
   
def companies(request):
      return render(request,'company_index.html', {'isCompanie': True})
   
def privacy_policy(request):
     return render(request,'privacy_policy.html', {'isProfile': True})
    
def terms_and_conditions(request):
     return render(request,'terms_and_conditions.html', {'isProfile': True})
    
def email_campaign_0(request):
    return render(request, 'email_campaigns/campaign_0.html', {})
    
def handler500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response

def pricing_comparison(request):
     return render(request,'pricing.html',{})
   
def about_us(request):
     return render(request,'about_us.html',{})
    

def product(request):
     return render(request,'product.html',{})
    
def pricing(request):
    packages = Package.objects.all()
    return render(request,'pricing.html',{'packages':packages})
"""   
def contact(request):
    if request.method == 'POST':
        form_contact = ContactForm(request=request,data=request.POST )
        if form_contact.is_valid():
            form_contact.save()
            form_contact = ContactForm(request=request)
    else:
        form_contact = ContactForm(request=request)
        return render(request,'contact.html',{'form_contact':form_contact})
"""
def contact(request):
    if request.method == 'POST':
        form_contact = ContactForm(request=request, data=request.POST)
        if form_contact.is_valid():
            form_contact.save()
            form_contact = ContactForm(request=request)
            return render(request, 'contact.html', {
                'form_contact': form_contact,
                'success': True
            })
        else:
            return render(request, 'contact.html', {
                'form_contact': form_contact
            })
    else:
        form_contact = ContactForm(request=request)
        return render(request, 'contact.html', {
            'form_contact': form_contact
        })

    
def comingsoon(request):
    if request.method == 'POST':
        form_request = EarlyAccessForm(request=request,data=request.POST )
        if form_request.is_valid():
            form_request.save()
            form_request = EarlyAccessForm(request=request)
    else:
        form_request = EarlyAccessForm(request=request)
        return render(request,'comingsoon.html',{'no_header':True, 'no_footer':True, 'form_request':form_request})
    
def job_board(request):
    subdomain_data = subdomain(request)
    if subdomain_data['active_host']:
        return redirect(settings.HOSTED_URL + reverse('job_board'))
    alljobs = Vacancy.objects.all()
    jobs = Vacancy.publishedjobs.all()
    alllocations = set(job.location() for job in alljobs)
    filters = {
        'keywords':'',
        'locations':'',
        'types':'',
        'industries':'',
        'degress':'',
        'joinings':'',
        'experiences':'',
    }
    if request.method == 'GET':
        jobsbykeywords = jobs.none()
        jobsbylocations = jobs.none()
        jobsbytypes = jobs.none()
        jobsbyindustries = jobs.none()
        jobsbydegrees = jobs.none()
        jobsbysalaries = jobs.none()
        jobsbyjoinings = jobs.none()
        jobsbyexperiences = jobs.none()
        keywords = request.GET.get('k','').split(';')
        filters['keywords'] = keywords
        if keywords and keywords[0]:
            for keyword in keywords:
                jobsbykeywords = jobs.filter(
                    Q(company__name__icontains = keyword) |
                    Q(company__social_name__icontains = keyword) |
                    Q(description__icontains = keyword) |
                    Q(employment__icontains = keyword) |
                    Q(function__icontains = keyword) |
                    Q(skills__icontains = keyword))
            # raise ValueError(jobsbykeywords)
        locations = request.GET.get('l','').split(';')
        filters['locations'] = locations
        if locations and locations[0]:
            for location in locations:
                location = location.split(',')
                q = Q()
                for place in location:
                    place = place.strip()
                    q |= Q(city__icontains = place) | Q(state__icontains = place) | Q(nationality__name__icontains = place) | Q(nationality__iso2_code__icontains = place)
                jobsbylocations = jobs.filter(q)
        types = request.GET.get('t','').split(';')
        filters['types'] = types
        if types and types[0]:
            types = Employment_Type.objects.filter(id__in=types)
            jobsbytypes = jobs.filter(employmentType__in=types)
        industries = request.GET.get('i','').split(';')
        filters['industries'] = industries
        if industries and industries[0]:
            industries = Industry.objects.filter(id__in=industries)
            jobsbyindustries = jobs.filter(industry__in=industries)
        degrees = request.GET.get('d','').split(';')
        filters['degrees'] = degrees
        if degrees and degrees[0]:
            degrees = Degree.objects.filter(id__in=degrees)
            jobsbydegrees = jobs.filter(degree__in=degrees)
        salaries = request.GET.get('s','').split(';')
        filters['salaries'] = salaries
        if salaries and salaries[0]:
            salaries = Salary_Type.objects.filter(id__in=salaries)
            jobsbysalaries = jobs.filter(salaryType__in=salaries)
        joinings = request.GET.get('j','').split(';')
        filters['joinings'] = joinings
        if joinings and joinings[0]:
            jobsbyjoinings = jobs.filter(hiring_date = None)
            for joining in joinings:
                rangestart, rangeend = joining.split(' - ')
                rangestart = rangestart.split('/')
                rangestart = date(int(rangestart[2]),int(rangestart[0]),int(rangestart[1]))
                rangeend = rangeend.split('/')
                rangeend = date(int(rangeend[2]),int(rangeend[0]),int(rangeend[1]))
                jobsinrange = jobs.filter(Q(hiring_date__gte=rangestart),Q(hiring_date__lte=rangeend))
                jobsbyjoinings |= jobsinrange
        experiences = request.GET.get('e','').split(';')
        filters['experiences'] = experiences
        if experiences and experiences[0]:
            q = Q(minEmploymentExperience__id = 1)
            for experience in experiences:
                experience = experience.split('-')
                q |= (Q(minEmploymentExperience__id__lte=int(experience[1]) + 2) & Q(maxEmploymentExperience__id__gte=int(experience[0]) + 2))
            jobsbyexperiences = jobs.filter(q)
        if keywords and keywords[0] or locations and locations[0] or types and types[0] or industries and industries[0] or degrees and degrees[0] or salaries and salaries[0] or joinings and joinings[0] or experiences and experiences[0]:
            jobs = jobsbykeywords | jobsbylocations | jobsbytypes | jobsbyindustries | jobsbydegrees | jobsbysalaries | jobsbyjoinings | jobsbyexperiences
            # raise ValueError(jobs)
    companies = Company.objects.annotate(recent=Max('vacancy__pub_date')).filter(vacancy__in = jobs).order_by('-recent').distinct()
    for company in companies:
        company.jobs = jobs.filter(company = company)
    template = 'job_board.html'
    page_template = 'job_board_item.html'
    if request.is_ajax():
        template = page_template
    return render(request, 
        template,
        {
            'page_template': page_template,
            'isJobBoard':True,
            'jobs':jobs,
            'companies': companies,
            'types': Employment_Type.objects.all(),
            'industries': Industry.objects.all(),
            'degrees': Degree.objects.all(),
            'salaries': Salary_Type.objects.all(),
            'locations': alllocations,
            'filters': filters,
        })
    #,context_instance = RequestContext(request))