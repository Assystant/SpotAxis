
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
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from TRM.settings import SITE_URL, num_pages, number_objects_page
from TRM.context_processors import subdomain
from companies.models import Company, Recruiter
from activities.models import *
# Create your views here.
@login_required
def activities(request, activity_id=None):
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
	return render_to_response('activities.html',context,context_instance=RequestContext(request))