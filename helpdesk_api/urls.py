from django.urls import path, include
from rest_framework.routers import DefaultRouter

from helpdesk_api.views import feeds, kb, public, staff

router = DefaultRouter()

# Feeds
router.register(r'open-tickets-by-user', feeds.OpenTicketsByUserViewSet, basename='open-tickets-by-user')
router.register(r'unassigned-tickets', feeds.UnassignedTicketsViewSet, basename='unassigned-tickets')
router.register(r'recent-followups', feeds.RecentFollowUpsViewSet, basename='recent-followups')
router.register(r'open-tickets-by-queue', feeds.OpenTicketsByQueueViewSet, basename='open-tickets-by-queue')

# Knowledge Base
router.register(r'kb-categories', kb.KBCategoryViewSet)
router.register(r'kb-items', kb.KBItemViewSet)

# Public
router.register(r'public-tickets', public.PublicTicketViewSet, basename='public-tickets')

# Staff / Admin
router.register(r'tickets/dashboard', staff.TicketDashboardViewSet, basename='ticket-dashboard')
router.register(r'tickets/delete', staff.DeleteTicketViewSet, basename='ticket-delete')
router.register(r'tickets/view', staff.ViewTicketViewSet, basename='ticket-view')
router.register(r'tickets/update', staff.UpdateTicketViewSet, basename='ticket-update')
router.register(r'tickets/edit', staff.EditTicketViewSet, basename='ticket-edit')
router.register(r'tickets/create', staff.TicketCreateViewSet, basename='ticket-create')
router.register(r'tickets/hold', staff.HoldUnHoldTicketViewSet, basename='ticket-hold')
router.register(r'tickets/list', staff.TicketListViewSet, basename='ticket-list')
router.register(r'tickets/followups/edit', staff.FollowUpEditViewSet, basename='followup-edit')
router.register(r'tickets/followups/delete', staff.FollowUpDeleteViewSet, basename='followup-delete')
router.register(r'tickets/return', staff.ReturnToTicketViewSet, basename='return-to-ticket')
router.register(r'tickets/mass-update', staff.MassUpdateViewSet, basename='mass-update')
router.register(r'reports/index', staff.ReportIndexViewSet, basename='report-index')
router.register(r'reports/run', staff.RunReportViewSet, basename='run-report')
router.register(r'saved-queries', staff.SavedQueryViewSet, basename='saved-query')
router.register(r'saved-queries/delete', staff.DeleteSavedQueryViewSet, basename='delete-saved-query')
router.register(r'user-settings', staff.UserSettingsViewSet, basename='user-settings')
router.register(r'ignore-emails', staff.IgnoreEmailViewSet, basename='ignore-email')
router.register(r'ticket-cc', staff.TicketCCViewSet, basename='ticket-cc')
router.register(r'attachments', staff.AttachmentViewSet, basename='attachments')

urlpatterns = [
    path('', include(router.urls)),
]