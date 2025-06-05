# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime, timedelta
from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from vacancies.models import Vacancy_Status, Postulate_Stage

register = template.Library()


@register.filter
def addClass(formField,cssClass):
    try:
        formField.field.widget.attrs['class'] = formField.field.widget.attrs.get('class','') + ' ' + cssClass
    except:
        pass
    return formField
 
@register.filter
def removeZeros(number):
    try:
        if number == int(number):
            return int(number)
    except:
        return number

@register.filter
def addAttr(formField,attr):
    try:
        attr_name, attr_value = attr.split(':')
        formField.field.widget.attrs[attr_name] = formField.field.widget.attrs.get(attr_name,'') + ' ' + attr_value
    except:
        pass
    return formField
 
@register.filter
def get_dict_key(dict,key):
    try:
        return dict[key]
    except:
        return None
 
# @register.filter
# def get_dir(obj):
#     # return 'a'
#     return str(dir(obj))
  
@register.filter
def limit_number(num, limit):
    try:
        if num <= limit:
            return num
        else:
            return str(limit) + "+"
    except:
        return num
 
@register.filter
def args(obj, arg):
    if "__callArg" not in obj.__dict__:
        obj.__callArg = []
 
    obj.__callArg += [arg]
    return obj

@register.filter(name="call")
def callMethod(obj, methodName):
    method = getattr(obj, methodName)
 
    if "__callArg" in obj.__dict__:
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()



@register.filter(name='rem_nbsp', is_safe=True)
@stringfilter
def rem_nbsp(value):
    """
    Removes labels &nbsp;
    used to display the descrition of the preview of vacancies
    """
    return value.replace('&nbsp;', ' ')


@register.filter(name='upto', is_safe=True)
@stringfilter
def upto(value, delimiter=None):
    """
    Parse a string to find a specific character
    Used to get year of birthdate of a candidate
    {{ candidate.birthday|timesince|upto:',' }}
    """
    return value.split(delimiter)[0]

@register.filter(name='uptill', is_safe=True)
@stringfilter
def uptill(value, length=0):
    """
    Parse a string to find a specific character
    Used to get year of birthdate of a candidate
    {{ candidate.birthday|timesince|upto:',' }}
    """
    return value[0:length]


@register.filter(name='inAuthList', is_safe=True)
@stringfilter
def inAuthList(value):
    """
    Parse a string to find a specific character
    Used to get year of birthdate of a candidate
    {{ candidate.birthday|timesince|upto:',' }}
    """
    from django.urls import reverse
    if value == reverse('auth_login') or value == reverse('auth_logout') or value == reverse('companies_record_recruiter') or value == reverse('candidates_register_candidate'):
        return True
    else:
        return False

@register.filter(name='resolveNamespace', is_safe=True)
@stringfilter
def resolveNamespace(value, namespace = None):
    """
    Parse a string to find a specific character
    Used to get year of birthdate of a candidate
    {{ candidate.birthday|timesince|upto:',' }}
    """
    from django.urls import resolve
    if namespace and namespace in resolve(value).namespaces:
        return True
    else:
        return False


import locale
locale.setlocale(locale.LC_ALL, '')
@register.filter()
def currency(value):
    """
    Apply the currency format .00 o ,00
    """
    return locale.currency(value, symbol=False, grouping=True)


@register.filter(name='show_no_email', is_safe=True)
@stringfilter
def show_no_email(value):
    """
    Sample **** before the @ in an email
    """
    return value.split('@')[-1]

@register.filter(name='split')
def split(value, arg):
    return value.split(arg)

#@register.assignment_tag
@register.simple_tag
def get_status_count(status,company):
    try:
        return Vacancy_Status.objects.get(name = status).vacancy_set.filter(company__id=company).count()
    except:
        return 0

@register.filter
def mod(num, val):
    return num % val
@register.filter
def sub(num, val):
    return num - val
@register.filter
def timeleft(date):
    try:
        return (date - datetime.now()).days
    except:
        return 1

@register.filter
def isProcessManager(recruiter,process):
    if recruiter in process.recruiters.all():
        return True
    else:
        return False

@register.filter
def hasRated(recruiter,activity):
    if activity.activity_type == 1:
        ps,c = Postulate_Stage.objects.get_or_create(postulate = activity.postulate, vacancy_stage = activity.postulate.vacancy_stage)
        rated = ps.scores.all().filter(recruiter = recruiter)
        if rated:
            return True
        else:
            return False
    else:
        return False


@register.filter
def daysadd(date,days):
    try:
        return (date + timedelta(days=days)).date()
    except:
        return (datetime.now() + timedelta(days=days)).date()


@register.filter
def days_from_now(days):
    from datetime import datetime
    try:
        return (timedelta(days=days) + datetime.now()).date()
    except:
        return datetime.now().date()



@register.filter
def isPast(DateTime):
    if DateTime.date() < datetime.now().date() or DateTime.date() == datetime.now().date() and DateTime.time() < datetime.now().time():
        return True
    return False


@register.filter
def isNearFuture(DateTime,minutes = 10):
    delta = timedelta(minutes=minutes)
    Future = datetime.now() + delta
    DateTime = DateTime.replace(tzinfo=None)
    if DateTime.date() == Future.date() and DateTime.time() <= Future.time() or DateTime.date() < Future.date() and (Future - DateTime) <= delta:
        return True
    return False


@register.filter
def isPastDate(Date):
    if Date.date() < datetime.now().date():
        return True
    return False


@register.filter
def isToday(Date):
    Future = datetime.now()
    if Date.date() == Future.date():
        return True
    return False


@register.filter
def appendURL(url,slug):
    if not slug:
        return url
    else:
        return url.strip('/') + '/' + slug.strip('/') + '/'

@register.filter
def get_field_value(model,field):
    try:
        return getattr(model,field)
    except:
        return ''


@register.filter
def isIterable(object):
    if hasattr(object,'__iter__'):
        return True
    return False

@register.filter
def joinBy(array,character):
    return character.join(array)

@register.filter
def utf8(array):
    return [node.encode('utf-8') for node in array]

@register.filter
def ascii(string,arg=None):
    if arg:
        return string.encode('ascii',arg)
    else:
        return string.encode('ascii')

@register.filter
def startsWith(string, slug):
    return string.startswith(slug)

@register.filter
def parseInt(string):
    try:
        return int(string)
    except:
        return string

@register.filter
def get_settings_url(company):
    if company.check_service('CSM_CNAME'):
        return reverse('companies_site_management',args=['subdomain'])
    elif company.check_service('CSM_JOBS_WIDGET'):
        return reverse('companies_site_management',args=['embed'])
    else:
        return reverse('companies_site_management',args=['joblinks'])

@register.filter
def no_date(date):
    try:
        return date.strftime("%b %Y")
    except:
        if date:
            return date
        else:
            return ""
