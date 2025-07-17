"""
Views for handling activity-related functionality in the SpotAxis application.

This module provides view functions for displaying and managing user activities,
including activity streams and individual activity details. It handles both
company-specific and user-specific activity views with proper authentication
and authorization checks.
"""

from __future__ import absolute_import
import decimal
import os
import traceback
import json
import random
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
#from django.template import RequestContext
from TRM.settings import SITE_URL, num_pages, number_objects_page
from TRM.context_processors import subdomain
from companies.models import Company, Recruiter
from activities.models import *
# Create your views here.

@login_required
def activities(request, activity_id=None):
    """
    View function for displaying user activities and activity streams.
    
    This view handles both the activity stream for a user and individual activity details.
    It requires user authentication and proper company/recruiter association.
    The view supports two modes:
    1. Activity stream mode (when activity_id is None): Shows all activities where the user
       is either the actor or a subscriber
    2. Individual activity mode (when activity_id is provided): Shows a specific activity
       if the user has permission to view it
    
    Args:
        request (HttpRequest): The HTTP request object containing user and session data
        activity_id (int, optional): The ID of a specific activity to view. If None,
                                   shows the activity stream
    
    Returns:
        HttpResponse: Rendered template 'activities.html' with activity data
        
    Context:
        company (Company): The company associated with the current subdomain
        recruiter (Recruiter): The recruiter profile of the current user
        user (User): The current authenticated user
        activity_id (int): The ID of the activity being viewed (if any)
        activity_stream (QuerySet): The activities to be displayed
        
    Raises:
        Http404: If the company/subdomain is not found, the user is not a recruiter
                for the company, or the requested activity is not accessible
    """
    context = {}
    subdomain_data = subdomain(request)
    try:
        company = Company.objects.get(subdomain__slug = subdomain_data['active_subdomain'])
        recruiter = Recruiter.objects.get(company__in=[company], user = request.user)
    except:
        raise Http404
    context['company'] = company
    context['recruiter'] = recruiter
    context['user'] = request.user
    context['activity_id'] = activity_id
    if not activity_id:
        context['activity_stream'] = Activity.objects.all().filter(Q(actor = request.user) | Q(subscribers__in=[request.user])).distinct()
    else:
        context['activity_stream'] = Activity.objects.all().filter(Q(id=activity_id) & (Q(actor=request.user) | Q(subscribers__in =[request.user]))).distinct()
        if not context['activity_stream']:
            raise Http404
    return render(request, 'activities.html', context)