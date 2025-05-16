"""
EntryAdmin for Zinnia

Defines the Django admin interface for managing blog entries in the Zinnia application.

Features:
- Rich field layout with collapsible sections.
- Inline filters for authors, categories, publication status, and sites.
- Custom list display methods for authors, categories, tags, and short URL.
- Admin actions to publish, hide, close comments, ping directories, mark featured, and more.
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db.models import Q
from django.utils import timezone
from django.utils.html import conditional_escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from zinnia import settings
from zinnia.admin.filters import AuthorListFilter, CategoryListFilter
from zinnia.admin.forms import EntryAdminForm
from zinnia.comparison import EntryPublishedVectorBuilder
from zinnia.managers import HIDDEN, PUBLISHED
from zinnia.models.author import Author
from zinnia.ping import DirectoryPinger


class EntryAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Entry model in Zinnia.

    Provides advanced content management features including:
    - Template selection
    - Site association
    - Pingback/Trackback/Comments toggling
    - Visibility and access control
    - Author assignments and related entries
    """
    form = EntryAdminForm
    date_hierarchy = 'publication_date'
    fieldsets = (
        (_('Content'), {
            'fields': (('title', 'status'), 'lead', 'content',)}),
        (_('Illustration'), {
            'fields': ('image', 'image_caption'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Publication'), {
            'fields': ('publication_date', 'sites',
                       ('start_publication', 'end_publication')),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Discussions'), {
            'fields': ('comment_enabled', 'pingback_enabled',
                       'trackback_enabled'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Privacy'), {
            'fields': ('login_required', 'password'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Templates'), {
            'fields': ('content_template', 'detail_template'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Metadatas'), {
            'fields': ('featured', 'excerpt', 'authors', 'related'),
            'classes': ('collapse', 'collapse-closed')}),
        (None, {'fields': ('categories', 'tags', 'slug')}))
    list_filter = (CategoryListFilter, AuthorListFilter,
                   'publication_date', 'sites', 'status')
    list_display = ('get_title', 'get_authors', 'get_categories',
                    'get_tags', 'get_sites', 'get_is_visible', 'featured',
                    'get_short_url', 'publication_date')
    radio_fields = {'content_template': admin.VERTICAL,
                    'detail_template': admin.VERTICAL}
    filter_horizontal = ('categories', 'authors', 'related')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'excerpt', 'content', 'tags')
    actions = ['make_mine', 'make_published', 'make_hidden',
               'close_comments', 'close_pingbacks', 'close_trackbacks',
               'ping_directories', 'put_on_top',
               'mark_featured', 'unmark_featured']
    actions_on_top = True
    actions_on_bottom = True

    def __init__(self, model, admin_site):
        """
        Inject admin site into the form context.
        """
        self.form.admin_site = admin_site
        super(EntryAdmin, self).__init__(model, admin_site)

    # ----- Display Methods -----

    def get_title(self, entry):
        """
        Return the entry title with word count and total reaction count.
        """
        title = _('%(title)s (%(word_count)i words)') % {
            'title': entry.title, 'word_count': entry.word_count}
        reaction_count = int(entry.comment_count +
                             entry.pingback_count +
                             entry.trackback_count)
        if reaction_count:
            return ungettext_lazy(
                '%(title)s (%(reactions)i reaction)',
                '%(title)s (%(reactions)i reactions)', reaction_count) % {
                'title': title, 'reactions': reaction_count}
        return title
    get_title.short_description = _('title')

    def get_authors(self, entry):
        """
        Return HTML list of authors for an entry.
        """
        try:
            return format_html_join(
                ', ', '<a href="{}" target="blank">{}</a>',
                [(author.get_absolute_url(),
                  getattr(author, author.USERNAME_FIELD))
                 for author in entry.authors.all()])
        except NoReverseMatch:
            return ', '.join(
                [conditional_escape(getattr(author, author.USERNAME_FIELD))
                 for author in entry.authors.all()])
    get_authors.short_description = _('author(s)')

    def get_categories(self, entry):
        """
        Return HTML list of categories for an entry.
        """
        try:
            return format_html_join(
                ', ', '<a href="{}" target="blank">{}</a>',
                [(category.get_absolute_url(), category.title)
                 for category in entry.categories.all()])
        except NoReverseMatch:
            return ', '.join([conditional_escape(category.title)
                              for category in entry.categories.all()])
    get_categories.short_description = _('category(s)')

    def get_tags(self, entry):
        """
        Return HTML list of tags for an entry.
        """
        try:
            return format_html_join(
                ', ', '<a href="{}" target="blank">{}</a>',
                [(reverse('zinnia:tag_detail', args=[tag]), tag)
                 for tag in entry.tags_list])
        except NoReverseMatch:
            return conditional_escape(entry.tags)
    get_tags.short_description = _('tag(s)')

    def get_sites(self, entry):
        """
        Return HTML list of associated sites.
        """
        try:
            index_url = reverse('zinnia:entry_archive_index')
        except NoReverseMatch:
            index_url = ''
        return format_html_join(
            ', ', '<a href="{}://{}{}" target="blank">{}</a>',
            [(settings.PROTOCOL, site.domain, index_url,
              conditional_escape(site.name)) for site in entry.sites.all()])
    get_sites.short_description = _('site(s)')

    def get_short_url(self, entry):
        """
        Return HTML for the short URL of the entry.
        """
        try:
            short_url = entry.short_url
        except NoReverseMatch:
            short_url = entry.get_absolute_url()
        return format_html('<a href="{url}" target="blank">{url}</a>',
                           url=short_url)
    get_short_url.short_description = _('short url')

    def get_is_visible(self, entry):
        """
        Return whether the entry is currently visible.
        """
        return entry.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    # ----- Query Methods -----

    def get_queryset(self, request):
        """
        Filter entries based on permissions.
        """
        if not request.user.has_perm('zinnia.can_view_all'):
            queryset = self.model.objects.filter(authors__pk=request.user.pk)
        else:
            queryset = super(EntryAdmin, self).get_queryset(request)
        return queryset.prefetch_related('categories', 'authors', 'sites')

    def get_changeform_initial_data(self, request):
        """
        Prepopulate authors and sites on new entry.
        """
        get_data = super(EntryAdmin, self).get_changeform_initial_data(request)
        return get_data or {
            'sites': [Site.objects.get_current().pk],
            'authors': [request.user.pk]
        }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Restrict author list to staff or previously published users.
        """
        if db_field.name == 'authors':
            kwargs['queryset'] = Author.objects.filter(
                Q(is_staff=True) | Q(entries__isnull=False)
            ).distinct()
        return super(EntryAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        Restrict editable fields based on user's permissions.
        """
        readonly_fields = list(super(EntryAdmin, self).get_readonly_fields(request, obj))
        if not request.user.has_perm('zinnia.can_change_status'):
            readonly_fields.append('status')
        if not request.user.has_perm('zinnia.can_change_author'):
            readonly_fields.append('authors')
        return readonly_fields

    def get_actions(self, request):
        """
        Filter available actions based on user permissions.
        """
        actions = super(EntryAdmin, self).get_actions(request)
        if not actions:
            return actions
        if (not request.user.has_perm('zinnia.can_change_author') or
                not request.user.has_perm('zinnia.can_view_all')):
            actions.pop('make_mine', None)
        if not request.user.has_perm('zinnia.can_change_status'):
            actions.pop('make_hidden', None)
            actions.pop('make_published', None)
        if not settings.PING_DIRECTORIES:
            actions.pop('ping_directories', None)
        return actions

    # ----- Admin Actions -----

    def make_mine(self, request, queryset):
        """Assign selected entries to current user."""
        author = Author.objects.get(pk=request.user.pk)
        for entry in queryset:
            if author not in entry.authors.all():
                entry.authors.add(author)
        self.message_user(request, _('The selected entries now belong to you.'))
    make_mine.short_description = _('Set the entries to the user')

    def make_published(self, request, queryset):
        """Publish selected entries."""
        queryset.update(status=PUBLISHED)
        EntryPublishedVectorBuilder().cache_flush()
        self.ping_directories(request, queryset, messages=False)
        self.message_user(request, _('The selected entries are now marked as published.'))
    make_published.short_description = _('Set entries selected as published')

    def make_hidden(self, request, queryset):
        """Hide selected entries."""
        queryset.update(status=HIDDEN)
        EntryPublishedVectorBuilder().cache_flush()
        self.message_user(request, _('The selected entries are now marked as hidden.'))
    make_hidden.short_description = _('Set entries selected as hidden')

    def close_comments(self, request, queryset):
        """Close comments for selected entries."""
        queryset.update(comment_enabled=False)
        self.message_user(request, _('Comments are now closed for selected entries.'))
    close_comments.short_description = _('Close the comments for selected entries')

    def close_pingbacks(self, request, queryset):
        """Disable pingbacks for selected entries."""
        queryset.update(pingback_enabled=False)
        self.message_user(request, _('Pingbacks are now closed for selected entries.'))
    close_pingbacks.short_description = _('Close the pingbacks for selected entries')

    def close_trackbacks(self, request, queryset):
        """Disable trackbacks for selected entries."""
        queryset.update(trackback_enabled=False)
        self.message_user(request, _('Trackbacks are now closed for selected entries.'))
    close_trackbacks.short_description = _('Close the trackbacks for selected entries')

    def put_on_top(self, request, queryset):
        """Set publication date to now (move to top)."""
        queryset.update(publication_date=timezone.now())
        self.ping_directories(request, queryset, messages=False)
        self.message_user(request, _('The selected entries are now set at the current date.'))
    put_on_top.short_description = _('Put the selected entries on top at the current date')

    def mark_featured(self, request, queryset):
        """Mark entries as featured."""
        queryset.update(featured=True)
        self.message_user(request, _('Selected entries are now marked as featured.'))
    mark_featured.short_description = _('Mark selected entries as featured')

    def unmark_featured(self, request, queryset):
        """Unmark entries as featured."""
        queryset.update(featured=False)
        self.message_user(request, _('Selected entries are no longer marked as featured.'))
    unmark_featured.short_description = _('Unmark selected entries as featured')

    def ping_directories(self, request, queryset, messages=True):
        """
        Ping external directories for selected entries.

        Sends XML-RPC pingbacks to configured directories.
        """
        for directory in settings.PING_DIRECTORIES:
            pinger = DirectoryPinger(directory, queryset)
            pinger.join()
            if messages:
                success = 0
                for result in pinger.results:
                    if not result.get('flerror', True):
                        success += 1
                    else:
                        self.message_user(request, '%s : %s' % (directory, result['message']))
                if success:
                    self.message_user(
                        request,
                        _('%(directory)s directory successfully pinged %(success)d entries.') %
                        {'directory': directory, 'success': success})
    ping_directories.short_description = _('Ping Directories for selected entries')
