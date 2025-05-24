"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/kb.py - Public-facing knowledgebase views. The knowledgebase is a
              simple categorised question/answer system to show common
              resolutions to common problems.

This module provides views for displaying knowledgebase categories,
individual questions/answers, and supports user voting to help identify
useful responses.
"""

from __future__ import absolute_import
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from helpdesk import settings as helpdesk_settings
from helpdesk.models import KBCategory, KBItem


def index(request):
    """
    Displays the main Knowledgebase index page.

    Shows a list of all available categories in the knowledgebase. Each category
    contains grouped question-and-answer items that help users find solutions
    before opening a support ticket.

    Note: Could be extended in future to show top-rated or most viewed articles.
    """

    category_list = KBCategory.objects.all()
    # TODO: It'd be great to have a list of most popular items here.
    return render(request, 'helpdesk/kb_index.html', {
        'kb_categories': category_list,
        'helpdesk_settings': helpdesk_settings,
    })


def category(request, slug):
    """
    Displays a specific category of knowledgebase items.

    Fetches the category based on the slug and renders a list of all question/
    answer items within that category.

    Useful when users are browsing the KB by topic or department.
    """

    category = get_object_or_404(KBCategory, slug__iexact=slug)
    items = category.kbitem_set.all()
    return render(request, 'helpdesk/kb_category.html', {
        'category': category,
        'items': items,
        'helpdesk_settings': helpdesk_settings,
    })


def item(request, item):
    """
    Displays a specific knowledgebase item.

    Shows the full question and answer text to the user, allowing them to
    understand the solution. Includes contextual helpdesk settings.

    Can be accessed directly from category pages or search results.
    """

    item = get_object_or_404(KBItem, pk=item)
    return render(request, 'helpdesk/kb_item.html', {
        'item': item,
        'helpdesk_settings': helpdesk_settings,
    })


def vote(request, item):
    """
    Allows users to vote on the helpfulness of a knowledgebase article.

    Votes can be either 'up' or 'down'. Each vote increases the total vote
    count, and 'up' votes additionally increase the positive recommendation
    counter. Redirects back to the item page after voting.

    This helps the team understand which articles are most useful.
    """

    item = get_object_or_404(KBItem, pk=item)
    vote = request.GET.get('vote', None)
    if vote in ('up', 'down'):
        item.votes += 1
        if vote == 'up':
            item.recommendations += 1
        item.save()

    return HttpResponseRedirect(item.get_absolute_url())
