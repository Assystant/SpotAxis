"""
Views for Zinnia quick entry posting.

This module allows users with the correct permissions to rapidly create
blog entries via a simplified form and workflow, without going through
the full Django admin interface.
"""

try:
    from urllib.parse import urlencode  # Python 3
except:  # Python 2 fallback
    from urllib import urlencode

from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse  # Django < 1.10
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.utils.html import linebreaks
from django.views.generic.base import View

from zinnia.managers import DRAFT, PUBLISHED
from zinnia.models.entry import Entry
from zinnia.settings import MARKUP_LANGUAGE


class QuickEntryForm(forms.ModelForm):
    """
    Form used to create a quick blog entry submission.

    Excludes comment and trackback related fields since
    those are not relevant for quick publishing.
    """

    class Meta:
        model = Entry
        exclude = ('comment_count', 'pingback_count', 'trackback_count')


class QuickEntry(View):
    """
    View handling fast blog entry creation.

    Allows authenticated users with `zinnia.add_entry` permission
    to quickly post an entry via a POST request. A GET request redirects
    to the normal admin entry creation form.

    Supports saving as a draft or publishing directly based on the
    submitted data.
    """

    @method_decorator(permission_required('zinnia.add_entry'))
    def dispatch(self, *args, **kwargs):
        """
        Wrap the dispatch method with permission enforcement.
        Only users with the `add_entry` permission may access this view.
        """
        return super(QuickEntry, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Redirect users to the standard Django admin entry creation page.

        Quick entry creation is only supported via POST.
        """
        return redirect('admin:zinnia_entry_add')

    def post(self, request, *args, **kwargs):
        """
        Handle POST data to create a new Entry.

        - If valid, saves the entry and redirects to its detail page.
        - If invalid, redirects to the admin entry creation form with
          pre-filled data for manual correction.

        POST Parameters:
        - title: title of the entry
        - content: body content
        - tags: comma-separated tags
        - save_draft (optional): if present, entry is saved as draft
        """
        now = timezone.now()
        data = {
            'title': request.POST.get('title'),
            'slug': slugify(request.POST.get('title')),
            'status': DRAFT if 'save_draft' in request.POST else PUBLISHED,
            'sites': [Site.objects.get_current().pk],
            'authors': [request.user.pk],
            'content_template': 'zinnia/_entry_detail.html',
            'detail_template': 'entry_detail.html',
            'publication_date': now,
            'creation_date': now,
            'last_update': now,
            'content': request.POST.get('content'),
            'tags': request.POST.get('tags'),
        }

        form = QuickEntryForm(data)

        if form.is_valid():
            # Convert content if markup type is HTML
            form.instance.content = self.htmlize(form.cleaned_data['content'])
            entry = form.save()
            return redirect(entry)

        # Fallback: redirect to admin entry form with prefilled values
        data = {
            'title': smart_str(request.POST.get('title', '')),
            'content': smart_str(self.htmlize(request.POST.get('content', ''))),
            'tags': smart_str(request.POST.get('tags', '')),
            'slug': slugify(request.POST.get('title', '')),
            'authors': request.user.pk,
            'sites': Site.objects.get_current().pk
        }

        return redirect('%s?%s' % (
            reverse('admin:zinnia_entry_add'), urlencode(data)
        ))

    def htmlize(self, content):
        """
        Format content as HTML if `MARKUP_LANGUAGE` is set to 'html'.

        This helps improve rendering and avoids raw linebreak issues
        in WYSIWYG editors like WYMEditor.
        """
        if MARKUP_LANGUAGE == 'html':
            return linebreaks(content)
        return content
