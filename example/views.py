# -*- coding: utf-8 -*-

from __future__ import absolute_import
import random
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext


def test(request):
    """# if request.method == 'POST':
    #     form = BasicSearchVacancyForm(data=request.POST, files=request.FILES, industry_selected=industry_selected)
    #     if form.is_valid():
    #         return redirect('vacancies_first_search_vacancies')
    # else:
    #     form = BasicSearchVacancyForm()"""

    return render(request, 'test.html',
                              {'isIndex': True,
                               })
 