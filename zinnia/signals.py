"""
Signal handlers of Zinnia

This module defines signal handlers and connections for the Zinnia blogging
platform. These signals help automate various tasks such as:

- Pinging directories and external URLs after a blog entry is saved.
- Keeping comment, pingback, and trackback counts updated.
- Flushing the cache of similar entries.
- Managing comment-related notifications and moderation actions.

It also provides functions to connect and disconnect all these signals cleanly.
"""

import inspect
from functools import wraps

from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import Signal
import django_comments as comments
from django_comments.signals import comment_was_flagged, comment_was_posted

from zinnia import settings
from zinnia.comparison import EntryPublishedVectorBuilder
from zinnia.models.entry import Entry
from zinnia.ping import DirectoryPinger, ExternalUrlsPinger

# Comment model reference
comment_model = comments.get_model()

# Unique identifiers for signal connections
ENTRY_PS_PING_DIRECTORIES = 'zinnia.entry.post_save.ping_directories'
ENTRY_PS_PING_EXTERNAL_URLS = 'zinnia.entry.post_save.ping_external_urls'
ENTRY_PS_FLUSH_SIMILAR_CACHE = 'zinnia.entry.post_save.flush_similar_cache'
ENTRY_PD_FLUSH_SIMILAR_CACHE = 'zinnia.entry.post_delete.flush_similar_cache'
COMMENT_PS_COUNT_DISCUSSIONS = 'zinnia.comment.post_save.count_discussions'
COMMENT_PD_COUNT_DISCUSSIONS = 'zinnia.comment.pre_delete.count_discussions'
COMMENT_WF_COUNT_DISCUSSIONS = 'zinnia.comment.was_flagged.count_discussions'
COMMENT_WP_COUNT_COMMENTS = 'zinnia.comment.was_posted.count_comments'
PINGBACK_WF_COUNT_PINGBACKS = 'zinnia.pingback.was_flagged.count_pingbacks'
TRACKBACK_WF_COUNT_TRACKBACKS = 'zinnia.trackback.was_flagged.count_trackbacks'

# Custom signals for pingbacks and trackbacks
pingback_was_posted = Signal(providing_args=['pingback', 'entry'])
trackback_was_posted = Signal(providing_args=['trackback', 'entry'])


