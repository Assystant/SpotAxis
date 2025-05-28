from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from __future__ import absolute_import
from datetime import datetime, timedelta
from django import VERSION, forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django.core import paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dates import MONTHS_3
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.template import loader, Context
from collections import defaultdict
import mimetypes

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from helpdesk.forms import (
    TicketForm, UserSettingsForm, EmailIgnoreForm, EditTicketForm, TicketCCForm,
    EditFollowUpForm, TicketDependencyForm
)
from helpdesk.lib import (
    send_templated_mail, query_to_dict, apply_query, safe_template_context,
)
from helpdesk.models import (
    Ticket, Queue, FollowUp, TicketChange, PreSetReply, Attachment, SavedSearch,
    IgnoreEmail, TicketCC, TicketDependency,
)
from helpdesk import settings as helpdesk_settings
from helpdesk_api.serializers import *

User = get_user_model()

from helpdesk.settings import HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE, HELPDESK_AUTO_SUBSCRIBE_ON_TICKET_RESPONSE
if helpdesk_settings.HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE:
    # treat 'normal' users like 'staff'
    staff_member_required = user_passes_test(
        lambda u: u.is_authenticated() and u.is_active)
else:
    staff_member_required = user_passes_test(
        lambda u: u.is_authenticated() and u.is_active and u.is_staff)


superuser_required = user_passes_test(
    lambda u: u.is_authenticated() and u.is_active and u.is_superuser)

def _get_user_queues(user):
    """Return the list of Queues the user can access.

    :param user: The User (the class should have the has_perm method)
    :return: A Python list of Queues
    """
    all_queues = Queue.objects.all()
    limit_queues_by_user = \
        helpdesk_settings.HELPDESK_ENABLE_PER_QUEUE_STAFF_PERMISSION \
        and not user.is_superuser
    if limit_queues_by_user:
        id_list = [q.pk for q in all_queues if user.has_perm(q.permission_name)]
        return all_queues.filter(pk__in=id_list)
    else:
        return all_queues


def _has_access_to_queue(user, queue):
    """Check if a certain user can access a certain queue.

    :param user: The User (the class should have the has_perm method)
    :param queue: The django-helpdesk Queue instance
    :return: True if the user has permission (either by default or explicitly), false otherwise
    """
    if user.is_superuser or not helpdesk_settings.HELPDESK_ENABLE_PER_QUEUE_STAFF_PERMISSION:
        return True
    else:
        return user.has_perm(queue.permission_name)


class HasQueueAccess(BasePermission):
    """
    Permission that uses `_has_access_to_queue` to check object-level access.
    """
    def has_object_permission(self, request, view, obj):
        return _has_access_to_queue(request.user, obj.queue)

def return_ticketccstring_and_show_subscribe(user, ticket):
    """used in view_ticket() and followup_edit()"""
    # create the ticketcc_string and check whether current user is already
    # subscribed
    username = user.get_username().upper()
    useremail = user.email.upper()
    strings_to_check = list()
    strings_to_check.append(username)
    strings_to_check.append(useremail)

    ticketcc_string = ''
    all_ticketcc = ticket.ticketcc_set.all()
    counter_all_ticketcc = len(all_ticketcc) - 1
    show_subscribe = True
    for i, ticketcc in enumerate(all_ticketcc):
        ticketcc_this_entry = str(ticketcc.display)
        ticketcc_string += ticketcc_this_entry
        if i < counter_all_ticketcc:
            ticketcc_string += ', '
        if strings_to_check.__contains__(ticketcc_this_entry.upper()):
            show_subscribe = False

    # check whether current user is a submitter or assigned to ticket
    assignedto_username = str(ticket.assigned_to).upper()
    submitter_email = ticket.submitter_email.upper()
    strings_to_check = list()
    strings_to_check.append(assignedto_username)
    strings_to_check.append(submitter_email)
    if strings_to_check.__contains__(username) or strings_to_check.__contains__(useremail):
        show_subscribe = False

    return ticketcc_string, show_subscribe

def subscribe_staff_member_to_ticket(ticket, user):
    """used in view_ticket() and update_ticket()"""
    ticketcc = TicketCC(
        ticket=ticket,
        user=user,
        can_view=True,
        can_update=True,
    )
    ticketcc.save()

