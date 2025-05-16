"""
CategoryAdmin for Zinnia

Defines the Django admin interface for managing blog categories in Zinnia.

Features:
- Uses a custom admin form.
- Displays a tree path to reflect category hierarchy.
- Prepopulates the slug field from the title.
- Supports filtering and searching by parent or description.
"""

from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from zinnia.admin.forms import CategoryAdminForm


class CategoryAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Category model in Zinnia.

    This class customizes:
    - Display of fields in list and detail views
    - Form behavior using `CategoryAdminForm`
    - Prepopulation of slug from title
    - HTML rendering of the tree path
    """
    form = CategoryAdminForm
    fields = ('title', 'parent', 'description', 'slug')
    list_display = ('title', 'slug', 'get_tree_path', 'description')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description')
    list_filter = ('parent',)

    def __init__(self, model, admin_site):
        """
        Inject the admin site into the form for further customization.
        """
        self.form.admin_site = admin_site
        super(CategoryAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, category):
        """
        Return a clickable HTML link showing the full category tree path.

        If `get_absolute_url` fails due to routing issues,
        fallback to plain text display.

        Args:
            category (Category): The category instance.

        Returns:
            str: HTML string or plain text fallback.
        """
        try:
            return format_html(
                '<a href="{}" target="blank">/{}/</a>',
                category.get_absolute_url(), category.tree_path)
        except NoReverseMatch:
            return '/%s/' % category.tree_path

    get_tree_path.short_description = _('tree path')
