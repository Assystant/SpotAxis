"""                                     ..
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

api.py - Wrapper around API calls, and core functions to provide complete
         API to third party applications.

The API documentation can be accessed by visiting http://helpdesk/api/help/
(obviously, substitute helpdesk for your django-helpdesk URI), or by reading
through templates/helpdesk/help_api.html.
"""

from __future__ import absolute_import
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
import simplejson
from django.views.decorators.csrf import csrf_exempt

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from helpdesk.forms import TicketForm
from helpdesk.lib import send_templated_mail, safe_template_context
from helpdesk.models import Ticket, Queue, FollowUp

import warnings

User = get_user_model()

STATUS_OK = 200

STATUS_ERROR = 400
STATUS_ERROR_NOT_FOUND = 404
STATUS_ERROR_PERMISSIONS = 403
STATUS_ERROR_BADMETHOD = 405


@csrf_exempt
def api(request, method):
    """
    Regardless of any other paramaters, we provide a help screen
    to the user if they requested one.

    If the user isn't looking for help, then we enforce a few conditions:
        * The request must be sent via HTTP POST
        * The request must contain a 'user' and 'password' which
          must be valid users
        * The method must match one of the public methods of the API class.


    THIS IS DEPRECATED AS OF DECEMBER 2015 AND WILL BE REMOVED IN JANUARY 2016.
    SEE https://github.com/django-helpdesk/django-helpdesk/issues/198 FOR DETAILS

    """

    warnings.warn("django-helpdesk API will be removed in January 2016. "
                  "See https://github.com/django-helpdesk/django-helpdesk/issues/198 for details.",
                  category=DeprecationWarning)

    if method == 'help':
        return render(request, template_name='helpdesk/help_api.html')

    if request.method != 'POST':
        return api_return(STATUS_ERROR_BADMETHOD)

    # TODO: Move away from having the username & password in every request.
    request.user = authenticate(
        username=request.POST.get('user', False),
        password=request.POST.get('password'),
        )

    if request.user is None:
        return api_return(STATUS_ERROR_PERMISSIONS)

    api = API(request)
    if hasattr(api, 'api_public_%s' % method):
        return getattr(api, 'api_public_%s' % method)()

    return api_return(STATUS_ERROR)


def api_return(status, text='', json=False):
    """
    Returns a standardized HTTP response for API calls.

    Depending on the status, this can return either a plain text or JSON response.
    Also handles error messages like 'Resource Not Found' or 'Invalid method'.

    Parameters:
        status (int): HTTP status code like 200, 400, 403, etc.
        text (str): Response body (text or JSON string)
        json (bool): Whether to set the content type to application/json

    If `status` is 405 (bad method), sets the HTTP Allow header to POST.
    """
    content_type = 'text/plain'
    if status == STATUS_OK and json:
        content_type = 'text/json'

    if text is None:
        if status == STATUS_ERROR:
            text = 'Error'
        elif status == STATUS_ERROR_NOT_FOUND:
            text = 'Resource Not Found'
        elif status == STATUS_ERROR_PERMISSIONS:
            text = 'Invalid username or password'
        elif status == STATUS_ERROR_BADMETHOD:
            text = 'Invalid request method'
        elif status == STATUS_OK:
            text = 'OK'

    r = HttpResponse(status=status, content=text, content_type=content_type)

    if status == STATUS_ERROR_BADMETHOD:
        r.Allow = 'POST'

    return r