def return_to_ticket(user, helpdesk_settings, ticket):
    """Helper function for update_ticket"""

    if user.is_staff or helpdesk_settings.HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE:
        return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        return HttpResponseRedirect(ticket.ticket_url)

def calc_average_nbr_days_until_ticket_resolved(Tickets):
    nbr_closed_tickets = len(Tickets)
    days_per_ticket = 0
    days_each_ticket = list()

    for ticket in Tickets:
        time_ticket_open = ticket.modified - ticket.created
        days_this_ticket = time_ticket_open.days
        days_per_ticket += days_this_ticket
        days_each_ticket.append(days_this_ticket)

    if nbr_closed_tickets > 0:
        mean_per_ticket = days_per_ticket / nbr_closed_tickets
    else:
        mean_per_ticket = 0

    return mean_per_ticket

def calc_basic_ticket_stats(Tickets):
    # all not closed tickets (open, reopened, resolved,) - independent of user
    all_open_tickets = Tickets.exclude(status=Ticket.CLOSED_STATUS)
    today = datetime.today()

    date_30 = date_rel_to_today(today, 30)
    date_60 = date_rel_to_today(today, 60)
    date_30_str = date_30.strftime('%Y-%m-%d')
    date_60_str = date_60.strftime('%Y-%m-%d')

    # > 0 & <= 30
    ota_le_30 = all_open_tickets.filter(created__gte=date_30_str)
    N_ota_le_30 = len(ota_le_30)

    # >= 30 & <= 60
    ota_le_60_ge_30 = all_open_tickets.filter(created__gte=date_60_str, created__lte=date_30_str)
    N_ota_le_60_ge_30 = len(ota_le_60_ge_30)

    # >= 60
    ota_ge_60 = all_open_tickets.filter(created__lte=date_60_str)
    N_ota_ge_60 = len(ota_ge_60)

    # (O)pen (T)icket (S)tats
    ots = list()
    # label, number entries, color, sort_string
    ots.append(['< 30 days', N_ota_le_30, get_color_for_nbr_days(N_ota_le_30),
                sort_string(date_30_str, ''), ])
    ots.append(['30 - 60 days', N_ota_le_60_ge_30, get_color_for_nbr_days(N_ota_le_60_ge_30),
                sort_string(date_60_str, date_30_str), ])
    ots.append(['> 60 days', N_ota_ge_60, get_color_for_nbr_days(N_ota_ge_60),
                sort_string('', date_60_str), ])

    # all closed tickets - independent of user.
    all_closed_tickets = Tickets.filter(status=Ticket.CLOSED_STATUS)
    average_nbr_days_until_ticket_closed = \
        calc_average_nbr_days_until_ticket_resolved(all_closed_tickets)
    # all closed tickets that were opened in the last 60 days.
    all_closed_last_60_days = all_closed_tickets.filter(created__gte=date_60_str)
    average_nbr_days_until_ticket_closed_last_60_days = \
        calc_average_nbr_days_until_ticket_resolved(all_closed_last_60_days)

    # put together basic stats
    basic_ticket_stats = {
        'average_nbr_days_until_ticket_closed': average_nbr_days_until_ticket_closed,
        'average_nbr_days_until_ticket_closed_last_60_days':
            average_nbr_days_until_ticket_closed_last_60_days,
        'open_ticket_stats': ots,
    }

    return basic_ticket_stats


def get_color_for_nbr_days(nbr_days):
    if nbr_days < 5:
        color_string = 'green'
    elif nbr_days < 10:
        color_string = 'orange'
    else:  # more than 10 days
        color_string = 'red'

    return color_string


def days_since_created(today, ticket):
    return (today - ticket.created).days


def date_rel_to_today(today, offset):
    return today - timedelta(days = offset)


def sort_string(begin, end):
    return 'sort=created&date_from=%s&date_to=%s&status=%s&status=%s&status=%s' % (
        begin, end, Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS, Ticket.RESOLVED_STATUS)

