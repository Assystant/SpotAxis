"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/staff.py - The bulk of the application - provides most business logic and
                 renders all staff-facing views.
"""

from __future__ import absolute_import
from datetime import datetime, timedelta

from django import VERSION
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django.core import paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dates import MONTHS_3
from django.utils.translation import gettext as _
from django.utils.html import escape
from django import forms

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

User = get_user_model()


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
    """
    Return the list of Queues the given user can access.

    This function checks for `HELPDESK_ENABLE_PER_QUEUE_STAFF_PERMISSION` in settings.
    If enabled, it filters queues based on the user's assigned permissions unless they are a superuser.

    Args:
        user (User): A Django User object.
    param user: 
        The User (the class should have the has_perm method)
    Returns:
        QuerySet: A queryset of Queue objects the user is permitted to access.
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


def dashboard(request):
    """
    A quick summary overview for users: A list of their own tickets, a table
    showing ticket counts by queue/status, and a list of unassigned tickets
    with options for them to 'Take' ownership of said tickets.
    """

    # open & reopened tickets, assigned to current user
    tickets = Ticket.objects.select_related('queue').filter(
            assigned_to=request.user,
        ).exclude(
            status__in=[Ticket.CLOSED_STATUS, Ticket.RESOLVED_STATUS],
        )

    # closed & resolved tickets, assigned to current user
    tickets_closed_resolved = Ticket.objects.select_related('queue').filter(
            assigned_to=request.user,
            status__in=[Ticket.CLOSED_STATUS, Ticket.RESOLVED_STATUS])

    user_queues = _get_user_queues(request.user)

    unassigned_tickets = Ticket.objects.select_related('queue').filter(
            assigned_to__isnull=True,
            queue__in=user_queues
        ).exclude(
            status=Ticket.CLOSED_STATUS,
        )

    # all tickets, reported by current user
    all_tickets_reported_by_current_user = ''
    email_current_user = request.user.email
    if email_current_user:
        all_tickets_reported_by_current_user = Ticket.objects.select_related('queue').filter(
            submitter_email=email_current_user,
        ).order_by('status')

    tickets_in_queues = Ticket.objects.filter(
                queue__in=user_queues,
            )
    basic_ticket_stats = calc_basic_ticket_stats(tickets_in_queues)

    # The following query builds a grid of queues & ticket statuses,
    # to be displayed to the user. EG:
    #          Open  Resolved
    # Queue 1    10     4
    # Queue 2     4    12

    queues = _get_user_queues(request.user).values_list('id', flat=True)

    from_clause = """FROM    helpdesk_ticket t,
                    helpdesk_queue q"""
    if queues:
        where_clause = """WHERE   q.id = t.queue_id AND
                        q.id IN (%s)""" % (",".join(("%d" % pk for pk in queues)))
    else:
        where_clause = """WHERE   q.id = t.queue_id"""

    cursor = connection.cursor()
    cursor.execute("""
        SELECT      q.id as queue,
                    q.title AS name,
                    COUNT(CASE t.status WHEN '1' THEN t.id WHEN '2' THEN t.id END) AS open,
                    COUNT(CASE t.status WHEN '3' THEN t.id END) AS resolved,
                    COUNT(CASE t.status WHEN '4' THEN t.id END) AS closed
            %s
            %s
            GROUP BY queue, name
            ORDER BY q.id;
    """ % (from_clause, where_clause))

    dash_tickets = query_to_dict(cursor.fetchall(), cursor.description)

    return render(request, 'helpdesk/dashboard.html', {
        'user_tickets': tickets,
        'user_tickets_closed_resolved': tickets_closed_resolved,
        'unassigned_tickets': unassigned_tickets,
        'all_tickets_reported_by_current_user': all_tickets_reported_by_current_user,
        'dash_tickets': dash_tickets,
        'basic_ticket_stats': basic_ticket_stats,
    })
dashboard = staff_member_required(dashboard)


