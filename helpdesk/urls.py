"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

urls.py - Mapping of URL's to our various views. Note we always used NAMED
          views for simplicity in linking later on.
"""
"""
URL routing for django-helpdesk.

Maps URL patterns to views for ticket management, public ticket submission,
RSS feeds, API access, knowledge base, and user authentication.

Uses named URL patterns for consistency and easier reverse lookup.

Main route categories:
- Staff views (ticket CRUD, reports, settings)
- Public views (submit/view ticket)
- RSS feeds (open/unassigned tickets, activity)
- API endpoints
- Optional knowledge base (if enabled)
"""
from __future__ import absolute_import
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from helpdesk import settings as helpdesk_settings
from helpdesk.views import feeds, staff, public, api, kb
from helpdesk.views.auth import HelpdeskLoginView, HelpdeskLogoutView
from helpdesk.views.help import HelpAPIView, HelpContextView, SystemSettingsView


class DirectTemplateView(TemplateView):
    """
    Custom TemplateView that allows passing static or dynamic context data.

    If a context value is callable, it gets evaluated before rendering.

    Inherits:
        - django.views.generic.TemplateView
    """
    extra_context = None

    def get_context_data(self, **kwargs):
        """
        Adds extra_context (if provided) to the default context.

        Returns:
            dict: Template context for rendering the view
        """
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in list(self.extra_context.items()):
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context

urlpatterns = [
    path('dashboard/', staff.dashboard, name='helpdesk_dashboard'),
    path('tickets/', staff.ticket_list, name='helpdesk_list'),
    path('tickets/update/', staff.mass_update, name='helpdesk_mass_update'),
    path('tickets/submit/', staff.create_ticket, name='helpdesk_submit'),
    path('tickets/<int:ticket_id>/', staff.view_ticket, name='helpdesk_view'),
    path('tickets/<int:ticket_id>/followup_edit/<int:followup_id>/', staff.followup_edit, name='helpdesk_followup_edit'),
    path('tickets/<int:ticket_id>/followup_delete/<int:followup_id>/', staff.followup_delete, name='helpdesk_followup_delete'),
    path('tickets/<int:ticket_id>/edit/', staff.edit_ticket, name='helpdesk_edit'),
    path('tickets/<int:ticket_id>/update/', staff.update_ticket, name='helpdesk_update'),
    path('tickets/<int:ticket_id>/delete/', staff.delete_ticket, name='helpdesk_delete'),
    path('tickets/<int:ticket_id>/hold/', staff.hold_ticket, name='helpdesk_hold'),
    path('tickets/<int:ticket_id>/unhold/', staff.unhold_ticket, name='helpdesk_unhold'),
    path('tickets/<int:ticket_id>/cc/', staff.ticket_cc, name='helpdesk_ticket_cc'),
    path('tickets/<int:ticket_id>/cc/add/', staff.ticket_cc_add, name='helpdesk_ticket_cc_add'),
    path('tickets/<int:ticket_id>/cc/delete/<int:cc_id>/', staff.ticket_cc_del, name='helpdesk_ticket_cc_del'),
    path('tickets/<int:ticket_id>/dependency/add/', staff.ticket_dependency_add, name='helpdesk_ticket_dependency_add'),
    path('tickets/<int:ticket_id>/dependency/delete/<int:dependency_id>/', staff.ticket_dependency_del, name='helpdesk_ticket_dependency_del'),
    path('tickets/<int:ticket_id>/attachment_delete/<int:attachment_id>/', staff.attachment_del, name='helpdesk_attachment_del'),
    re_path(r'^raw/(?P<type>\w+)/$', staff.raw_details, name='helpdesk_raw'),
    path('rss/', staff.rss_list, name='helpdesk_rss_index'),
    path('reports/', staff.report_index, name='helpdesk_report_index'),
    re_path(r'^reports/(?P<report>\w+)/$', staff.run_report, name='helpdesk_run_report'),
    path('save_query/', staff.save_query, name='helpdesk_savequery'),
    path('delete_query/<int:id>/', staff.delete_saved_query, name='helpdesk_delete_query'),
    path('settings/', staff.user_settings, name='helpdesk_user_settings'),
    path('ignore/', staff.email_ignore, name='helpdesk_email_ignore'),
    path('ignore/add/', staff.email_ignore_add, name='helpdesk_email_ignore_add'),
    path('ignore/delete/<int:id>/', staff.email_ignore_del, name='helpdesk_email_ignore_del'),
]

urlpatterns += [
    path('', public.homepage, name='helpdesk_home'),
    path('view/', public.view_ticket, name='helpdesk_public_view'),
    path('change_language/', public.change_language, name='helpdesk_public_change_language'),
]

urlpatterns += [
    re_path(r'^rss/user/(?P<user_name>[^/]+)/$', login_required(feeds.OpenTicketsByUser()), name='helpdesk_rss_user'),
    re_path(r'^rss/user/(?P<user_name>[^/]+)/(?P<queue_slug>[A-Za-z0-9_-]+)/$', login_required(feeds.OpenTicketsByUser()), name='helpdesk_rss_user_queue'),
    re_path(r'^rss/queue/(?P<queue_slug>[A-Za-z0-9_-]+)/$', login_required(feeds.OpenTicketsByQueue()), name='helpdesk_rss_queue'),
]

urlpatterns += [
    re_path(r'^rss/unassigned/$', login_required(feeds.UnassignedTickets()), name='helpdesk_rss_unassigned'),
    re_path(r'^rss/recent_activity/$', login_required(feeds.RecentFollowUps()), name='helpdesk_rss_activity'),
]

urlpatterns += [
    path(r'^api/(?P<method>[a-z_-]+)/$', api.api, name='helpdesk_api'),
    path(r'^login/$', HelpdeskLoginView.as_view(), name='login'),
    path(r'^logout/$', HelpdeskLogoutView.as_view(), name='logout'),
]

if helpdesk_settings.HELPDESK_KB_ENABLED:
    urlpatterns += [
        path(r'^kb/$', kb.index, name='helpdesk_kb_index'),
        path(r'^kb/(?P<item>[0-9]+)/$', kb.item, name='helpdesk_kb_item'),
        path(r'^kb/(?P<item>[0-9]+)/vote/$', kb.vote, name='helpdesk_kb_vote'),
        path(r'^kb/(?P<slug>[A-Za-z0-9_-]+)/$', kb.category, name='helpdesk_kb_category'),
    ]

urlpatterns += [
    path(r'^api/$', HelpAPIView.as_view(), name='helpdesk_api_help'),
    path(r'^help/context/$', HelpContextView.as_view(), name='helpdesk_help_context'),
    path(r'^system_settings/$', SystemSettingsView.as_view(), name='helpdesk_system_settings'),
]