class TicketDashboardViewSet(viewsets.ModelViewSet):
    """
    A ModelViewSet that includes a dashboard view for ticket summaries.
    """
    queryset = Ticket.objects.none()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user
        user_queues = _get_user_queues(user)

        # Tickets assigned to the user and open/reopened
        tickets = Ticket.objects.select_related('queue').filter(
            assigned_to=user
        ).exclude(
            status__in=[Ticket.CLOSED_STATUS, Ticket.RESOLVED_STATUS]
        )

        # Tickets assigned to the user and closed/resolved
        tickets_closed_resolved = Ticket.objects.select_related('queue').filter(
            assigned_to=user,
            status__in=[Ticket.CLOSED_STATUS, Ticket.RESOLVED_STATUS]
        )

        # Unassigned tickets in queues the user has access to
        unassigned_tickets = Ticket.objects.select_related('queue').filter(
            assigned_to__isnull=True,
            queue__in=user_queues
        ).exclude(status=Ticket.CLOSED_STATUS)

        # Tickets submitted by the user
        reported_tickets = Ticket.objects.none()
        if user.email:
            reported_tickets = Ticket.objects.select_related('queue').filter(
                submitter_email=user.email
            ).order_by('status')

        # Tickets in queues the user has access to
        tickets_in_queues = Ticket.objects.filter(queue__in=user_queues)
        basic_ticket_stats = calc_basic_ticket_stats(tickets_in_queues)

        # Status counts by queue
        dash_tickets = defaultdict(lambda: {
            'queue': None,
            'name': '',
            'open': 0,
            'resolved': 0,
            'closed': 0,
        })

        for ticket in tickets_in_queues.select_related('queue'):
            q_id = ticket.queue.id
            data = dash_tickets[q_id]
            data['queue'] = q_id
            data['name'] = ticket.queue.title

            if ticket.status in [Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]:
                data['open'] += 1
            elif ticket.status == Ticket.RESOLVED_STATUS:
                data['resolved'] += 1
            elif ticket.status == Ticket.CLOSED_STATUS:
                data['closed'] += 1

        return Response({
            'user_tickets': TicketSerializer(tickets, many=True).data,
            'user_tickets_closed_resolved': TicketSerializer(tickets_closed_resolved, many=True).data,
            'unassigned_tickets': TicketSerializer(unassigned_tickets, many=True).data,
            'all_tickets_reported_by_current_user': TicketSerializer(reported_tickets, many=True).data,
            'dash_tickets': list(dash_tickets.values()),
            'basic_ticket_stats': basic_ticket_stats,
        })

class DeleteTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['delete', 'get'], url_path='delete', url_name='delete_ticket')
    def delete_ticket(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)

        if not _has_access_to_queue(request.user, ticket.queue):
            raise PermissionDenied("You do not have permission to delete this ticket.")

        if request.method == 'GET':
            return Response({
                'detail': 'Confirm deletion of this ticket.',
                'ticket_id': ticket.id,
                'title': ticket.title,
            })

        ticket.delete()
        return Response({'detail': 'Ticket deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class FollowUpEditViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['put'], url_path='edit', url_name='edit_followup')
    def edit_followup(self, request, pk=None):
        old_followup = get_object_or_404(FollowUp, id=pk)
        ticket = get_object_or_404(Ticket, id=old_followup.ticket.id)

        if not _has_access_to_queue(request.user, ticket.queue):
            raise PermissionDenied("You do not have access to this queue.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        # create new followup preserving old date and user
        new_followup = FollowUp(
            title=data['title'],
            ticket=data['ticket'],
            comment=data['comment'],
            public=data['public'],
            new_status=data['new_status'],
            date=old_followup.date,
            user=old_followup.user
        )
        new_followup.save()

        # re-link attachments
        attachments = Attachment.objects.filter(followup=old_followup)
        for attachment in attachments:
            attachment.followup = new_followup
            attachment.save()

        old_followup.delete()

        return Response(FollowUpSerializer(new_followup).data, status=status.HTTP_200_OK)

class FollowUpDeleteViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        """Allow only superusers to delete followups."""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete followups.")

        followup = self.get_object()
        followup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ViewTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not _has_access_to_queue(request.user, ticket.queue):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(ticket)

        users = User.objects.filter(is_active=True)
        if helpdesk_settings.HELPDESK_STAFF_ONLY_TICKET_OWNERS:
            users = users.filter(is_staff=True)

        ticketcc_string, show_subscribe = return_ticketccstring_and_show_subscribe(request.user, ticket)

        return Response({
            'ticket': serializer.data,
            'active_users': [user.username for user in users],
            'priorities': Ticket.PRIORITY_CHOICES,
            'preset_replies': PreSetReply.objects.filter(queues=ticket.queue) | PreSetReply.objects.filter(queues__isnull=True),
            'ticketcc_string': ticketcc_string,
            'SHOW_SUBSCRIBE': show_subscribe,
        })

    @action(detail=True, methods=['post'], url_path='take')
    def take(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)
        ticket.assigned_to = request.user
        ticket.save()
        return Response({'detail': 'Ticket assigned to you.'})

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)
        _, show_subscribe = return_ticketccstring_and_show_subscribe(request.user, ticket)
        if show_subscribe:
            subscribe_staff_member_to_ticket(ticket, request.user)
            return Response({'detail': 'Subscribed to ticket.'})
        return Response({'detail': 'Already subscribed or not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status != Ticket.RESOLVED_STATUS:
            return Response({'detail': 'Ticket must be resolved before closing.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = Ticket.CLOSED_STATUS
        ticket.save()
        return Response({'detail': 'Ticket closed.'})

class UpdateTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=kwargs.get("pk"))
        if not self._can_update_ticket(request):
            return Response({"detail": "Authentication required."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        comment = data.get('comment', '')
        title = data.get('title', ticket.title)
        new_status = int(data.get('new_status', ticket.status))
        owner = int(data.get('owner', -1))
        priority = int(data.get('priority', ticket.priority))
        due_date = self._parse_due_date(data, ticket)
        public = data.get('public', False)

        if self._no_changes(request, ticket, comment, new_status, title, priority, due_date, owner):
            return Response({"detail": "No changes detected."})

        rendered_comment = self._render_comment(comment, ticket)
        followup = self._create_followup(request, ticket, rendered_comment, public)
        reassigned = self._handle_assignment(ticket, followup, owner)
        self._handle_status_change(ticket, followup, new_status)

        if title != ticket.title:
            self._log_ticket_change(followup, _('Title'), ticket.title, title)
            ticket.title = title

        if priority != ticket.priority:
            self._log_ticket_change(followup, _('Priority'), ticket.priority, priority)
            ticket.priority = priority

        if due_date != ticket.due_date:
            self._log_ticket_change(followup, _('Due on'), ticket.due_date, due_date)
            ticket.due_date = due_date

        if new_status in [Ticket.RESOLVED_STATUS, Ticket.CLOSED_STATUS]:
            ticket.resolution = rendered_comment

        followup.save()
        self._handle_attachments(request, followup)
        ticket.save()
        self._send_notifications(request, ticket, followup, public, reassigned)
        self._auto_subscribe_user(request, ticket)

        return Response(TicketSerializer(ticket).data)

    def _can_update_ticket(self, request):
        return request.user.is_authenticated and (
            request.user.is_staff or HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE)

    def _parse_due_date(self, data, ticket):
        try:
            year, month, day = int(data.get('due_date_year', 0)), int(data.get('due_date_month', 0)), int(data.get('due_date_day', 0))
            if year and month and day:
                return timezone.datetime(year, month, day)
        except Exception:
            pass
        return ticket.due_date

    def _no_changes(self, request, ticket, comment, new_status, title, priority, due_date, owner):
        current_owner_id = ticket.assigned_to.id if ticket.assigned_to else None
        return all([
            not request.FILES,
            not comment,
            new_status == ticket.status,
            title == ticket.title,
            priority == ticket.priority,
            due_date == ticket.due_date,
            (owner == -1) or (owner == 0 and not current_owner_id) or (owner == current_owner_id),
        ])

    def _render_comment(self, comment, ticket):
        context = safe_template_context(ticket)
        try:
            from django.template import engines
            template_func = engines['django'].from_string
        except ImportError:
            template_func = loader.get_template_from_string
        return template_func(comment).render(Context(context))

    def _create_followup(self, request, ticket, comment, public):
        f = FollowUp(ticket=ticket, date=timezone.now(), comment=comment, public=public)
        if request.user.is_staff or HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE:
            f.user = request.user
        return f

    def _handle_assignment(self, ticket, followup, owner):
        reassigned = False
        if owner != -1:
            if owner == 0 and ticket.assigned_to:
                followup.title = _('Unassigned')
                ticket.assigned_to = None
            elif owner and (not ticket.assigned_to or ticket.assigned_to.id != owner):
                new_user = User.objects.get(id=owner)
                followup.title = _('Assigned to %(username)s') % {'username': new_user.get_username()}
                ticket.assigned_to = new_user
                reassigned = True
        return reassigned

    def _handle_status_change(self, ticket, followup, new_status):
        if new_status != ticket.status:
            ticket.status = new_status
            followup.new_status = new_status
            followup.title = (followup.title + ' and ' if followup.title else '') + ticket.get_status_display()

    def _log_ticket_change(self, followup, field, old, new):
        TicketChange.objects.create(followup=followup, field=field, old_value=old, new_value=new)

    def _handle_attachments(self, request, followup):
        if request.FILES:
            for file in request.FILES.getlist('attachment'):
                filename = file.name.encode('ascii', 'ignore').decode('utf-8')
                a = Attachment(
                    followup=followup,
                    filename=filename,
                    mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                    size=file.size,
                )
                a.file.save(filename, file, save=False)
                a.save()

    def _send_notifications(self, request, ticket, followup, public, reassigned):
        messages_sent_to = []
        context = safe_template_context(ticket)
        context.update(resolution=ticket.resolution, comment=followup.comment)
        files = []

        # Email submitter and CCs if public and comment/status changed
        if public and (followup.comment or followup.new_status in [Ticket.RESOLVED_STATUS, Ticket.CLOSED_STATUS]):
            if followup.new_status == Ticket.RESOLVED_STATUS:
                template = 'resolved_'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template = 'closed_'
            else:
                template = 'updated_'

            # Email submitter
            if ticket.submitter_email:
                send_templated_mail(
                    template + 'submitter',
                    context,
                    recipients=ticket.submitter_email,
                    sender=ticket.queue.from_address,
                    fail_silently=True,
                    files=files
                )
                messages_sent_to.append(ticket.submitter_email)

            # Email CCs
            for cc in ticket.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        template + 'cc',
                        context,
                        recipients=cc.email_address,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                        files=files
                    )
                    messages_sent_to.append(cc.email_address)

        # Email assigned staff if assigned and different from current user
        if ticket.assigned_to and request.user != ticket.assigned_to and ticket.assigned_to.email:
            if reassigned:
                template_staff = 'assigned_owner'
            elif followup.new_status == Ticket.RESOLVED_STATUS:
                template_staff = 'resolved_owner'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template_staff = 'closed_owner'
            else:
                template_staff = 'updated_owner'

            settings = getattr(ticket.assigned_to, 'usersettings', None)
            email_on_assign = settings.settings.get('email_on_ticket_assign', False) if settings else False
            email_on_change = settings.settings.get('email_on_ticket_change', False) if settings else False

            if (not reassigned or (reassigned and email_on_assign)) or (not reassigned and email_on_change):
                send_templated_mail(
                    template_staff,
                    context,
                    recipients=ticket.assigned_to.email,
                    sender=ticket.queue.from_address,
                    fail_silently=True,
                    files=files
                )
                messages_sent_to.append(ticket.assigned_to.email)

        # Email queue-level CC if configured
        if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
            if reassigned:
                template_cc = 'assigned_cc'
            elif followup.new_status == Ticket.RESOLVED_STATUS:
                template_cc = 'resolved_cc'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template_cc = 'closed_cc'
            else:
                template_cc = 'updated_cc'

            send_templated_mail(
                template_cc,
                context,
                recipients=ticket.queue.updated_ticket_cc,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files
            )

    def _auto_subscribe_user(self, request, ticket):
        if HELPDESK_AUTO_SUBSCRIBE_ON_TICKET_RESPONSE and request.user.is_authenticated:
            ticketcc_string, show_subscribe = return_ticketccstring_and_show_subscribe(request.user, ticket)
            if show_subscribe:
                subscribe_staff_member_to_ticket(ticket, request.user)

class ReturnToTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    # ... your other methods ...

    def return_to_ticket_response(self, user, ticket):
        """
        Return JSON response with the ticket URL the frontend should navigate to,
        based on user permissions.
        """
        # Replace this check with your exact permission logic if needed
        can_update = user.is_staff or getattr(settings, 'HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE', False)

        if can_update:
            return Response({"redirect_url": ticket.get_absolute_url()})
        else:
            return Response({"redirect_url": ticket.ticket_url})

class MassUpdateViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]  # Add staff or custom permissions if needed

    @action(detail=False, methods=['post'], url_path='mass-update')
    def mass_update(self, request):
        tickets_ids = request.data.get('ticket_id', [])
        action = request.data.get('action', None)

        if not tickets_ids or not action:
            return Response({"detail": "ticket_id and action are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse action user if needed
        user = None
        if action.startswith('assign_'):
            parts = action.split('_')
            try:
                user = User.objects.get(id=int(parts[1]))
                action = 'assign'
            except (User.DoesNotExist, IndexError, ValueError):
                return Response({"detail": "Invalid user id for assignment."}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'take':
            user = request.user
            action = 'assign'

        updated_tickets = []
        for ticket in Ticket.objects.filter(id__in=tickets_ids):
            if not self._has_access_to_queue(request.user, ticket.queue):
                continue

            followup = None

            if action == 'assign' and ticket.assigned_to != user:
                ticket.assigned_to = user
                ticket.save()
                followup = FollowUp(
                    ticket=ticket,
                    date=timezone.now(),
                    title=_('Assigned to %(username)s in bulk update') % {'username': user.get_username()},
                    public=True,
                    user=request.user
                )
                followup.save()

            elif action == 'unassign' and ticket.assigned_to is not None:
                ticket.assigned_to = None
                ticket.save()
                followup = FollowUp(
                    ticket=ticket,
                    date=timezone.now(),
                    title=_('Unassigned in bulk update'),
                    public=True,
                    user=request.user
                )
                followup.save()

            elif action == 'close' and ticket.status != Ticket.CLOSED_STATUS:
                ticket.status = Ticket.CLOSED_STATUS
                ticket.save()
                followup = FollowUp(
                    ticket=ticket,
                    date=timezone.now(),
                    title=_('Closed in bulk update'),
                    public=False,
                    user=request.user,
                    new_status=Ticket.CLOSED_STATUS
                )
                followup.save()

            elif action == 'close_public' and ticket.status != Ticket.CLOSED_STATUS:
                ticket.status = Ticket.CLOSED_STATUS
                ticket.save()
                followup = FollowUp(
                    ticket=ticket,
                    date=timezone.now(),
                    title=_('Closed in bulk update'),
                    public=True,
                    user=request.user,
                    new_status=Ticket.CLOSED_STATUS
                )
                followup.save()

                # Email sending logic
                context = safe_template_context(ticket)
                context.update(resolution=ticket.resolution, queue=ticket.queue)

                messages_sent_to = []

                if ticket.submitter_email:
                    send_templated_mail(
                        'closed_submitter',
                        context,
                        recipients=ticket.submitter_email,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                    )
                    messages_sent_to.append(ticket.submitter_email)

                for cc in ticket.ticketcc_set.all():
                    if cc.email_address not in messages_sent_to:
                        send_templated_mail(
                            'closed_submitter',
                            context,
                            recipients=cc.email_address,
                            sender=ticket.queue.from_address,
                            fail_silently=True,
                        )
                        messages_sent_to.append(cc.email_address)

                if (ticket.assigned_to and request.user != ticket.assigned_to
                        and ticket.assigned_to.email and ticket.assigned_to.email not in messages_sent_to):
                    send_templated_mail(
                        'closed_owner',
                        context,
                        recipients=ticket.assigned_to.email,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                    )
                    messages_sent_to.append(ticket.assigned_to.email)

                if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
                    send_templated_mail(
                        'closed_cc',
                        context,
                        recipients=ticket.queue.updated_ticket_cc,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                    )

            elif action == 'delete':
                ticket.delete()
                continue

            if followup:
                updated_tickets.append(followup.ticket)

        # Serialize updated tickets for response (optional)
        serializer = TicketSerializer(updated_tickets, many=True)
        return Response({
            "detail": "Mass update completed.",
            "updated_tickets": serializer.data
        })

class TicketListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing tickets with filtering, searching, sorting, and pagination.
    Staff users only.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    class Pagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = Pagination

    def _get_user_queues(self, user):
        # Replace this with your actual method for retrieving accessible queues
        from helpdesk.views.staff import _get_user_queues
        return _get_user_queues(user)

    def filter_and_sort_tickets(self, base_tickets, query_params):
        qs = base_tickets

        # Apply filtering
        for field, value in query_params.get('filtering', {}).items():
            qs = qs.filter(**{field: value})

        # Keyword search
        search_string = query_params.get('search_string')
        if search_string:
            qs = qs.filter(
                Q(title__icontains=search_string) |
                Q(description__icontains=search_string)
            )

        # Sorting
        sort_field = query_params.get('sorting') or 'created'
        reverse = query_params.get('sortreverse', False)
        order_by = f"-{sort_field}" if reverse else sort_field
        qs = qs.order_by(order_by)

        return qs

    def list(self, request, *args, **kwargs):
        user_queues = self._get_user_queues(request.user)
        base_tickets = Ticket.objects.filter(queue__in=user_queues)

        # Construct query parameters
        query_params = {
            'filtering': {},
            'sorting': None,
            'sortreverse': False,
            'search_string': None,
        }

        # Filtering
        if queues := request.GET.getlist('queue'):
            try:
                query_params['filtering']['queue__id__in'] = [int(q) for q in queues]
            except ValueError:
                pass

        if owners := request.GET.getlist('assigned_to'):
            try:
                query_params['filtering']['assigned_to__id__in'] = [int(o) for o in owners]
            except ValueError:
                pass

        if statuses := request.GET.getlist('status'):
            try:
                query_params['filtering']['status__in'] = [int(s) for s in statuses]
            except ValueError:
                pass

        if date_from := request.GET.get('date_from'):
            query_params['filtering']['created__gte'] = date_from

        if date_to := request.GET.get('date_to'):
            query_params['filtering']['created__lte'] = date_to

        # Keyword search
        if q := request.GET.get('q'):
            query_params['search_string'] = q

        # Sorting
        sort = request.GET.get('sort')
        if sort in ('status', 'assigned_to', 'created', 'title', 'queue', 'priority'):
            query_params['sorting'] = sort
        else:
            query_params['sorting'] = 'created'

        sortreverse = request.GET.get('sortreverse')
        query_params['sortreverse'] = sortreverse in ['true', '1', 'yes', 'on']

        # Apply ORM filters
        try:
            ticket_qs = self.filter_and_sort_tickets(base_tickets, query_params)
        except ValidationError:
            ticket_qs = base_tickets.filter(status__in=[1, 2, 3]).order_by('created')

        page = self.paginate_queryset(ticket_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(ticket_qs, many=True)
        return Response(serializer.data)

class EditTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser, HasQueueAccess]

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(queue__in=_get_user_queues(user))

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()

        # Optional: Recheck queue access
        if not _has_access_to_queue(request.user, ticket.queue):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(ticket, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

class TicketCreateViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAdminUser]  # staff_member_required equivalent

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketChangeSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save(user=self.request.user)

        if not _has_access_to_queue(self.request.user, ticket.queue):
            # You can customize this behavior: e.g., raise PermissionDenied
            return Response({'detail': 'No access to queue.'}, status=status.HTTP_403_FORBIDDEN)
        return ticket

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        ticket = self.perform_create(serializer)
        if isinstance(ticket, Response):  # permission denied response
            return ticket
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

class HoldUnHoldTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]  # staff_member_required equivalent

    @action(detail=True, methods=['post'], url_path='hold')
    def hold_ticket(self, request, pk=None):
        return self._set_hold_status(request, pk, hold=True)

    @action(detail=True, methods=['post'], url_path='unhold')
    def unhold_ticket(self, request, pk=None):
        return self._set_hold_status(request, pk, hold=False)

    def _set_hold_status(self, request, pk, hold=True):
        ticket = get_object_or_404(Ticket, pk=pk)

        if not _has_access_to_queue(request.user, ticket.queue):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        ticket.on_hold = hold
        ticket.save()

        FollowUp.objects.create(
            ticket=ticket,
            user=request.user,
            title=_('Ticket placed on hold') if hold else _('Ticket taken off hold'),
            date=timezone.now(),
            public=True,
        )

        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)

class RssListViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    permission_classes = [IsAdminUser]

class ReportIndexViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]  # Equivalent to staff_member_required

    def list(self, request):
        number_tickets = Ticket.objects.count()
        saved_query = request.GET.get('saved_query', None)
        data = {
            'number_tickets': number_tickets,
            'saved_query': saved_query,
        }
        serializer = TicketSerializer(data)
        return Response(serializer.data)

class RunReportViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        count = self.queryset.count()
        saved_query = request.GET.get('saved_query')
        return Response({
            'number_tickets': count,
            'saved_query': saved_query,
        })

    @action(detail=False, methods=['get'], url_path='run/(?P<report>[^/.]+)')
    def run_report(self, request, report=None):
        if Ticket.objects.count() == 0 or report not in (
            'queuemonth', 'usermonth', 'queuestatus', 'queuepriority',
            'userstatus', 'userpriority', 'userqueue', 'daysuntilticketclosedbymonth'):
            return Response({'error': 'Invalid report'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().select_related().filter(
            queue__in=get_user_queues(request.user)
        )

        saved_query_id = request.GET.get('saved_query')
        if saved_query_id:
            try:
                saved_query = SavedSearch.objects.get(pk=saved_query_id)
                if not (saved_query.shared or saved_query.user == request.user):
                    return Response({'error': 'Access denied to saved query'}, status=status.HTTP_403_FORBIDDEN)
                import json
                from helpdesk.lib import b64decode
                query_params = json.loads(b64decode(str(saved_query.query)))
                queryset = apply_query(queryset, query_params)
            except SavedSearch.DoesNotExist:
                return Response({'error': 'Saved query not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception:
                return Response({'error': 'Invalid query encoding'}, status=status.HTTP_400_BAD_REQUEST)

        # Report logic via utility function
        report_data = build_report_table(queryset, report, request.user)

        return Response(report_data)

class SavedQueryViewSet(viewsets.ModelViewSet):
    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        # Return URL with query param just like the original view
        redirect_url = f"{request.build_absolute_uri('/helpdesk/list')}?saved_query={serializer.instance.id}"
        return Response({'redirect_url': redirect_url}, status=status.HTTP_201_CREATED)

class DeleteSavedQueryViewSet(viewsets.ModelViewSet):
    queryset = SavedSearch.objects.all()
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Ensure users only see their own saved queries
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied("You do not have permission to delete this saved query.")
        self.perform_destroy(instance)
        redirect_url = reverse('helpdesk_list')
        return Response({'redirect_url': redirect_url}, status=status.HTTP_204_NO_CONTENT)

class UserSettingsViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        try:
            return UserSettings.objects.get(user=self.request.user)
        except UserSettings.DoesNotExist:
            raise NotFound("User settings not found")

    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)

class IgnoreEmailViewSet(viewsets.ModelViewSet):
    queryset = IgnoreEmail.objects.all()
    serializer_class = IgnoreEmailSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get', 'post'], url_path='confirm-delete')
    def confirm_delete(self, request, pk=None):
        ignore = get_object_or_404(IgnoreEmail, pk=pk)

        if request.method == 'POST':
            ignore.delete()
            # Redirect to list view URL - adjust name accordingly
            return redirect(reverse('ignore-emails-list')) 

        # GET request - render confirmation template
        return render(request, 'helpdesk/email_ignore_del.html', {'ignore': ignore})

class TicketCCViewSet(viewsets.ModelViewSet):
    serializer_class = TicketCCSerializer

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        # Access control check
        if not _has_access_to_queue(self.request.user, ticket.queue):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No access to this ticket's queue.")

        return TicketCC.objects.filter(ticket=ticket)

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if not _has_access_to_queue(self.request.user, ticket.queue):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No access to this ticket's queue.")

        serializer.save(ticket=ticket)

    @action(detail=True, methods=['post'])
    def delete_cc(self, request, ticket_id=None, pk=None):
        cc = get_object_or_404(TicketCC, ticket__id=ticket_id, id=pk)

        if not _has_access_to_queue(request.user, cc.ticket.queue):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No access to this ticket's queue.")

        cc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TicketCCViewSet(viewsets.ModelViewSet):
    serializer_class = TicketCCSerializer

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        # Check user access to the queue of the ticket
        if not _has_access_to_queue(self.request.user, ticket.queue):
            raise PermissionDenied("You do not have access to this ticket's queue.")

        return TicketCC.objects.filter(ticket=ticket)

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if not _has_access_to_queue(self.request.user, ticket.queue):
            raise PermissionDenied("You do not have access to this ticket's queue.")

        serializer.save(ticket=ticket)

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if not _has_access_to_queue(self.request.user, ticket.queue):
            raise PermissionDenied("You do not have access to this ticket's queue.")

        # Return attachments only for this ticket
        return Attachment.objects.filter(ticket=ticket)

    def destroy(self, request, *args, **kwargs):
        # Overriding destroy to add permission check
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if not _has_access_to_queue(request.user, ticket.queue):
            raise PermissionDenied("You do not have access to this ticket's queue.")

        return super().destroy(request, *args, **kwargs)