def delete_ticket(request, ticket_id):
    """
    Delete a ticket after confirmation.

    This view ensures that the requesting user has access to the ticket's queue.

    Args:
        request (HttpRequest): The incoming request.
        ticket_id (int): The ID of the ticket to be deleted.

    Returns:
        HttpResponse: Redirects to homepage or confirmation page.

    Raises:
        PermissionDenied: If user is unauthorized to delete the ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    if request.method == 'GET':
        return render(request, 'helpdesk/delete_ticket.html', {
            'ticket': ticket,
        })
    else:
        ticket.delete()
        return HttpResponseRedirect(reverse('helpdesk_home'))
delete_ticket = staff_member_required(delete_ticket)


def followup_edit(request, ticket_id, followup_id):
    """
    Allows staff to edit a follow-up on a ticket.

    On GET:
        Displays a pre-filled form.
    On POST:
        Saves updated follow-up and links old attachments to new record.

    Args:
        request (HttpRequest)
        ticket_id (int)
        followup_id (int)

    Returns:
        HttpResponse: Renders form or redirects to ticket view."""
    followup = get_object_or_404(FollowUp, id=followup_id)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()
    if request.method == 'GET':
        form = EditFollowUpForm(initial={
            'title': escape(followup.title),
            'ticket': followup.ticket,
            'comment': escape(followup.comment),
            'public': followup.public,
            'new_status': followup.new_status,
        })

        ticketcc_string, show_subscribe = \
            return_ticketccstring_and_show_subscribe(request.user, ticket)

        return render(request, 'helpdesk/followup_edit.html', {
            'followup': followup,
            'ticket': ticket,
            'form': form,
            'ticketcc_string': ticketcc_string,
        })
    elif request.method == 'POST':
        form = EditFollowUpForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            _ticket = form.cleaned_data['ticket']
            comment = form.cleaned_data['comment']
            public = form.cleaned_data['public']
            new_status = form.cleaned_data['new_status']
            # will save previous date
            old_date = followup.date
            new_followup = FollowUp(title=title, date=old_date, ticket=_ticket, comment=comment, public=public, new_status=new_status, )
            # keep old user if one did exist before.
            if followup.user:
                new_followup.user = followup.user
            new_followup.save()
            # get list of old attachments & link them to new_followup
            attachments = Attachment.objects.filter(followup = followup)
            for attachment in attachments:
                attachment.followup = new_followup
                attachment.save()
            # delete old followup
            followup.delete()
        return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket.id]))
followup_edit = staff_member_required(followup_edit)


def followup_delete(request, ticket_id, followup_id):
    """
    Allows superusers to delete a follow-up.

    Args:
        request (HttpRequest)
        ticket_id (int)
        followup_id (int)

    Returns:
        HttpResponse: Redirects to ticket view.

    Notes:
        Only superusers can perform this action.
    """

    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket.id]))

    followup = get_object_or_404(FollowUp, id=followup_id)
    followup.delete()
    return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket.id]))
followup_delete = staff_member_required(followup_delete)


def view_ticket(request, ticket_id):
    """
    View details of a ticket and perform actions like:
        - Take ownership
        - Subscribe to updates
        - Close resolved tickets

    Args:
        request (HttpRequest)
        ticket_id (int)

    Returns:
        HttpResponse: Renders ticket detail page.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    if 'take' in request.GET:
        # Allow the user to assign the ticket to themselves whilst viewing it.

        # Trick the update_ticket() view into thinking it's being called with
        # a valid POST.
        request.POST = {
            'owner': request.user.id,
            'public': 1,
            'title': ticket.title,
            'comment': ''
        }
        return update_ticket(request, ticket_id)

    if 'subscribe' in request.GET:
        # Allow the user to subscribe him/herself to the ticket whilst viewing it.
        ticket_cc, show_subscribe = \
            return_ticketccstring_and_show_subscribe(request.user, ticket)
        if show_subscribe:
            subscribe_staff_member_to_ticket(ticket, request.user)
            return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket.id]))

    if 'close' in request.GET and ticket.status == Ticket.RESOLVED_STATUS:
        if not ticket.assigned_to:
            owner = 0
        else:
            owner = ticket.assigned_to.id

        # Trick the update_ticket() view into thinking it's being called with
        # a valid POST.
        request.POST = {
            'new_status': Ticket.CLOSED_STATUS,
            'public': 1,
            'owner': owner,
            'title': ticket.title,
            'comment': _('Accepted resolution and closed ticket'),
            }

        return update_ticket(request, ticket_id)

    if helpdesk_settings.HELPDESK_STAFF_ONLY_TICKET_OWNERS:
        users = User.objects.filter(is_active=True, is_staff=True).order_by(User.USERNAME_FIELD)
    else:
        users = User.objects.filter(is_active=True).order_by(User.USERNAME_FIELD)


    # TODO: shouldn't this template get a form to begin with?
    form = TicketForm(initial={'due_date': ticket.due_date})

    ticketcc_string, show_subscribe = \
        return_ticketccstring_and_show_subscribe(request.user, ticket)

    return render(request, 'helpdesk/ticket.html', {
        'ticket': ticket,
        'form': form,
        'active_users': users,
        'priorities': Ticket.PRIORITY_CHOICES,
        'preset_replies': PreSetReply.objects.filter(
            Q(queues=ticket.queue) | Q(queues__isnull=True)),
        'ticketcc_string': ticketcc_string,
        'SHOW_SUBSCRIBE': show_subscribe,
    })
view_ticket = staff_member_required(view_ticket)


def return_ticketccstring_and_show_subscribe(user, ticket):
    """
    Builds a string of CC'd users and checks if the user can subscribe.

    Args:
        user (User): The current logged-in user.
        ticket (Ticket): Ticket object.

    Returns:
        tuple: (ticketcc_string (str), show_subscribe (bool))"""
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
    """
    Subscribes a staff user to a ticket's updates.

    Args:
        ticket (Ticket)
        user (User)

    Returns:
        None
    """
    ticketcc = TicketCC(
        ticket=ticket,
        user=user,
        can_view=True,
        can_update=True,
    )
    ticketcc.save()


