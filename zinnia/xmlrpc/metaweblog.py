"""
XML-RPC methods of Zinnia (metaWeblog API)

This module provides XML-RPC endpoints to allow remote access and integration
with blogging clients that implement the MetaWeblog, Blogger, and WordPress APIs.

Supported operations:
- Blog/user info retrieval
- Post CRUD operations (create, update, delete, get)
- Category and tag management
- Author listing
- Media uploads

Each XML-RPC function is exposed using the @xmlrpc_func decorator from django-xmlrpc.
"""

from datetime import datetime
try:
    from xmlrpc.client import DateTime, Fault
except ImportError:  # Python 2 fallback
    from xmlrpclib import DateTime, Fault

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils import six, timezone
from django.utils.translation import gettext as _

from django_xmlrpc.decorators import xmlrpc_func

from tagging.models import Tag
from zinnia.managers import DRAFT, PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.settings import PROTOCOL

# Error codes based on NucleusCMS standard
LOGIN_ERROR = 801
PERMISSION_DENIED = 803


def authenticate(username, password, permission=None):
    """
    Authenticate a user against the Author model and optionally check permission.

    Raises:
        Fault: If authentication or permission fails.

    Returns:
        Author instance if successful.
    """
    try:
        author = Author.objects.get(
            **{'%s__exact' % Author.USERNAME_FIELD: username})
    except Author.DoesNotExist:
        raise Fault(LOGIN_ERROR, _('Username is incorrect.'))
    if not author.check_password(password):
        raise Fault(LOGIN_ERROR, _('Password is invalid.'))
    if not author.is_staff or not author.is_active:
        raise Fault(PERMISSION_DENIED, _('User account unavailable.'))
    if permission and not author.has_perm(permission):
        raise Fault(PERMISSION_DENIED, _('User cannot %s.') % permission)
    return author


def blog_structure(site):
    """
    Return the XML-RPC blog structure.
    """
    return {
        'blogid': settings.SITE_ID,
        'blogName': site.name,
        'url': '%s://%s%s' % (
            PROTOCOL, site.domain, reverse('zinnia:entry_archive_index'))
    }


def user_structure(user, site):
    """
    Return user structure used in Blogger API.
    """
    full_name = user.get_full_name().split()
    first_name = full_name[0]
    last_name = full_name[1] if len(full_name) > 1 else ''
    return {
        'userid': user.pk,
        'email': user.email,
        'nickname': user.get_username(),
        'lastname': last_name,
        'firstname': first_name,
        'url': '%s://%s%s' % (PROTOCOL, site.domain, user.get_absolute_url())
    }


def author_structure(user):
    """
    Return author structure used in WordPress API.
    """
    return {
        'user_id': user.pk,
        'user_login': user.get_username(),
        'display_name': str(user),
        'user_email': user.email
    }


def category_structure(category, site):
    """
    Return category structure with WordPress/MovableType extensions.
    """
    return {
        'description': category.title,
        'htmlUrl': '%s://%s%s' % (PROTOCOL, site.domain, category.get_absolute_url()),
        'rssUrl': '%s://%s%s' % (PROTOCOL, site.domain,
                                 reverse('zinnia:category_feed', args=[category.tree_path])),
        'categoryId': category.pk,
        'parentId': category.parent.pk if category.parent else 0,
        'categoryDescription': category.description,
        'categoryName': category.title
    }


def tag_structure(tag, site):
    """
    Return tag structure with RSS and permalink.
    """
    return {
        'tag_id': tag.pk,
        'name': tag.name,
        'count': tag.count,
        'slug': tag.name,
        'html_url': '%s://%s%s' % (PROTOCOL, site.domain,
                                   reverse('zinnia:tag_detail', args=[tag.name])),
        'rss_url': '%s://%s%s' % (PROTOCOL, site.domain,
                                  reverse('zinnia:tag_feed', args=[tag.name]))
    }


def post_structure(entry, site):
    """
    Return a post's structure in the MetaWeblog/WordPress format.
    """
    author = entry.authors.first()
    return {
        'title': entry.title,
        'description': six.text_type(entry.html_content),
        'link': '%s://%s%s' % (PROTOCOL, site.domain, entry.get_absolute_url()),
        'permaLink': '%s://%s%s' % (PROTOCOL, site.domain, entry.get_absolute_url()),
        'categories': [cat.title for cat in entry.categories.all()],
        'dateCreated': DateTime(entry.creation_date.isoformat()),
        'postid': entry.pk,
        'userid': author.get_username(),
        'mt_excerpt': entry.excerpt,
        'mt_allow_comments': int(entry.comment_enabled),
        'mt_allow_pings': int(entry.pingback_enabled or entry.trackback_enabled),
        'mt_keywords': entry.tags,
        'wp_author': author.get_username(),
        'wp_author_id': author.pk,
        'wp_author_display_name': str(author),
        'wp_password': entry.password,
        'wp_slug': entry.slug,
        'sticky': entry.featured
    }


# XML-RPC Method Implementations

@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_users_blogs(apikey, username, password):
    """Return blog info for user."""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [blog_structure(site)]


@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_user_info(apikey, username, password):
    """Return user info for Blogger API."""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return user_structure(user, site)


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_authors(apikey, username, password):
    """Return all staff authors."""
    authenticate(username, password)
    return [author_structure(author) for author in Author.objects.filter(is_staff=True)]


