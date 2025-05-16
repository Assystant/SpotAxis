"""
Base entry models for Zinnia.

This module defines the various abstract model components that make up
a blog entry in the Zinnia blogging system. Each abstract class encapsulates
specific aspects of an entry such as its content, discussion features,
authorship, categorization, SEO, media support, access restrictions, and templating.

All classes are composed into the final AbstractEntry model, which can then be
used by the concrete Entry model depending on the project configuration.
"""

import os
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

import django_comments as comments
from django_comments.models import CommentFlag

from tagging.fields import TagField
from tagging.utils import parse_tag_input

from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.managers import EntryPublishedManager, entries_published
from zinnia.markups import html_format
from zinnia.preview import HTMLPreview
from zinnia.settings import (
    AUTO_CLOSE_COMMENTS_AFTER,
    AUTO_CLOSE_PINGBACKS_AFTER,
    AUTO_CLOSE_TRACKBACKS_AFTER,
    ENTRY_CONTENT_TEMPLATES,
    ENTRY_DETAIL_TEMPLATES,
    UPLOAD_TO
)
from zinnia.url_shortener import get_url_shortener


@python_2_unicode_compatible
class CoreEntry(models.Model):
    """
    Abstract core entry model providing the essential fields and logic
    for publishing blog content over time.
    """
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique_for_date='publication_date',
                             help_text=_("Used to build the entry's URL."))
    status = models.IntegerField(_('status'), db_index=True, choices=STATUS_CHOICES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), db_index=True,
                                            default=timezone.now,
                                            help_text=_("Used to build the entry's URL."))
    start_publication = models.DateTimeField(_('start publication'), db_index=True,
                                             blank=True, null=True,
                                             help_text=_('Start date of publication.'))
    end_publication = models.DateTimeField(_('end publication'), db_index=True,
                                           blank=True, null=True,
                                           help_text=_('End date of publication.'))
    sites = models.ManyToManyField(Site, related_name='entries', verbose_name=_('sites'),
                                   help_text=_('Sites where the entry will be published.'))
    creation_date = models.DateTimeField(_('creation date'), default=timezone.now)
    last_update = models.DateTimeField(_('last update'), default=timezone.now)

    objects = models.Manager()
    published = EntryPublishedManager()

    @property
    def is_actual(self):
        """Check if the entry is currently within its publication window."""
        now = timezone.now()
        if self.start_publication and now < self.start_publication:
            return False
        if self.end_publication and now >= self.end_publication:
            return False
        return True

    @property
    def is_visible(self):
        """Check if the entry is visible and published."""
        return self.is_actual and self.status == PUBLISHED

    @property
    def previous_entry(self):
        """Return the previous published entry, if available."""
        return self.previous_next_entries[0]

    @property
    def next_entry(self):
        """Return the next published entry, if available."""
        return self.previous_next_entries[1]

    @property
    def previous_next_entries(self):
        """Return a tuple (previous, next) of adjacent published entries."""
        previous_next = getattr(self, 'previous_next', None)
        if previous_next is None:
            if not self.is_visible:
                previous_next = (None, None)
                setattr(self, 'previous_next', previous_next)
                return previous_next
            entries = list(self.__class__.published.all())
            index = entries.index(self)
            previous = entries[index + 1] if index + 1 < len(entries) else None
            next = entries[index - 1] if index > 0 else None
            previous_next = (previous, next)
            setattr(self, 'previous_next', previous_next)
        return previous_next

    @property
    def short_url(self):
        """Return a shortened URL for the entry."""
        return get_url_shortener()(self)

    def save(self, *args, **kwargs):
        """Override save to update the last_update timestamp."""
        self.last_update = timezone.now()
        super(CoreEntry, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        """Build the entry's URL using the slug and publication date."""
        publication_date = self.publication_date
        if timezone.is_aware(publication_date):
            publication_date = timezone.localtime(publication_date)
        return ('zinnia:entry_detail', (), {
            'year': publication_date.strftime('%Y'),
            'month': publication_date.strftime('%m'),
            'day': publication_date.strftime('%d'),
            'slug': self.slug})

    def __str__(self):
        return '%s: %s' % (self.title, self.get_status_display())

    class Meta:
        abstract = True
        ordering = ['-publication_date']
        get_latest_by = 'publication_date'
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        index_together = [['slug', 'publication_date'],
                          ['status', 'publication_date',
                           'start_publication', 'end_publication']]
        permissions = (('can_view_all', 'Can view all entries'),
                       ('can_change_status', 'Can change status'),
                       ('can_change_author', 'Can change author(s)'))








class ContentEntry(models.Model):
    """
    Abstract content model providing a field and helper methods
    for managing the body of an entry.
    """
    content = models.TextField(_('content'), blank=True)

    @property
    def html_content(self):
        """Return the content field formatted into HTML."""
        return html_format(self.content)

    @property
    def html_preview(self):
        """Return a formatted HTML preview of the content or lead."""
        return HTMLPreview(self.html_content, getattr(self, 'html_lead', ''))

    @property
    def word_count(self):
        """Return the number of words in the HTML-stripped content."""
        return len(strip_tags(self.html_content).split())

    class Meta:
        abstract = True


class DiscussionsEntry(models.Model):
    """
    Abstract model for managing discussions on entries,
    including comments, pingbacks, and trackbacks.
    """
    comment_enabled = models.BooleanField(_('comments enabled'), default=True)
    pingback_enabled = models.BooleanField(_('pingbacks enabled'), default=True)
    trackback_enabled = models.BooleanField(_('trackbacks enabled'), default=True)

    comment_count = models.IntegerField(_('comment count'), default=0)
    pingback_count = models.IntegerField(_('pingback count'), default=0)
    trackback_count = models.IntegerField(_('trackback count'), default=0)

    @property
    def discussions(self):
        """Return all public and non-removed discussions for this entry."""
        return comments.get_model().objects.for_model(self).filter(is_public=True, is_removed=False)

    @property
    def comments(self):
        """Return filtered public comments that have moderator approval if flagged."""
        return self.discussions.filter(Q(flags=None) | Q(flags__flag=CommentFlag.MODERATOR_APPROVAL))

    @property
    def pingbacks(self):
        """Return pingbacks only."""
        return self.discussions.filter(flags__flag=PINGBACK)

    @property
    def trackbacks(self):
        """Return trackbacks only."""
        return self.discussions.filter(flags__flag=TRACKBACK)

    def discussion_is_still_open(self, discussion_type, auto_close_after):
        """
        Determine whether a discussion type is still open
        based on time since publication.
        """
        discussion_enabled = getattr(self, discussion_type)
        if discussion_enabled and isinstance(auto_close_after, int) and auto_close_after >= 0:
            return (timezone.now() - (self.start_publication or self.publication_date)).days < auto_close_after
        return discussion_enabled

    @property
    def comments_are_open(self):
        """Check if comments are open based on AUTO_CLOSE_COMMENTS_AFTER setting."""
        return self.discussion_is_still_open('comment_enabled', AUTO_CLOSE_COMMENTS_AFTER)

    @property
    def pingbacks_are_open(self):
        """Check if pingbacks are open based on AUTO_CLOSE_PINGBACKS_AFTER setting."""
        return self.discussion_is_still_open('pingback_enabled', AUTO_CLOSE_PINGBACKS_AFTER)

    @property
    def trackbacks_are_open(self):
        """Check if trackbacks are open based on AUTO_CLOSE_TRACKBACKS_AFTER setting."""
        return self.discussion_is_still_open('trackback_enabled', AUTO_CLOSE_TRACKBACKS_AFTER)

    class Meta:
        abstract = True


class RelatedEntry(models.Model):
    """Abstract model for manually associating entries with related entries."""
    related = models.ManyToManyField('self', blank=True, verbose_name=_('related entries'))

    @property
    def related_published(self):
        """Return only the related entries that are published."""
        return entries_published(self.related)

    class Meta:
        abstract = True


class LeadEntry(models.Model):
    """Abstract model to provide a lead paragraph for an entry."""
    lead = models.TextField(_('lead'), blank=True, help_text=_('Lead paragraph'))

    @property
    def html_lead(self):
        """Return the lead content formatted into HTML."""
        return html_format(self.lead)

    class Meta:
        abstract = True


class ExcerptEntry(models.Model):
    """
    Abstract model to provide an SEO-focused excerpt for the entry.
    If no excerpt is provided, it is auto-generated from content.
    """
    excerpt = models.TextField(_('excerpt'), blank=True, help_text=_('Used for SEO purposes.'))

    def save(self, *args, **kwargs):
        if not self.excerpt and self.status == PUBLISHED:
            self.excerpt = Truncator(strip_tags(getattr(self, 'content', ''))).words(50)
        super(ExcerptEntry, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ImageEntry(models.Model):
    """Abstract model for adding an image and caption to an entry."""
    def image_upload_to(self, filename):
        now = timezone.now()
        filename, extension = os.path.splitext(filename)
        return os.path.join(UPLOAD_TO, now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'), f'{slugify(filename)}{extension}')

    image = models.ImageField(_('image'), blank=True, upload_to='zinnia.entry.image_upload_to_dispatcher', help_text=_('Used for illustration.'))
    image_caption = models.TextField(_('caption'), blank=True, help_text=_("Image's caption."))

    class Meta:
        abstract = True


def image_upload_to_dispatcher(entry, filename):
    """Separate dispatcher to avoid migration issues with method references."""
    return entry.image_upload_to(filename)


class FeaturedEntry(models.Model):
    """Abstract model for marking an entry as featured."""
    featured = models.BooleanField(_('featured'), default=False)

    class Meta:
        abstract = True


class AuthorsEntry(models.Model):
    """Abstract model for assigning authors to an entry."""
    authors = models.ManyToManyField('zinnia.Author', blank=True, related_name='entries', verbose_name=_('authors'))

    class Meta:
        abstract = True


class CategoriesEntry(models.Model):
    """Abstract model for assigning categories to an entry."""
    categories = models.ManyToManyField('zinnia.Category', blank=True, related_name='entries', verbose_name=_('categories'))

    class Meta:
        abstract = True


class TagsEntry(models.Model):
    """Abstract model for tagging entries."""
    tags = TagField(_('tags'))

    @property
    def tags_list(self):
        """Return a list of parsed tags."""
        return parse_tag_input(self.tags)

    class Meta:
        abstract = True


class LoginRequiredEntry(models.Model):
    """Restrict entry visibility to authenticated users."""
    login_required = models.BooleanField(_('login required'), default=False, help_text=_('Only authenticated users can view the entry.'))

    class Meta:
        abstract = True


class PasswordRequiredEntry(models.Model):
    """Restrict entry visibility to users with the correct password."""
    password = models.CharField(_('password'), max_length=50, blank=True, help_text=_('Protects the entry with a password.'))

    class Meta:
        abstract = True


class ContentTemplateEntry(models.Model):
    """Allow the entry content to be rendered using a custom template."""
    content_template = models.CharField(_('content template'), max_length=250, default='zinnia/_entry_detail.html',
                                        choices=[('zinnia/_entry_detail.html', _('Default template'))] + ENTRY_CONTENT_TEMPLATES,
                                        help_text=_("Template used to display the entry's content."))

    class Meta:
        abstract = True


class DetailTemplateEntry(models.Model):
    """Allow the entry detail page to use a custom template."""
    detail_template = models.CharField(_('detail template'), max_length=250, default='entry_detail.html',
                                       choices=[('entry_detail.html', _('Default template'))] + ENTRY_DETAIL_TEMPLATES,
                                       help_text=_("Template used to display the entry's detail page."))

    class Meta:
        abstract = True


class AbstractEntry(
    CoreEntry,
    ContentEntry,
    DiscussionsEntry,
    RelatedEntry,
    LeadEntry,
    ExcerptEntry,
    ImageEntry,
    FeaturedEntry,
    AuthorsEntry,
    CategoriesEntry,
    TagsEntry,
    LoginRequiredEntry,
    PasswordRequiredEntry,
    ContentTemplateEntry,
    DetailTemplateEntry):
    """
    Final abstract blog entry model composed of all the individual
    abstract model components. This allows for customization and modularity
    in defining blog entries in the Zinnia system.
    """
    class Meta(CoreEntry.Meta):
        abstract = True
