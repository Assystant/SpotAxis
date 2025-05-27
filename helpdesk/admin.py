from __future__ import absolute_import
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from helpdesk.models import Queue, Ticket, FollowUp, PreSetReply, KBCategory
from helpdesk.models import EscalationExclusion, EmailTemplate, KBItem
from helpdesk.models import TicketChange, Attachment, IgnoreEmail
from helpdesk.models import CustomField


"""
admin.py - Django admin configuration for django-helpdesk models.

Version: 0.2.0  
Maintainer: Jutda (c) 2008

This module defines how helpdesk models are presented and managed in the
Django admin interface, including list displays, inlines, filters, and
custom formatting.

Registered models include:
- Queue, Ticket, FollowUp, PreSetReply
- KBCategory, KBItem
- EscalationExclusion, EmailTemplate, IgnoreEmail
- CustomField, Attachment, TicketChange
"""


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Queue model.

    - Displays basic metadata like title, slug, email, and locale.
    - Automatically generates the slug from the title.
    """
    list_display = ('title', 'slug', 'email_address', 'locale')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin interface for managing support tickets.

    - Shows status, assigned user, and obfuscated email.
    - Adds filters for queue, assignee, and status.
    - Uses `date_hierarchy` on the ticket creation date.
    """
    list_display = ('title', 'status', 'assigned_to', 'queue', 'hidden_submitter_email',)
    date_hierarchy = 'created'
    list_filter = ('queue', 'assigned_to', 'status')

    def hidden_submitter_email(self, ticket):
        """
        Returns a partially masked email for privacy in admin listing.
        """
        if ticket.submitter_email:
            username, domain = ticket.submitter_email.split("@")
            username = username[:2] + "*" * (len(username) - 2)
            domain = domain[:1] + "*" * (len(domain) - 2) + domain[-1:]
            return "%s@%s" % (username, domain)
        else:
            return ticket.submitter_email
    hidden_submitter_email.short_description = _('Submitter E-Mail')


class TicketChangeInline(admin.StackedInline):
    """
    Inline to display changes made during a FollowUp.
    """
    model = TicketChange


class AttachmentInline(admin.StackedInline):
    """
    Inline to display file attachments within a FollowUp.
    """
    model = Attachment


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    """
    Admin view for ticket follow-ups.

    - Displays related ticket changes and attachments as inlines.
    """
    inlines = [TicketChangeInline, AttachmentInline]


@admin.register(KBItem)
class KBItemAdmin(admin.ModelAdmin):
    """
    Admin interface for knowledge base items.

    - Shows title, category, and last updated timestamp.
    """
    list_display = ('category', 'title', 'last_updated',)
    list_display_links = ('title',)


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """
    Admin config for ticket custom fields.

    - Displays field name, label, and data type.
    """
    list_display = ('name', 'label', 'data_type')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for email templates.

    - Shows template name, heading, and locale.
    - Filters templates by locale.
    """
    list_display = ('template_name', 'heading', 'locale')
    list_filter = ('locale', )


admin.site.register(PreSetReply)
admin.site.register(EscalationExclusion)
admin.site.register(KBCategory)
admin.site.register(IgnoreEmail)