def disable_for_loaddata(signal_handler):
    """
    Decorator that disables signal handlers during 'loaddata' to avoid
    side effects when loading fixtures.
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return  # Skip signal if during loaddata
        signal_handler(*args, **kwargs)
    return wrapper


@disable_for_loaddata
def ping_directories_handler(sender, **kwargs):
    """
    Handler to ping configured directories after an entry is saved.
    """
    entry = kwargs['instance']
    if entry.is_visible and settings.SAVE_PING_DIRECTORIES:
        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [entry])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """
    Handler to ping external URLs referenced in the entry.
    """
    entry = kwargs['instance']
    if entry.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        ExternalUrlsPinger(entry)


@disable_for_loaddata
def flush_similar_cache_handler(sender, **kwargs):
    """
    Handler to flush the cache of similar entries after entry updates or deletions.
    """
    entry = kwargs['instance']
    if entry.is_visible:
        EntryPublishedVectorBuilder().cache_flush()


def count_discussions_handler(sender, **kwargs):
    """
    Updates the discussion counts (comments, pingbacks, trackbacks)
    for an entry when a comment is modified or flagged.
    """
    if kwargs.get('instance') and kwargs.get('created'):
        # Skip if this is a freshly created comment (handled by comment_was_posted)
        return

    comment = kwargs.get('comment') or kwargs.get('instance')
    entry = comment.content_object
    if isinstance(entry, Entry):
        entry.comment_count = entry.comments.count()
        entry.pingback_count = entry.pingbacks.count()
        entry.trackback_count = entry.trackbacks.count()
        entry.save(update_fields=['comment_count', 'pingback_count', 'trackback_count'])


def count_comments_handler(sender, **kwargs):
    """
    Increments Entry.comment_count when a new public comment is posted.
    """
    comment = kwargs['comment']
    if comment.is_public:
        entry = comment.content_object
        if isinstance(entry, Entry):
            entry.comment_count = F('comment_count') + 1
            entry.save(update_fields=['comment_count'])


def count_pingbacks_handler(sender, **kwargs):
    """
    Increments Entry.pingback_count when a pingback is posted.
    """
    entry = kwargs['entry']
    entry.pingback_count = F('pingback_count') + 1
    entry.save(update_fields=['pingback_count'])


def count_trackbacks_handler(sender, **kwargs):
    """
    Increments Entry.trackback_count when a trackback is posted.
    """
    entry = kwargs['entry']
    entry.trackback_count = F('trackback_count') + 1
    entry.save(update_fields=['trackback_count'])


def connect_entry_signals():
    """
    Connect all signal handlers related to Entry model.
    """
    post_save.connect(ping_directories_handler, sender=Entry,
                      dispatch_uid=ENTRY_PS_PING_DIRECTORIES)
    post_save.connect(ping_external_urls_handler, sender=Entry,
                      dispatch_uid=ENTRY_PS_PING_EXTERNAL_URLS)
    post_save.connect(flush_similar_cache_handler, sender=Entry,
                      dispatch_uid=ENTRY_PS_FLUSH_SIMILAR_CACHE)
    post_delete.connect(flush_similar_cache_handler, sender=Entry,
                        dispatch_uid=ENTRY_PD_FLUSH_SIMILAR_CACHE)


def disconnect_entry_signals():
    """
    Disconnect all signal handlers related to Entry model.
    """
    post_save.disconnect(sender=Entry, dispatch_uid=ENTRY_PS_PING_DIRECTORIES)
    post_save.disconnect(sender=Entry, dispatch_uid=ENTRY_PS_PING_EXTERNAL_URLS)
    post_save.disconnect(sender=Entry, dispatch_uid=ENTRY_PS_FLUSH_SIMILAR_CACHE)
    post_delete.disconnect(sender=Entry, dispatch_uid=ENTRY_PD_FLUSH_SIMILAR_CACHE)


def connect_discussion_signals():
    """
    Connect all signal handlers related to comment and discussion events.
    Keeps discussion counts updated and handles pingbacks/trackbacks.
    """
    post_save.connect(count_discussions_handler, sender=comment_model,
                      dispatch_uid=COMMENT_PS_COUNT_DISCUSSIONS)
    pre_delete.connect(count_discussions_handler, sender=comment_model,
                       dispatch_uid=COMMENT_PD_COUNT_DISCUSSIONS)
    comment_was_flagged.connect(count_discussions_handler, sender=comment_model,
                                dispatch_uid=COMMENT_WF_COUNT_DISCUSSIONS)
    comment_was_posted.connect(count_comments_handler, sender=comment_model,
                               dispatch_uid=COMMENT_WP_COUNT_COMMENTS)
    pingback_was_posted.connect(count_pingbacks_handler, sender=comment_model,
                                dispatch_uid=PINGBACK_WF_COUNT_PINGBACKS)
    trackback_was_posted.connect(count_trackbacks_handler, sender=comment_model,
                                 dispatch_uid=TRACKBACK_WF_COUNT_TRACKBACKS)


def disconnect_discussion_signals():
    """
    Disconnect all signal handlers related to comment and discussion events.
    """
    post_save.disconnect(sender=comment_model, dispatch_uid=COMMENT_PS_COUNT_DISCUSSIONS)
    pre_delete.disconnect(sender=comment_model, dispatch_uid=COMMENT_PD_COUNT_DISCUSSIONS)
    comment_was_flagged.disconnect(sender=comment_model, dispatch_uid=COMMENT_WF_COUNT_DISCUSSIONS)
    comment_was_posted.disconnect(sender=comment_model, dispatch_uid=COMMENT_WP_COUNT_COMMENTS)
    pingback_was_posted.disconnect(sender=comment_model, dispatch_uid=PINGBACK_WF_COUNT_PINGBACKS)
    trackback_was_posted.disconnect(sender=comment_model, dispatch_uid=TRACKBACK_WF_COUNT_TRACKBACKS)
