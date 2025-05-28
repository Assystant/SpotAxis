"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

forms.py - Definitions of newforms-based forms for creating and maintaining
           tickets.
"""
from __future__ import absolute_import
from django.core.exceptions import ObjectDoesNotExist

try:
    from io import StringIO
except ImportError:
    from io import StringIO

from django import forms
from django.forms import extras
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from helpdesk.lib import send_templated_mail, safe_template_context
from helpdesk.models import (Ticket, Queue, FollowUp, Attachment, IgnoreEmail, TicketCC,
                             CustomField, TicketCustomFieldValue, TicketDependency)
from helpdesk import settings as helpdesk_settings

User = get_user_model()


class CustomFieldMixin(object):
    """
    Mixin to dynamically add custom ticket fields to a form instance.

    This mixin maps each `CustomField` from the database to the appropriate
    Django form field type. The generated field is added to `self.fields`.

    Supports types like:
    - varchar -> CharField
    - text -> CharField with Textarea
    - integer -> IntegerField
    - list -> ChoiceField with optional empty selection
    - boolean, date, datetime, time, decimal, email, url, IP address, slug, etc.

    Used in:
        - TicketForm
        - PublicTicketForm
        - EditTicketForm
    """
    def customfield_to_field(self, field, instanceargs):
        if field.data_type == 'varchar':
            fieldclass = forms.CharField
            instanceargs['max_length'] = field.max_length
        elif field.data_type == 'text':
            fieldclass = forms.CharField
            instanceargs['widget'] = forms.Textarea
            instanceargs['max_length'] = field.max_length
        elif field.data_type == 'integer':
            fieldclass = forms.IntegerField
        elif field.data_type == 'decimal':
            fieldclass = forms.DecimalField
            instanceargs['decimal_places'] = field.decimal_places
            instanceargs['max_digits'] = field.max_length
        elif field.data_type == 'list':
            fieldclass = forms.ChoiceField
            choices = field.choices_as_array
            if field.empty_selection_list:
                choices.insert(0, ('', '---------'))
            instanceargs['choices'] = choices
        elif field.data_type == 'boolean':
            fieldclass = forms.BooleanField
        elif field.data_type == 'date':
            fieldclass = forms.DateField
        elif field.data_type == 'time':
            fieldclass = forms.TimeField
        elif field.data_type == 'datetime':
            fieldclass = forms.DateTimeField
        elif field.data_type == 'email':
            fieldclass = forms.EmailField
        elif field.data_type == 'url':
            fieldclass = forms.URLField
        elif field.data_type == 'ipaddress':
            fieldclass = forms.IPAddressField
        elif field.data_type == 'slug':
            fieldclass = forms.SlugField

        self.fields['custom_%s' % field.name] = fieldclass(**instanceargs)


class EditTicketForm(CustomFieldMixin, forms.ModelForm):
    """
    A form for editing an existing ticket, excluding fields that are managed
    automatically (e.g. creation/modification dates, status, resolution, etc.).

    This form also dynamically includes any `CustomField` entries using the
    `CustomFieldMixin`.

    Inherits from:
        - CustomFieldMixin: Adds custom ticket fields
        - forms.ModelForm: Standard Django model form

    Uses:
        - CustomField: to fetch user-defined fields
        - TicketCustomFieldValue: to populate custom field values per ticket
    """
    class Meta:
        model = Ticket
        exclude = ('created', 'modified', 'status', 'on_hold', 'resolution', 'last_escalation', 'assigned_to')

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with custom fields based on `CustomField` records.

        For each custom field, the current value (if set) is fetched from
        `TicketCustomFieldValue` and used as the initial value.

        Modules Used:
            - CustomField: to fetch all custom field definitions
            - TicketCustomFieldValue: to fetch existing values for the current ticket
        """
        super(EditTicketForm, self).__init__(*args, **kwargs)

        for field in CustomField.objects.all():
            try:
                current_value = TicketCustomFieldValue.objects.get(ticket=self.instance, field=field)
                initial_value = current_value.value
            except TicketCustomFieldValue.DoesNotExist:
                initial_value = None
            instanceargs = {
                    'label': field.label,
                    'help_text': field.help_text,
                    'required': field.required,
                    'initial': initial_value,
                    }

            self.customfield_to_field(field, instanceargs)

    def save(self, *args, **kwargs):
        """
        Saves the form and updates any `TicketCustomFieldValue` entries
        for the custom fields.

        First processes all cleaned data that starts with 'custom_' prefix,
        retrieves or creates the appropriate `TicketCustomFieldValue`, and
        updates its value before saving the base ticket.

        Modules Used:
            - CustomField: to resolve custom field by name
            - TicketCustomFieldValue: to update per-ticket field values
            - ObjectDoesNotExist: to catch missing value cases
        """
        for field, value in list(self.cleaned_data.items()):
            if field.startswith('custom_'):
                field_name = field.replace('custom_', '', 1)
                customfield = CustomField.objects.get(name=field_name)
                try:
                    cfv = TicketCustomFieldValue.objects.get(ticket=self.instance, field=customfield)
                except ObjectDoesNotExist:
                    cfv = TicketCustomFieldValue(ticket=self.instance, field=customfield)
                cfv.value = value
                cfv.save()

        return super(EditTicketForm, self).save(*args, **kwargs)