@xmlrpc_func(returns='boolean', args=['string', 'string', 'string', 'string', 'string'])
def delete_post(apikey, post_id, username, password, publish):
    """Delete a post by ID if user is an author."""
    user = authenticate(username, password, 'zinnia.delete_entry')
    Entry.objects.get(id=post_id, authors=user).delete()
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_post(post_id, username, password):
    """Return post by ID."""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return post_structure(Entry.objects.get(id=post_id, authors=user), site)


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string', 'integer'])
def get_recent_posts(blog_id, username, password, number):
    """Return recent posts by user."""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return [post_structure(entry, site)
            for entry in Entry.objects.filter(authors=user)[:number]]


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_tags(blog_id, username, password):
    """Return tags used in published entries."""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [tag_structure(tag, site)
            for tag in Tag.objects.usage_for_queryset(Entry.published.all(), counts=True)]


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_categories(blog_id, username, password):
    """Return all categories."""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [category_structure(category, site) for category in Category.objects.all()]


@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'struct'])
def new_category(blog_id, username, password, category_struct):
    """Create a new category."""
    authenticate(username, password, 'zinnia.add_category')
    category_dict = {
        'title': category_struct['name'],
        'description': category_struct['description'],
        'slug': category_struct['slug']
    }
    if int(category_struct['parent_id']):
        category_dict['parent'] = Category.objects.get(pk=category_struct['parent_id'])
    return Category.objects.create(**category_dict).pk


@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'struct', 'boolean'])
def new_post(blog_id, username, password, post, publish):
    """Create a new blog post."""
    user = authenticate(username, password, 'zinnia.add_entry')
    creation_date = timezone.now()
    if post.get('dateCreated'):
        creation_date = datetime.strptime(post['dateCreated'].value[:18], '%Y-%m-%dT%H:%M:%S')
        if settings.USE_TZ:
            creation_date = timezone.make_aware(creation_date, timezone.utc)

    entry_dict = {
        'title': post['title'],
        'content': post['description'],
        'excerpt': post.get('mt_excerpt', ''),
        'publication_date': creation_date,
        'creation_date': creation_date,
        'last_update': creation_date,
        'comment_enabled': post.get('mt_allow_comments', 1) == 1,
        'pingback_enabled': post.get('mt_allow_pings', 1) == 1,
        'trackback_enabled': post.get('mt_allow_pings', 1) == 1,
        'featured': post.get('sticky', 0) == 1,
        'tags': post.get('mt_keywords', ''),
        'slug': post.get('wp_slug', slugify(post['title'])),
        'password': post.get('wp_password', '')
    }

    if user.has_perm('zinnia.can_change_status'):
        entry_dict['status'] = PUBLISHED if publish else DRAFT

    entry = Entry.objects.create(**entry_dict)

    author = user
    if 'wp_author_id' in post and user.has_perm('zinnia.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = Author.objects.get(pk=post['wp_author_id'])
    entry.authors.add(author)
    entry.sites.add(Site.objects.get_current())

    if 'categories' in post:
        entry.categories.add(*[
            Category.objects.get_or_create(title=cat, slug=slugify(cat))[0]
            for cat in post['categories']
        ])
    return entry.pk


@xmlrpc_func(returns='boolean', args=['string', 'string', 'string', 'struct', 'boolean'])
def edit_post(post_id, username, password, post, publish):
    """Edit an existing post."""
    user = authenticate(username, password, 'zinnia.change_entry')
    entry = Entry.objects.get(id=post_id, authors=user)

    creation_date = entry.creation_date
    if post.get('dateCreated'):
        creation_date = datetime.strptime(post['dateCreated'].value[:18], '%Y-%m-%dT%H:%M:%S')
        if settings.USE_TZ:
            creation_date = timezone.make_aware(creation_date, timezone.utc)

    entry.title = post['title']
    entry.content = post['description']
    entry.excerpt = post.get('mt_excerpt', '')
    entry.publication_date = creation_date
    entry.creation_date = creation_date
    entry.last_update = timezone.now()
    entry.comment_enabled = post.get('mt_allow_comments', 1) == 1
    entry.pingback_enabled = post.get('mt_allow_pings', 1) == 1
    entry.trackback_enabled = post.get('mt_allow_pings', 1) == 1
    entry.featured = post.get('sticky', 0) == 1
    entry.tags = post.get('mt_keywords', '')
    entry.slug = post.get('wp_slug', slugify(post['title']))
    if user.has_perm('zinnia.can_change_status'):
        entry.status = PUBLISHED if publish else DRAFT
    entry.password = post.get('wp_password', '')
    entry.save()

    if 'wp_author_id' in post and user.has_perm('zinnia.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = Author.objects.get(pk=post['wp_author_id'])
            entry.authors.set([author])

    if 'categories' in post:
        entry.categories.set([
            Category.objects.get_or_create(title=cat, slug=slugify(cat))[0]
            for cat in post['categories']
        ])
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'struct'])
def new_media_object(blog_id, username, password, media):
    """Upload media via MetaWeblog API."""
    authenticate(username, password)
    path = default_storage.save(Entry().image_upload_to(media['name']),
                                ContentFile(media['bits'].data))
    return {'url': default_storage.url(path)}