def update_ticket(request, ticket_id, public=False):
    """
    Update a ticket with new data such as status, assignment, comment, and attachments.

    This view processes POST requests containing updates for a specific ticket.
    It handles permission checks, form parsing, status changes, email notifications,
    attachment saving, and audit logging via follow-ups.

    Parameters:
    - request: The HTTP request containing update data.
    - ticket_id: The ID of the ticket to update.
    - public (bool): Indicates whether the update is public or internal.

    Returns:
    - HttpResponseRedirect to the updated ticket's detail view.
    """

    if not (public or (
            request.user.is_authenticated and
            request.user.is_active and (
                request.user.is_staff or
                helpdesk_settings.HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE))):
        return HttpResponseRedirect('%s?next=%s' %
                                    (reverse('login'), request.path))

    ticket = get_object_or_404(Ticket, id=ticket_id)

    comment = request.POST.get('comment', '')
    new_status = int(request.POST.get('new_status', ticket.status))
    title = request.POST.get('title', '')
    public = request.POST.get('public', False)
    owner = int(request.POST.get('owner', -1))
    priority = int(request.POST.get('priority', ticket.priority))
    due_date_year = int(request.POST.get('due_date_year', 0))
    due_date_month = int(request.POST.get('due_date_month', 0))
    due_date_day = int(request.POST.get('due_date_day', 0))

    if not (due_date_year and due_date_month and due_date_day):
        due_date = ticket.due_date
    else:
        if ticket.due_date:
            due_date = ticket.due_date
        else:
            due_date = timezone.now()
        due_date = due_date.replace(due_date_year, due_date_month, due_date_day)

    no_changes = all([
        not request.FILES,
        not comment,
        new_status == ticket.status,
        title == ticket.title,
        priority == int(ticket.priority),
        due_date == ticket.due_date,
        (owner == -1) or (not owner and not ticket.assigned_to) or
        (owner and User.objects.get(id=owner) == ticket.assigned_to),
    ])
    if no_changes:
        return return_to_ticket(request.user, helpdesk_settings, ticket)

    # We need to allow the 'ticket' and 'queue' contexts to be applied to the
    # comment.
    from django.template import loader, Context
    context = safe_template_context(ticket)
    # this line sometimes creates problems if code is sent as a comment.
    # if comment contains some django code, like "why does {% if bla %} crash",
    # then the following line will give us a crash, since django expects {% if %}
    # to be closed with an {% endif %} tag.

    # get_template_from_string was removed in Django 1.8
    # http://django.readthedocs.org/en/1.8.x/ref/templates/upgrading.html
    try:
        from django.template import engines
        template_func = engines['django'].from_string
    except ImportError:  # occurs in django < 1.8
        template_func = loader.get_template_from_string

    # RemovedInDjango110Warning: render() must be called with a dict, not a Context.
    if VERSION < (1, 8):
        context = Context(context)

    comment = template_func(comment).render(context)

    if owner == -1 and ticket.assigned_to:
        owner = ticket.assigned_to.id

    f = FollowUp(ticket=ticket, date=timezone.now(), comment=comment)

    if request.user.is_staff or helpdesk_settings.HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE:
        f.user = request.user

    f.public = public

    reassigned = False

    if owner != -1:
        if owner != 0 and ((ticket.assigned_to and owner != ticket.assigned_to.id) or not ticket.assigned_to):
            new_user = User.objects.get(id=owner)
            f.title = _('Assigned to %(username)s') % {
                'username': new_user.get_username(),
                }
            ticket.assigned_to = new_user
            reassigned = True
        # user changed owner to 'unassign'
        elif owner == 0 and ticket.assigned_to is not None:
            f.title = _('Unassigned')
            ticket.assigned_to = None

    if new_status != ticket.status:
        ticket.status = new_status
        ticket.save()
        f.new_status = new_status
        if f.title:
            f.title += ' and %s' % ticket.get_status_display()
        else:
            f.title = '%s' % ticket.get_status_display()

    if not f.title:
        if f.comment:
            f.title = _('Comment')
        else:
            f.title = _('Updated')

    f.save()

    files = []
    if request.FILES:
        import mimetypes
        for file in request.FILES.getlist('attachment'):
            filename = file.name.encode('ascii', 'ignore')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                size=file.size,
                )
            a.file.save(filename, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append([a.filename, a.file])

    if title != ticket.title:
        c = TicketChange(
            followup=f,
            field=_('Title'),
            old_value=ticket.title,
            new_value=title,
            )
        c.save()
        ticket.title = title

    if priority != ticket.priority:
        c = TicketChange(
            followup=f,
            field=_('Priority'),
            old_value=ticket.priority,
            new_value=priority,
            )
        c.save()
        ticket.priority = priority

    if due_date != ticket.due_date:
        c = TicketChange(
            followup=f,
            field=_('Due on'),
            old_value=ticket.due_date,
            new_value=due_date,
            )
        c.save()
        ticket.due_date = due_date

    if new_status in [ Ticket.RESOLVED_STATUS, Ticket.CLOSED_STATUS ]:
        if new_status == Ticket.RESOLVED_STATUS or ticket.resolution is None:
            ticket.resolution = comment

    messages_sent_to = []

    # ticket might have changed above, so we re-instantiate context with the
    # (possibly) updated ticket.
    context = safe_template_context(ticket)
    context.update(
        resolution=ticket.resolution,
        comment=f.comment,
        )

    if public and (f.comment or (
                f.new_status in (Ticket.RESOLVED_STATUS,
                                 Ticket.CLOSED_STATUS))):
        if f.new_status == Ticket.RESOLVED_STATUS:
            template = 'resolved_'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template = 'closed_'
        else:
            template = 'updated_'

        template_suffix = 'submitter'

        if ticket.submitter_email:
            send_templated_mail(
                template + template_suffix,
                context,
                recipients=ticket.submitter_email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(ticket.submitter_email)

        template_suffix = 'cc'

        for cc in ticket.ticketcc_set.all():
            if cc.email_address not in messages_sent_to:
                send_templated_mail(
                    template + template_suffix,
                    context,
                    recipients=cc.email_address,
                    sender=ticket.queue.from_address,
                    fail_silently=True,
                    files=files,
                    )
                messages_sent_to.append(cc.email_address)

    if ticket.assigned_to and \
            request.user != ticket.assigned_to and \
            ticket.assigned_to.email and \
            ticket.assigned_to.email not in messages_sent_to:
        # We only send e-mails to staff members if the ticket is updated by
        # another user. The actual template varies, depending on what has been
        # changed.
        if reassigned:
            template_staff = 'assigned_owner'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_staff = 'resolved_owner'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template_staff = 'closed_owner'
        else:
            template_staff = 'updated_owner'

        if (not reassigned or
                (reassigned and
                    ticket.assigned_to.usersettings.settings.get(
                        'email_on_ticket_assign', False))) or \
            (not reassigned and
                ticket.assigned_to.usersettings.settings.get(
                    'email_on_ticket_change', False)):
            send_templated_mail(
                template_staff,
                context,
                recipients=ticket.assigned_to.email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(ticket.assigned_to.email)

    if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
        if reassigned:
            template_cc = 'assigned_cc'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_cc = 'resolved_cc'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template_cc = 'closed_cc'
        else:
            template_cc = 'updated_cc'

        send_templated_mail(
            template_cc,
            context,
            recipients=ticket.queue.updated_ticket_cc,
            sender=ticket.queue.from_address,
            fail_silently=True,
            files=files,
            )

    ticket.save()

    # auto subscribe user if enabled
    if helpdesk_settings.HELPDESK_AUTO_SUBSCRIBE_ON_TICKET_RESPONSE and request.user.is_authenticated:
        ticketcc_string, SHOW_SUBSCRIBE = return_ticketccstring_and_show_subscribe(request.user, ticket)
        if SHOW_SUBSCRIBE:
            subscribe_staff_member_to_ticket(ticket, request.user)

    return return_to_ticket(request.user, helpdesk_settings, ticket)


def return_to_ticket(user, helpdesk_settings, ticket):
    """
    Redirect the user to the appropriate view of the ticket based on their role.

    Parameters:
    - user: The currently logged-in user.
    - helpdesk_settings: Settings object containing application configurations.
    - ticket: The ticket object to redirect to.

    Returns:
    - HttpResponseRedirect to either the staff or public ticket view.
    """


    if user.is_staff or helpdesk_settings.HELPDESK_ALLOW_NON_STAFF_TICKET_UPDATE:
        return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        return HttpResponseRedirect(ticket.ticket_url)


def mass_update(request):
    """
    Perform a bulk update on a list of tickets based on a selected action.

    This view handles multiple actions like assign, unassign, close, and delete
    on selected tickets. It ensures proper permission checks and sends appropriate
    email notifications.

    Parameters:
    - request: The HTTP POST request containing ticket IDs and action.

    Returns:
    - HttpResponseRedirect to the ticket list view.
    """

    tickets = request.POST.getlist('ticket_id')
    action = request.POST.get('action', None)
    if not (tickets and action):
        return HttpResponseRedirect(reverse('helpdesk_list'))

    if action.startswith('assign_'):
        parts = action.split('_')
        user = User.objects.get(id=parts[1])
        action = 'assign'
    elif action == 'take':
        user = request.user
        action = 'assign'

    for t in Ticket.objects.filter(id__in=tickets):
        if not _has_access_to_queue(request.user, t.queue):
            continue

        if action == 'assign' and t.assigned_to != user:
            t.assigned_to = user
            t.save()
            f = FollowUp(ticket=t,
                         date=timezone.now(),
                         title=_('Assigned to %(username)s in bulk update' % {
                             'username': user.get_username()
                         }),
                         public=True,
                         user=request.user)
            f.save()
        elif action == 'unassign' and t.assigned_to is not None:
            t.assigned_to = None
            t.save()
            f = FollowUp(ticket=t,
                         date=timezone.now(),
                         title=_('Unassigned in bulk update'),
                         public=True,
                         user=request.user)
            f.save()
        elif action == 'close' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(ticket=t,
                         date=timezone.now(),
                         title=_('Closed in bulk update'),
                         public=False,
                         user=request.user,
                         new_status=Ticket.CLOSED_STATUS)
            f.save()
        elif action == 'close_public' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(ticket=t,
                         date=timezone.now(),
                         title=_('Closed in bulk update'),
                         public=True,
                         user=request.user,
                         new_status=Ticket.CLOSED_STATUS)
            f.save()
            # Send email to Submitter, Owner, Queue CC
            context = safe_template_context(t)
            context.update(resolution=t.resolution,
                           queue=t.queue)

            messages_sent_to = []

            if t.submitter_email:
                send_templated_mail(
                    'closed_submitter',
                    context,
                    recipients=t.submitter_email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )
                messages_sent_to.append(t.submitter_email)

            for cc in t.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        'closed_submitter',
                        context,
                        recipients=cc.email_address,
                        sender=t.queue.from_address,
                        fail_silently=True,
                        )
                    messages_sent_to.append(cc.email_address)

            if t.assigned_to and \
                    request.user != t.assigned_to and \
                    t.assigned_to.email and \
                    t.assigned_to.email not in messages_sent_to:
                send_templated_mail(
                    'closed_owner',
                    context,
                    recipients=t.assigned_to.email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )
                messages_sent_to.append(t.assigned_to.email)

            if t.queue.updated_ticket_cc and \
                    t.queue.updated_ticket_cc not in messages_sent_to:
                send_templated_mail(
                    'closed_cc',
                    context,
                    recipients=t.queue.updated_ticket_cc,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )

        elif action == 'delete':
            t.delete()

    return HttpResponseRedirect(reverse('helpdesk_list'))
mass_update = staff_member_required(mass_update)


def ticket_list(request):
    """
    Display a paginated list of tickets accessible to the requesting user.

    Retrieves tickets filtered by queues the user has permission to view.
    Supports filtering by status, assigned user, creation dates, keyword searches,
    sorting, and saved queries. Handles redirection for direct ticket number searches.
    Also shows a search notice for SQLite users.

    Parameters:
    - request: The HTTP GET request containing query parameters for filtering, sorting, and pagination.

    Returns:
    - Rendered HTML response displaying the ticket list page with applied filters and pagination.
    """
    context = {}

    user_queues = _get_user_queues(request.user)
    # Prefilter the allowed tickets
    base_tickets = Ticket.objects.filter(queue__in=user_queues)

    # Query_params will hold a dictionary of parameters relating to
    # a query, to be saved if needed:
    query_params = {
        'filtering': {},
        'sorting': None,
        'sortreverse': False,
        'keyword': None,
        'search_string': None,
        }

    from_saved_query = False

    # If the user is coming from the header/navigation search box, lets' first
    # look at their query to see if they have entered a valid ticket number. If
    # they have, just redirect to that ticket number. Otherwise, we treat it as
    # a keyword search.

    if request.GET.get('search_type', None) == 'header':
        query = request.GET.get('q')
        filter = None
        if query.find('-') > 0:
            try:
                queue, id = Ticket.queue_and_id_from_query(query)
                id = int(id)
            except ValueError:
                id = None

            if id:
                filter = {'queue__slug': queue, 'id': id}
        else:
            try:
                query = int(query)
            except ValueError:
                query = None

            if query:
                filter = {'id': int(query)}

        if filter:
            try:
                ticket = base_tickets.get(**filter)
                return HttpResponseRedirect(ticket.staff_url)
            except Ticket.DoesNotExist:
                # Go on to standard keyword searching
                pass

    saved_query = None
    if request.GET.get('saved_query', None):
        from_saved_query = True
        try:
            saved_query = SavedSearch.objects.get(pk=request.GET.get('saved_query'))
        except SavedSearch.DoesNotExist:
            return HttpResponseRedirect(reverse('helpdesk_list'))
        if not (saved_query.shared or saved_query.user == request.user):
            return HttpResponseRedirect(reverse('helpdesk_list'))

        import json
        from helpdesk.lib import b64decode
        try:
            query_params = json.loads(b64decode(str(saved_query.query)))
        except ValueError:
            # Query deserialization failed. (E.g. was a pickled query)
            return HttpResponseRedirect(reverse('helpdesk_list'))

    elif not ('queue' in request.GET
              or 'assigned_to' in request.GET
              or 'status' in request.GET
              or 'q' in request.GET
              or 'sort' in request.GET
              or 'sortreverse' in request.GET
              ):

        # Fall-back if no querying is being done, force the list to only
        # show open/reopened/resolved (not closed) cases sorted by creation
        # date.

        query_params = {
            'filtering': {'status__in': [1, 2, 3]},
            'sorting': 'created',
        }
    else:
        queues = request.GET.getlist('queue')
        if queues:
            try:
                queues = [int(q) for q in queues]
                query_params['filtering']['queue__id__in'] = queues
            except ValueError:
                pass

        owners = request.GET.getlist('assigned_to')
        if owners:
            try:
                owners = [int(u) for u in owners]
                query_params['filtering']['assigned_to__id__in'] = owners
            except ValueError:
                pass

        statuses = request.GET.getlist('status')
        if statuses:
            try:
                statuses = [int(s) for s in statuses]
                query_params['filtering']['status__in'] = statuses
            except ValueError:
                pass

        date_from = request.GET.get('date_from')
        if date_from:
            query_params['filtering']['created__gte'] = date_from

        date_to = request.GET.get('date_to')
        if date_to:
            query_params['filtering']['created__lte'] = date_to

        # KEYWORD SEARCHING
        q = request.GET.get('q', None)

        if q:
            context = dict(context, query=q)
            query_params['search_string'] = q

        # SORTING
        sort = request.GET.get('sort', None)
        if sort not in ('status', 'assigned_to', 'created', 'title', 'queue', 'priority'):
            sort = 'created'
        query_params['sorting'] = sort

        sortreverse = request.GET.get('sortreverse', None)
        query_params['sortreverse'] = sortreverse

    tickets = base_tickets.select_related()

    try:
        ticket_qs = apply_query(tickets, query_params)
    except ValidationError:
        # invalid parameters in query, return default query
        query_params = {
            'filtering': {'status__in': [1, 2, 3]},
            'sorting': 'created',
        }
        ticket_qs = apply_query(tickets, query_params)

    ticket_paginator = paginator.Paginator(
        ticket_qs,
        request.user.usersettings.settings.get('tickets_per_page') or 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tickets = ticket_paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tickets = ticket_paginator.page(ticket_paginator.num_pages)

    search_message = ''
    if 'query' in context and settings.DATABASES['default']['ENGINE'].endswith('sqlite'):
        search_message = _(
            '<p><strong>Note:</strong> Your keyword search is case sensitive '
            'because of your database. This means the search will <strong>not</strong> '
            'be accurate. By switching to a different database system you will gain '
            'better searching! For more information, read the '
            '<a href="http://docs.djangoproject.com/en/dev/ref/databases/#sqlite-string-matching">'
            'Django Documentation on string matching in SQLite</a>.')

    import json
    from helpdesk.lib import b64encode
    urlsafe_query = b64encode(json.dumps(query_params).encode('UTF-8'))

    user_saved_queries = SavedSearch.objects.filter(Q(user=request.user) | Q(shared__exact=True))

    querydict = request.GET.copy()
    querydict.pop('page', 1)

    return render(request, 'helpdesk/ticket_list.html', dict(
        context,
        query_string=querydict.urlencode(),
        tickets=tickets,
        user_choices=User.objects.filter(is_active=True, is_staff=True),
        queue_choices=user_queues,
        status_choices=Ticket.STATUS_CHOICES,
        urlsafe_query=urlsafe_query,
        user_saved_queries=user_saved_queries,
        query_params=query_params,
        from_saved_query=from_saved_query,
        saved_query=saved_query,
        search_message=search_message,
    ))
ticket_list = staff_member_required(ticket_list)


def edit_ticket(request, ticket_id):
    """
    Provide a form to edit details of an existing ticket and process updates.

    Validates that the user has access to the ticket’s queue before allowing edits.
    Handles form display on GET and form submission on POST, saving changes if valid.

    Parameters:
    - request: The HTTP request (GET or POST).
    - ticket_id: The ID of the ticket to be edited.

    Returns:
    - Rendered form page on GET or invalid POST.
    - Redirect to ticket detail page upon successful update.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    if request.method == 'POST':
        form = EditTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        form = EditTicketForm(instance=ticket)

    return render(request, 'helpdesk/edit_ticket.html', {'form': form})
edit_ticket = staff_member_required(edit_ticket)


def create_ticket(request):
    """
    Display a form to create a new ticket and process its submission.

    The list of assignable users depends on configuration settings.
    Supports pre-filling fields from user settings and GET parameters.
    Optionally hides the assigned user field based on configuration.

    Parameters:
    - request: The HTTP request (GET or POST).

    Returns:
    - Rendered form page on GET or invalid POST.
    - Redirect to ticket detail page or dashboard upon successful creation.
    """
    if helpdesk_settings.HELPDESK_STAFF_ONLY_TICKET_OWNERS:
        assignable_users = User.objects.filter(is_active=True, is_staff=True).order_by(User.USERNAME_FIELD)
    else:
        assignable_users = User.objects.filter(is_active=True).order_by(User.USERNAME_FIELD)

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        form.fields['queue'].choices = [('', '--------')] + [
            (q.id, q.title) for q in Queue.objects.all()]
        form.fields['assigned_to'].choices = [('', '--------')] + [
            (u.id, u.get_username()) for u in assignable_users]
        if form.is_valid():
            ticket = form.save(user=request.user)
            if _has_access_to_queue(request.user, ticket.queue):
                return HttpResponseRedirect(ticket.get_absolute_url())
            else:
                return HttpResponseRedirect(reverse('helpdesk_dashboard'))
    else:
        initial_data = {}
        if request.user.usersettings.settings.get('use_email_as_submitter', False) and request.user.email:
            initial_data['submitter_email'] = request.user.email
        if 'queue' in request.GET:
            initial_data['queue'] = request.GET['queue']

        form = TicketForm(initial=initial_data)
        form.fields['queue'].choices = [('', '--------')] + [
            (q.id, q.title) for q in Queue.objects.all()]
        form.fields['assigned_to'].choices = [('', '--------')] + [
            (u.id, u.get_username()) for u in assignable_users]
        if helpdesk_settings.HELPDESK_CREATE_TICKET_HIDE_ASSIGNED_TO:
            form.fields['assigned_to'].widget = forms.HiddenInput()

    return render(request, 'helpdesk/create_ticket.html', {'form': form})
create_ticket = staff_member_required(create_ticket)


def raw_details(request, type):
    """
    Return a plain-text representation of a specific object type.

    Currently supports only the 'preset' type, returning the body text of a PreSetReply identified by ID.

    Parameters:
    - request: The HTTP GET request containing the 'id' of the object.
    - type: The type of object requested (only 'preset' supported).

    Returns:
    - HttpResponse with plain text content of the requested object.
    - Raises Http404 if the object or type is invalid.
    """
    # TODO: This currently only supports spewing out 'PreSetReply' objects,
    # in the future it needs to be expanded to include other items. All it
    # does is return a plain-text representation of an object.

    if type not in ('preset',):
        raise Http404

    if type == 'preset' and request.GET.get('id', False):
        try:
            preset = PreSetReply.objects.get(id=request.GET.get('id'))
            return HttpResponse(preset.body)
        except PreSetReply.DoesNotExist:
            raise Http404

    raise Http404
raw_details = staff_member_required(raw_details)


def hold_ticket(request, ticket_id, unhold=False):
    """
    Place a ticket on hold or remove it from hold status, logging the action.

    Checks user permission on the ticket’s queue.
    Creates a public FollowUp note recording the hold/unhold action with timestamp.

    Parameters:
    - request: The HTTP request.
    - ticket_id: The ID of the ticket to modify.
    - unhold: Boolean flag to indicate whether to remove the hold.

    Returns:
    - Redirect to the ticket’s detail page.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    if unhold:
        ticket.on_hold = False
        title = _('Ticket taken off hold')
    else:
        ticket.on_hold = True
        title = _('Ticket placed on hold')

    f = FollowUp(
        ticket=ticket,
        user=request.user,
        title=title,
        date=timezone.now(),
        public=True,
    )
    f.save()

    ticket.save()

    return HttpResponseRedirect(ticket.get_absolute_url())
hold_ticket = staff_member_required(hold_ticket)


def unhold_ticket(request, ticket_id):
    """
    Remove the hold status from a ticket.

    This is a wrapper around hold_ticket with unhold=True.

    Parameters:
    - request: The HTTP request.
    - ticket_id: The ID of the ticket to unhold.

    Returns:
    - Redirect to the ticket’s detail page.
    """
    return hold_ticket(request, ticket_id, unhold=True)
unhold_ticket = staff_member_required(unhold_ticket)


def rss_list(request):
    """
    Render an RSS feed list page showing all queues.

    Provides a simple listing of all queues for RSS subscription purposes.

    Parameters:
    - request: The HTTP request.

    Returns:
    - Rendered HTML page displaying all queues.
    """

    return render(request, 'helpdesk/rss_list.html', {'queues': Queue.objects.all()})
rss_list = staff_member_required(rss_list)


def report_index(request):
    """
    Display the report index page with the total number of tickets and optionally a saved query.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'report_index.html' template with context:
            - number_tickets: Total count of Ticket objects.
            - saved_query: ID of saved query if provided via GET parameters.

    Decorators:
        staff_member_required: Restricts access to staff users.
    """
    number_tickets = Ticket.objects.all().count()
    saved_query = request.GET.get('saved_query', None)
    return render(request, 'helpdesk/report_index.html', {
        'number_tickets': number_tickets,
        'saved_query': saved_query,
    })
report_index = staff_member_required(report_index)


def run_report(request, report):
    """
    Run a specified report on tickets, optionally filtered by a saved query.

    Args:
        request (HttpRequest): The HTTP request object.
        report (str): Identifier string for the report to generate.

    Returns:
        HttpResponse: Renders 'report_output.html' with report data or redirects
                      to report index if no tickets or invalid report specified.

    Raises:
        PermissionDenied: If user lacks access to queues.

    Notes:
        - Uses Django ORM to query Ticket objects.
        - Applies saved query filtering if provided.
        - Generates summary tables for display in chart/table formats.
    """
    if Ticket.objects.all().count() == 0 or report not in (
            'queuemonth', 'usermonth', 'queuestatus', 'queuepriority', 'userstatus',
            'userpriority', 'userqueue', 'daysuntilticketclosedbymonth'):
        return HttpResponseRedirect(reverse("helpdesk_report_index"))

    report_queryset = Ticket.objects.all().select_related().filter(
        queue__in=_get_user_queues(request.user)
    )

    from_saved_query = False
    saved_query = None

    if request.GET.get('saved_query', None):
        from_saved_query = True
        try:
            saved_query = SavedSearch.objects.get(pk=request.GET.get('saved_query'))
        except SavedSearch.DoesNotExist:
            return HttpResponseRedirect(reverse('helpdesk_report_index'))
        if not (saved_query.shared or saved_query.user == request.user):
            return HttpResponseRedirect(reverse('helpdesk_report_index'))

        import json
        from helpdesk.lib import b64decode
        try:
            query_params = json.loads(b64decode(str(saved_query.query)))
        except:
            return HttpResponseRedirect(reverse('helpdesk_report_index'))

        report_queryset = apply_query(report_queryset, query_params)

    from collections import defaultdict
    summarytable = defaultdict(int)
    # a second table for more complex queries
    summarytable2 = defaultdict(int)

    month_name = lambda m: MONTHS_3[m].title()

    first_ticket = Ticket.objects.all().order_by('created')[0]
    first_month = first_ticket.created.month
    first_year = first_ticket.created.year

    last_ticket = Ticket.objects.all().order_by('-created')[0]
    last_month = last_ticket.created.month
    last_year = last_ticket.created.year

    periods = []
    year, month = first_year, first_month
    working = True
    periods.append("%s %s" % (month_name(month), year))

    while working:
        month += 1
        if month > 12:
            year += 1
            month = 1
        if (year > last_year) or (month > last_month and year >= last_year):
            working = False
        periods.append("%s %s" % (month_name(month), year))

    if report == 'userpriority':
        title = _('User by Priority')
        col1heading = _('User')
        possible_options = [t[1].title() for t in Ticket.PRIORITY_CHOICES]
        charttype = 'bar'

    elif report == 'userqueue':
        title = _('User by Category')
        col1heading = _('User')
        queue_options = _get_user_queues(request.user)
        possible_options = [q.title for q in queue_options]
        charttype = 'bar'

    elif report == 'userstatus':
        title = _('User by Status')
        col1heading = _('User')
        possible_options = [s[1].title() for s in Ticket.STATUS_CHOICES]
        charttype = 'bar'

    elif report == 'usermonth':
        title = _('User by Month')
        col1heading = _('User')
        possible_options = periods
        charttype = 'date'

    elif report == 'queuepriority':
        title = _('Category by Priority')
        col1heading = _('Category')
        possible_options = [t[1].title() for t in Ticket.PRIORITY_CHOICES]
        charttype = 'bar'

    elif report == 'queuestatus':
        title = _('Category by Status')
        col1heading = _('Category')
        possible_options = [s[1].title() for s in Ticket.STATUS_CHOICES]
        charttype = 'bar'

    elif report == 'queuemonth':
        title = _('Category by Month')
        col1heading = _('Category')
        possible_options = periods
        charttype = 'date'

    elif report == 'daysuntilticketclosedbymonth':
        title = _('Days until ticket closed by Month')
        col1heading = _('Category')
        possible_options = periods
        charttype = 'date'

    metric3 = False
    for ticket in report_queryset:
        if report == 'userpriority':
            metric1 = '%s' % ticket.get_assigned_to
            metric2 = '%s' % ticket.get_priority_display()

        elif report == 'userqueue':
            metric1 = '%s' % ticket.get_assigned_to
            metric2 = '%s' % ticket.queue.title

        elif report == 'userstatus':
            metric1 = '%s' % ticket.get_assigned_to
            metric2 = '%s' % ticket.get_status_display()

        elif report == 'usermonth':
            metric1 = '%s' % ticket.get_assigned_to
            metric2 = '%s %s' % (month_name(ticket.created.month), ticket.created.year)

        elif report == 'queuepriority':
            metric1 = '%s' % ticket.queue.title
            metric2 = '%s' % ticket.get_priority_display()

        elif report == 'queuestatus':
            metric1 = '%s' % ticket.queue.title
            metric2 = '%s' % ticket.get_status_display()

        elif report == 'queuemonth':
            metric1 = '%s' % ticket.queue.title
            metric2 = '%s %s' % (month_name(ticket.created.month), ticket.created.year)

        elif report == 'daysuntilticketclosedbymonth':
            metric1 = '%s' % ticket.queue.title
            metric2 = '%s %s' % (month_name(ticket.created.month), ticket.created.year)
            metric3 = ticket.modified - ticket.created
            metric3 = metric3.days

        summarytable[metric1, metric2] += 1
        if metric3:
            if report == 'daysuntilticketclosedbymonth':
                summarytable2[metric1, metric2] += metric3

    table = []

    if report == 'daysuntilticketclosedbymonth':
        for key in list(summarytable2.keys()):
            summarytable[key] = summarytable2[key] / summarytable[key]

    header1 = sorted(set(list(i for i, _ in list(summarytable.keys()))))

    column_headings = [col1heading] + possible_options

    # Pivot the data so that 'header1' fields are always first column
    # in the row, and 'possible_options' are always the 2nd - nth columns.
    for item in header1:
        data = []
        for hdr in possible_options:
            data.append(summarytable[item, hdr])
        table.append([item] + data)

    return render(request, 'helpdesk/report_output.html', {
        'title': title,
        'charttype': charttype,
        'data': table,
        'headings': column_headings,
        'from_saved_query': from_saved_query,
        'saved_query': saved_query,
    })
run_report = staff_member_required(run_report)


def save_query(request):
    """
    Save a new saved search query for tickets.

    Args:
        request (HttpRequest): The HTTP POST request containing 'title', 'shared', and 'query_encoded'.

    Returns:
        HttpResponseRedirect: Redirect to the ticket list with the saved query ID as a GET parameter.

    Notes:
        - Only accessible by staff members.
        - 'shared' flag indicates if query is visible to others.
        - Redirects to ticket list if 'title' or 'query_encoded' missing.
    """
    title = request.POST.get('title', None)
    shared = request.POST.get('shared', False)
    if shared == 'on': # django only translates '1', 'true', 't' into True
        shared = True
    query_encoded = request.POST.get('query_encoded', None)

    if not title or not query_encoded:
        return HttpResponseRedirect(reverse('helpdesk_list'))

    query = SavedSearch(title=title, shared=shared, query=query_encoded, user=request.user)
    query.save()

    return HttpResponseRedirect('%s?saved_query=%s' % (reverse('helpdesk_list'), query.id))
save_query = staff_member_required(save_query)


def delete_saved_query(request, id):
    """
    Delete a saved search query belonging to the requesting user.

    Args:
        request (HttpRequest): The HTTP request.
        id (int): The primary key of the SavedSearch to delete.

    Returns:
        HttpResponseRedirect: Redirects to ticket list after deletion.
        HttpResponse: Renders a confirmation page if request method is GET.

    Raises:
        Http404: If no SavedSearch exists with given id and user.

    Notes:
        - Only accessible by staff members.
    """
    query = get_object_or_404(SavedSearch, id=id, user=request.user)

    if request.method == 'POST':
        query.delete()
        return HttpResponseRedirect(reverse('helpdesk_list'))
    else:
        return render(request, 'helpdesk/confirm_delete_saved_query.html', {'query': query})
delete_saved_query = staff_member_required(delete_saved_query)


def user_settings(request):
    """
    View and update user-specific settings for the helpdesk.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'user_settings.html' with the form.

    Notes:
        - Loads UserSettingsForm with existing settings on GET.
        - Saves updated settings on valid POST.
        - Access restricted to staff members.
    """
    s = request.user.usersettings
    if request.POST:
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            s.settings = form.cleaned_data
            s.save()
    else:
        form = UserSettingsForm(s.settings)

    return render(request, 'helpdesk/user_settings.html', {'form': form})
user_settings = staff_member_required(user_settings)


def email_ignore(request):
    """
    Display the list of ignored email addresses.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'email_ignore_list.html' template with all IgnoreEmail objects.

    Notes:
        - Access restricted to superusers.
    """
    return render(request, 'helpdesk/email_ignore_list.html', {
        'ignore_list': IgnoreEmail.objects.all(),
    })
email_ignore = superuser_required(email_ignore)


def email_ignore_add(request):
    """
    Add a new email address to the ignore list.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered form template on GET or invalid POST.
                      Redirects to ignore list on successful POST.

    Notes:
        - Uses EmailIgnoreForm to validate input.
        - Access restricted to superusers.
    """
    if request.method == 'POST':
        form = EmailIgnoreForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        form = EmailIgnoreForm(request.GET)

    return render(request, 'helpdesk/email_ignore_add.html', {'form': form})
email_ignore_add = superuser_required(email_ignore_add)


def email_ignore_del(request, id):
    """
    Delete an email address from the ignore list.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The primary key of the IgnoreEmail to delete.

    Returns:
        HttpResponseRedirect: Redirects to ignore list after deletion.
        HttpResponse: Renders a confirmation page if request method is GET.

    Raises:
        Http404: If no IgnoreEmail exists with given id.

    Notes:
        - Access restricted to superusers.
    """
    ignore = get_object_or_404(IgnoreEmail, id=id)
    if request.method == 'POST':
        ignore.delete()
        return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        return render(request, 'helpdesk/email_ignore_del.html', {'ignore': ignore})
email_ignore_del = superuser_required(email_ignore_del)


def ticket_cc(request, ticket_id):
    """Display the list of CC'd users/emails for a specific ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    copies_to = ticket.ticketcc_set.all()
    return render(request, 'helpdesk/ticket_cc_list.html', {
        'copies_to': copies_to,
        'ticket': ticket,
    })
ticket_cc = staff_member_required(ticket_cc)


def ticket_cc_add(request, ticket_id):
    """Add a CC recipient to a specific ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()

    if request.method == 'POST':
        form = TicketCCForm(request.POST)
        if form.is_valid():
            ticketcc = form.save(commit=False)
            ticketcc.ticket = ticket
            ticketcc.save()
            return HttpResponseRedirect(reverse('helpdesk_ticket_cc',
                                                kwargs={'ticket_id': ticket.id}))
    else:
        form = TicketCCForm()
    return render(request, 'helpdesk/ticket_cc_add.html', {
        'ticket': ticket,
        'form': form,
    })
ticket_cc_add = staff_member_required(ticket_cc_add)


def ticket_cc_del(request, ticket_id, cc_id):
    """View to delete a TicketCC entry related to a ticket."""
    cc = get_object_or_404(TicketCC, ticket__id=ticket_id, id=cc_id)

    if request.method == 'POST':
        cc.delete()
        return HttpResponseRedirect(reverse('helpdesk_ticket_cc',
                                            kwargs={'ticket_id': cc.ticket.id}))
    return render(request, 'helpdesk/ticket_cc_del.html', {'cc': cc})
ticket_cc_del = staff_member_required(ticket_cc_del)


def ticket_dependency_add(request, ticket_id):
    """Add a dependency to a ticket.

    Args:
        request: HttpRequest object.
        ticket_id: ID of the ticket to add dependency to.

    Raises:
        PermissionDenied if user has no access to the ticket's queue.

    Returns:
        On GET, renders a form to add dependency.
        On valid POST, adds dependency and redirects to ticket view."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()
    if request.method == 'POST':
        form = TicketDependencyForm(request.POST)
        if form.is_valid():
            ticketdependency = form.save(commit=False)
            ticketdependency.ticket = ticket
            if ticketdependency.ticket != ticketdependency.depends_on:
                ticketdependency.save()
            return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket.id]))
    else:
        form = TicketDependencyForm()
    return render(request, 'helpdesk/ticket_dependency_add.html', {
        'ticket': ticket,
        'form': form,
    })
ticket_dependency_add = staff_member_required(ticket_dependency_add)


def ticket_dependency_del(request, ticket_id, dependency_id):
    """Delete a ticket dependency."""
    dependency = get_object_or_404(TicketDependency, ticket__id=ticket_id, id=dependency_id)
    if request.method == 'POST':
        dependency.delete()
        return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket_id]))
    return render(request, 'helpdesk/ticket_dependency_del.html', {'dependency': dependency})
ticket_dependency_del = staff_member_required(ticket_dependency_del)


def attachment_del(request, ticket_id, attachment_id):
    """Delete an attachment from a ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not _has_access_to_queue(request.user, ticket.queue):
        raise PermissionDenied()
    attachment = get_object_or_404(Attachment, id=attachment_id)
    attachment.delete()
    return HttpResponseRedirect(reverse('helpdesk_view', args=[ticket_id]))
attachment_del = staff_member_required(attachment_del)


def calc_average_nbr_days_until_ticket_resolved(Tickets):
    """Calculate the average number of days between ticket creation and last modification (resolved)."""
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
    """Compute basic statistics for tickets such as counts of open tickets by age,
    and average resolution times."""
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
    """Return a color string("green", "orange or "red") based on the number of days."""
    if nbr_days < 5:
        color_string = 'green'
    elif nbr_days < 10:
        color_string = 'orange'
    else:  # more than 10 days
        color_string = 'red'

    return color_string


def days_since_created(today, ticket):
    """Calculate the number of days since the ticket was created."""
    return (today - ticket.created).days


def date_rel_to_today(today, offset):
    """Calculate the date relative to today by subtracting an offset in days."""
    return today - timedelta(days = offset)


def sort_string(begin, end):
    """Construct a query string for sorting and filtering tickets by date and status."""
    return 'sort=created&date_from=%s&date_to=%s&status=%s&status=%s&status=%s' % (
        begin, end, Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS, Ticket.RESOLVED_STATUS)