class EditFollowUpForm(forms.ModelForm):
    """
    A form for editing or creating a follow-up on an existing ticket.

    This form excludes automatic fields such as the creation date and user,
    and filters the ticket selection to only tickets that are still open
    or reopened.

    Inherits from:
        - forms.ModelForm: Standard Django model form

    Uses:
        - FollowUp: the model being edited
        - Ticket: used to filter open/reopened tickets in the queryset
    """
    class Meta:
        model = FollowUp
        exclude = ('date', 'user',)

    def __init__(self, *args, **kwargs):
        """
        Filters the 'ticket' field queryset to include only tickets that
        are currently in an open or reopened state.

        This ensures that follow-ups are only added to active tickets.

        Modules Used:
            - Ticket: to filter by status using constants OPEN_STATUS and REOPENED_STATUS
        """
        super(EditFollowUpForm, self).__init__(*args, **kwargs)
        self.fields["ticket"].queryset = Ticket.objects.filter(status__in=(Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS))


class TicketForm(CustomFieldMixin, forms.Form):
    """
    A form used for creating a new ticket via the staff interface.

    Allows selection of queue, owner, priority, and due date, and supports
    file attachments and custom fields.

    Includes:
    - Dynamically generated fields from `CustomFieldMixin`
    - Optional file attachment
    - Automatic email notifications to submitter, assignee, and CC addresses

    Inherits from:
        - CustomFieldMixin: For custom ticket fields
        - forms.Form: Base Django form
    """
    queue = forms.ChoiceField(
        label=_('Category'),
        required=True,
        choices=()
        )

    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'size':'60'}),
        label=_('Summary of the problem'),
        )

    submitter_email = forms.EmailField(
        required=False,
        label=_('Submitter E-Mail Address'),
        widget=forms.TextInput(attrs={'size':'60'}),
        help_text=_('This e-mail address will receive copies of all public '
            'updates to this ticket.'),
        )

    body = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 47, 'rows': 15}),
        label=_('Description of Issue'),
        required=True,
        )

    assigned_to = forms.ChoiceField(
        choices=(),
        required=False,
        label=_('Case owner'),
        help_text=_('If you select an owner other than yourself, they\'ll be '
                    'e-mailed details of this ticket immediately.'),
        )

    priority = forms.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES,
        required=False,
        initial='3',
        label=_('Priority'),
        help_text=_('Please select a priority carefully. If unsure, leave it as \'3\'.'),
        )

    due_date = forms.DateTimeField(
        widget=extras.SelectDateWidget,
        required=False,
        label=_('Due on'),
        )

    def clean_due_date(self):
        """
        Clean method for due_date field. Placeholder for future extensions,
        such as Google Calendar sync.

        Currently returns the value unchanged."""
        data = self.cleaned_data['due_date']
        # TODO: add Google calendar update hook
        # if not hasattr(self, 'instance') or self.instance.due_date != new_data:
        #     print "you changed!"
        return data

    attachment = forms.FileField(
        required=False,
        label=_('Attach File'),
        help_text=_('You can attach a file such as a document or screenshot to this ticket.'),
        )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and dynamically add any custom fields.

        Custom fields are fetched from the database and converted to actual form
        fields using `customfield_to_field`.

        Modules Used:
            - CustomField: defines the custom fields to include
        """
        super(TicketForm, self).__init__(*args, **kwargs)
        for field in CustomField.objects.all():
            instanceargs = {
                    'label': field.label,
                    'help_text': field.help_text,
                    'required': field.required,
                    }

            self.customfield_to_field(field, instanceargs)

    def save(self, user):
        """
        Writes and returns a Ticket() object
        """

        q = Queue.objects.get(id=int(self.cleaned_data['queue']))

        t = Ticket(title=self.cleaned_data['title'],
                   submitter_email=self.cleaned_data['submitter_email'],
                   created=timezone.now(),
                   status=Ticket.OPEN_STATUS,
                   queue=q,
                   description=self.cleaned_data['body'],
                   priority=self.cleaned_data['priority'],
                   due_date=self.cleaned_data['due_date'],
                   )

        if self.cleaned_data['assigned_to']:
            try:
                u = User.objects.get(id=self.cleaned_data['assigned_to'])
                t.assigned_to = u
            except User.DoesNotExist:
                t.assigned_to = None
        t.save()

        for field, value in list(self.cleaned_data.items()):
            if field.startswith('custom_'):
                field_name = field.replace('custom_', '', 1)
                customfield = CustomField.objects.get(name=field_name)
                cfv = TicketCustomFieldValue(ticket=t,
                                             field=customfield,
                                             value=value)
                cfv.save()

        f = FollowUp(ticket=t,
                     title=_('Ticket Opened'),
                     date=timezone.now(),
                     public=True,
                     comment=self.cleaned_data['body'],
                     user=user,
                     )
        if self.cleaned_data['assigned_to']:
            f.title = _('Ticket Opened & Assigned to %(name)s') % {
                'name': t.get_assigned_to
            }

        f.save()

        files = []
        if self.cleaned_data['attachment']:
            import mimetypes
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                size=file.size,
                )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                try:
                    files.append([a.filename, a.file])
                except NotImplementedError:
                    pass

        context = safe_template_context(t)
        context['comment'] = f.comment

        messages_sent_to = []

        if t.submitter_email:
            send_templated_mail(
                'newticket_submitter',
                context,
                recipients=t.submitter_email,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(t.submitter_email)

        if t.assigned_to and \
                t.assigned_to != user and \
                t.assigned_to.usersettings.settings.get('email_on_ticket_assign', False) and \
                t.assigned_to.email and \
                t.assigned_to.email not in messages_sent_to:
            send_templated_mail(
                'assigned_owner',
                context,
                recipients=t.assigned_to.email,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(t.assigned_to.email)

        if q.new_ticket_cc and q.new_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.new_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(q.new_ticket_cc)

        if q.updated_ticket_cc and \
                q.updated_ticket_cc != q.new_ticket_cc and \
                q.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.updated_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )

        return t


class PublicTicketForm(CustomFieldMixin, forms.Form):
    """
    Form for public users to submit new tickets via the web interface.

    Captures basic info like category, email, issue description, priority,
    and optional attachment.

    Dynamically includes non-staff-only custom fields.

    Inherits:
        - CustomFieldMixin
        - forms.Form
    """
    queue = forms.ChoiceField(
        label=_('Category'),
        required=True,
        choices=()
        )

    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_('Summary of your query'),
        )

    submitter_email = forms.EmailField(
        required=True,
        label=_('Your E-Mail Address'),
        help_text=_('We will e-mail you when your ticket is updated.'),
        )

    body = forms.CharField(
        widget=forms.Textarea(),
        label=_('Description of your issue'),
        required=True,
        help_text=_('Please be as descriptive as possible, including any '
                    'details we may need to address your query.'),
        )

    priority = forms.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES,
        required=True,
        initial='3',
        label=_('Urgency'),
        help_text=_('Please select a priority carefully.'),
        )

    # due_date = forms.DateTimeField(
    #     widget=extras.SelectDateWidget,
    #     required=False,
    #     label=_('Due on'),
    #     )

    attachment = forms.FileField(
        required=False,
        label=_('Attach File'),
        help_text=_('You can attach a file such as a document or screenshot to this ticket.'),
        max_length=1000,
        )

    def __init__(self, *args, **kwargs):
        """
        Add any custom fields that are defined to the form
        """
        super(PublicTicketForm, self).__init__(*args, **kwargs)
        for field in CustomField.objects.filter(staff_only=False):
            instanceargs = {
                    'label': field.label,
                    'help_text': field.help_text,
                    'required': field.required,
                    }

            self.customfield_to_field(field, instanceargs)

    def save(self):
        """
        Creates and saves a new Ticket submitted by a public user.

        - Creates a FollowUp
        - Saves custom field values and attachments
        - Sends notification emails

        Returns:
            Ticket: The created ticket object
        """

        q = Queue.objects.get(id=int(self.cleaned_data['queue']))

        t = Ticket(
            title=self.cleaned_data['title'],
            submitter_email=self.cleaned_data['submitter_email'],
            created=timezone.now(),
            status=Ticket.OPEN_STATUS,
            queue=q,
            description=self.cleaned_data['body'],
            priority=self.cleaned_data['priority'],
            due_date=None,
            )

        if q.default_owner and not t.assigned_to:
            t.assigned_to = q.default_owner

        t.save()

        for field, value in list(self.cleaned_data.items()):
            if field.startswith('custom_'):
                field_name = field.replace('custom_', '', 1)
                customfield = CustomField.objects.get(name=field_name)
                cfv = TicketCustomFieldValue(ticket=t,
                                             field=customfield,
                                             value=value)
                cfv.save()

        f = FollowUp(
            ticket=t,
            title=_('Ticket Opened Via Web'),
            date=timezone.now(),
            public=True,
            comment=self.cleaned_data['body'],
            )

        f.save()

        files = []
        if self.cleaned_data['attachment']:
            import mimetypes
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                size=file.size,
                )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append([a.filename, a.file])

        context = safe_template_context(t)

        messages_sent_to = []

        send_templated_mail(
            'newticket_submitter',
            context,
            recipients=t.submitter_email,
            sender=q.from_address,
            fail_silently=True,
            files=files,
            )
        messages_sent_to.append(t.submitter_email)

        if t.assigned_to and \
                t.assigned_to.usersettings.settings.get('email_on_ticket_assign', False) and \
                t.assigned_to.email and \
                t.assigned_to.email not in messages_sent_to:
            send_templated_mail(
                'assigned_owner',
                context,
                recipients=t.assigned_to.email,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(t.assigned_to.email)

        if q.new_ticket_cc and q.new_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.new_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(q.new_ticket_cc)

        if q.updated_ticket_cc and \
                q.updated_ticket_cc != q.new_ticket_cc and \
                q.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.updated_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
                )

        return t


class UserSettingsForm(forms.Form):
    """
    Form for managing user-specific preferences in the helpdesk system.

    Allows configuration of:
    - Dashboard view on login
    - Email notifications for ticket changes, assignments, and API updates
    - Ticket pagination preferences
    - Whether to auto-fill the submitter email field
    """
    login_view_ticketlist = forms.BooleanField(
        label=_('Show Ticket List on Login?'),
        help_text=_('Display the ticket list upon login? Otherwise, the dashboard is shown.'),
        required=False,
        )

    email_on_ticket_change = forms.BooleanField(
        label=_('E-mail me on ticket change?'),
        help_text=_('If you\'re the ticket owner and the ticket is changed via the web by somebody else, do you want to receive an e-mail?'),
        required=False,
        )

    email_on_ticket_assign = forms.BooleanField(
        label=_('E-mail me when assigned a ticket?'),
        help_text=_('If you are assigned a ticket via the web, do you want to receive an e-mail?'),
        required=False,
        )

    email_on_ticket_apichange = forms.BooleanField(
        label=_('E-mail me when a ticket is changed via the API?'),
        help_text=_('If a ticket is altered by the API, do you want to receive an e-mail?'),
        required=False,
        )

    tickets_per_page = forms.IntegerField(
        label=_('Number of tickets to show per page'),
        help_text=_('How many tickets do you want to see on the Ticket List page?'),
        required=False,
        min_value=1,
        max_value=1000,
        )

    use_email_as_submitter = forms.BooleanField(
        label=_('Use my e-mail address when submitting tickets?'),
        help_text=_('When you submit a ticket, do you want to automatically use your e-mail address as the submitter address? You can type a different e-mail address when entering the ticket if needed, this option only changes the default.'),
        required=False,
        )


class EmailIgnoreForm(forms.ModelForm):
    """
    Model form for managing ignored email addresses.

    Used to create or update `IgnoreEmail` entries that filter out unwanted
    email senders during ticket creation.
    """
    class Meta:
        model = IgnoreEmail
        exclude = []


class TicketCCForm(forms.ModelForm):
    """
    Model form to add or edit a CC (carbon copy) follower for a ticket.

    Filters the user queryset to staff-only or all active users based on
    `HELPDESK_STAFF_ONLY_TICKET_CC` setting.
    """
    class Meta:
        model = TicketCC
        exclude = ('ticket',)

    def __init__(self, *args, **kwargs):
        """
        Filters the user dropdown according to staff-only settings.
        """
        super(TicketCCForm, self).__init__(*args, **kwargs)
        if helpdesk_settings.HELPDESK_STAFF_ONLY_TICKET_CC:
            users = User.objects.filter(is_active=True, is_staff=True).order_by(User.USERNAME_FIELD)
        else:
            users = User.objects.filter(is_active=True).order_by(User.USERNAME_FIELD)
        self.fields['user'].queryset = users


class TicketDependencyForm(forms.ModelForm):
    """
    Model form for creating or editing ticket dependencies.

    Allows defining which ticket must be resolved before another.

    Based on:
        - `TicketDependency` model
    """
    class Meta:
        model = TicketDependency
        exclude = ('ticket',)