class API:
    """
    The API class provides the actual business logic for the supported API methods.

    Each API method is exposed as a method prefixed with `api_public_` and is invoked
    based on the `method` string passed to the `api()` dispatcher.

    All methods require POST data and a valid authenticated user.
    """
    def __init__(self, request):
        self.request = request

    def api_public_create_ticket(self):
        """
        Creates a new ticket from POSTed data using the `TicketForm`.

        The queue and assigned_to fields are dynamically populated from the DB.
        If the form is valid, a ticket is saved and the ID is returned.

        Returns:
            200 OK with ticket ID, or
            400 Error with form validation messages
        """
        form = TicketForm(self.request.POST)
        form.fields['queue'].choices = [[q.id, q.title] for q in Queue.objects.all()]
        form.fields['assigned_to'].choices = [[u.id, u.get_username()] for u in User.objects.filter(is_active=True)]

        if form.is_valid():
            ticket = form.save(user=self.request.user)
            return api_return(STATUS_OK, "%s" % ticket.id)
        else:
            return api_return(STATUS_ERROR, text=form.errors.as_text())

    def api_public_list_queues(self):
        """
        Returns a list of all queues in the system.

        Used to populate selection options when creating a ticket via the API.

        Returns:
            200 OK with a JSON list of queues, each with 'id' and 'title'
        """

        return api_return(STATUS_OK, simplejson.dumps([
            {"id": "%s" % q.id, "title": "%s" % q.title}
            for q in Queue.objects.all()
        ]), json=True)

    def api_public_find_user(self):
        """
        Finds and returns the ID of a user given a username.

        Used to assign ownership of a ticket programmatically.

        Returns:
            200 OK with user ID, or
            400 Error if username is invalid or not found
        """

        username = self.request.POST.get('username', False)

        try:
            u = User.objects.get(username=username)
            return api_return(STATUS_OK, "%s" % u.id)

        except User.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid username provided")

    def api_public_delete_ticket(self):
        """
        Deletes a ticket given its ID, only if 'confirm' is provided in the POST.

        This acts as a safeguard to prevent accidental deletions.

        Returns:
            200 OK on successful deletion, or
            400 Error if ticket ID is invalid or confirmation is missing
        """

        if not self.request.POST.get('confirm', False):
            return api_return(STATUS_ERROR, "No confirmation provided")

        try:
            ticket = Ticket.objects.get(id=self.request.POST.get('ticket', False))
        except Ticket.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid ticket ID")

        ticket.delete()

        return api_return(STATUS_OK)

    def api_public_hold_ticket(self):
        """
        Marks the ticket as on hold, which prevents automatic escalation.

        Returns:
            200 OK if the ticket is updated, or
            400 Error if the ticket ID is invalid
        """

        try:
            ticket = Ticket.objects.get(id=self.request.POST.get('ticket', False))
        except Ticket.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid ticket ID")

        ticket.on_hold = True
        ticket.save()

        return api_return(STATUS_OK)

    def api_public_unhold_ticket(self):
        """
        Removes the 'on hold' status from a ticket.

        Returns:
            200 OK if the ticket is updated, or
            400 Error if the ticket ID is invalid
        """

        try:
            ticket = Ticket.objects.get(id=self.request.POST.get('ticket', False))
        except Ticket.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid ticket ID")

        ticket.on_hold = False
        ticket.save()

        return api_return(STATUS_OK)

    def api_public_add_followup(self):
        """
        Adds a follow-up message to a ticket, either public or private.

        If public, it sends email notifications to the submitter, CC list, and assignee.
        Only accepts 'y' or 'n' for the public field.

        Returns:
            200 OK if the follow-up is added, or
            400 Error for invalid ticket ID, blank message, or invalid public flag
        """

        try:
            ticket = Ticket.objects.get(id=self.request.POST.get('ticket', False))
        except Ticket.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid ticket ID")

        message = self.request.POST.get('message', None)
        public = self.request.POST.get('public', 'n')

        if public not in ['y', 'n']:
            return api_return(STATUS_ERROR, "Invalid 'public' flag")

        if not message:
            return api_return(STATUS_ERROR, "Blank message")

        f = FollowUp(
            ticket=ticket,
            date=timezone.now(),
            comment=message,
            user=self.request.user,
            title='Comment Added',
            )

        if public:
            f.public = True

        f.save()

        context = safe_template_context(ticket)
        context['comment'] = f.comment

        messages_sent_to = []

        if public and ticket.submitter_email:
            send_templated_mail(
                'updated_submitter',
                context,
                recipients=ticket.submitter_email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                )
            messages_sent_to.append(ticket.submitter_email)

        if public:
            for cc in ticket.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        'updated_submitter',
                        context,
                        recipients=cc.email_address,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                        )
                    messages_sent_to.append(cc.email_address)

        if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'updated_cc',
                context,
                recipients=ticket.queue.updated_ticket_cc,
                sender=ticket.queue.from_address,
                fail_silently=True,
                )
            messages_sent_to.append(ticket.queue.updated_ticket_cc)

        if (
            ticket.assigned_to and
            self.request.user != ticket.assigned_to and
            ticket.assigned_to.usersettings.settings.get('email_on_ticket_apichange', False) and
            ticket.assigned_to.email and
            ticket.assigned_to.email not in messages_sent_to
        ):
            send_templated_mail(
                'updated_owner',
                context,
                recipients=ticket.assigned_to.email,
                sender=ticket.queue.from_address,
                fail_silently=True,
            )

        ticket.save()

        return api_return(STATUS_OK)

    def api_public_resolve(self):
        """
        Resolves a ticket by setting its status to RESOLVED and saving a resolution comment.

        Sends notifications to all relevant parties (submitter, CC, assignee, etc.)
        based on their preferences and system settings.

        Returns:
            200 OK if the ticket is resolved, or
            400 Error if the ticket ID or resolution is missing
        """

        try:
            ticket = Ticket.objects.get(id=self.request.POST.get('ticket', False))
        except Ticket.DoesNotExist:
            return api_return(STATUS_ERROR, "Invalid ticket ID")

        resolution = self.request.POST.get('resolution', None)

        if not resolution:
            return api_return(STATUS_ERROR, "Blank resolution")

        f = FollowUp(
            ticket=ticket,
            date=timezone.now(),
            comment=resolution,
            user=self.request.user,
            title='Resolved',
            public=True,
            )
        f.save()

        context = safe_template_context(ticket)
        context['resolution'] = f.comment

        # subject = '%s %s (Resolved)' % (ticket.ticket, ticket.title)

        messages_sent_to = []

        if ticket.submitter_email:
            send_templated_mail(
                'resolved_submitter',
                context,
                recipients=ticket.submitter_email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                )
            messages_sent_to.append(ticket.submitter_email)

            for cc in ticket.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        'resolved_submitter',
                        context,
                        recipients=cc.email_address,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                        )
                    messages_sent_to.append(cc.email_address)

        if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'resolved_cc',
                context,
                recipients=ticket.queue.updated_ticket_cc,
                sender=ticket.queue.from_address,
                fail_silently=True,
                )
            messages_sent_to.append(ticket.queue.updated_ticket_cc)

        if ticket.assigned_to and \
                self.request.user != ticket.assigned_to and \
                getattr(ticket.assigned_to.usersettings.settings,
                        'email_on_ticket_apichange', False) and \
                ticket.assigned_to.email and \
                ticket.assigned_to.email not in messages_sent_to:
            send_templated_mail(
                'resolved_resolved',
                context,
                recipients=ticket.assigned_to.email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                )

        ticket.resoltuion = f.comment
        ticket.status = Ticket.RESOLVED_STATUS

        ticket.save()

        return api_return(STATUS_OK)
