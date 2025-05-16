"""
Moderator of Zinnia comments

This module defines the `EntryCommentModerator`, a custom subclass
of `django_comments.moderation.CommentModerator`, that handles
moderation and email notification logic for comments posted on
Zinnia blog entries.

Features include:
- Auto-closing comments after a certain time
- Email notifications to staff, authors, and previous commenters
- Optional automatic moderation and spam checking
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, send_mail
from django.template import loader
from django.utils.translation import activate, get_language
from django.utils.translation import ugettext_lazy as _

from django_comments.moderation import CommentModerator

from zinnia.settings import (
    AUTO_CLOSE_COMMENTS_AFTER,
    AUTO_MODERATE_COMMENTS,
    MAIL_COMMENT_AUTHORS,
    MAIL_COMMENT_NOTIFICATION_RECIPIENTS,
    MAIL_COMMENT_REPLY,
    PROTOCOL,
    SPAM_CHECKER_BACKENDS,
)
from zinnia.spam_checker import check_is_spam


class EntryCommentModerator(CommentModerator):
    """
    Custom comment moderator for Zinnia blog entries.

    Controls comment behavior including:
    - Email notifications to admins/authors/previous commenters
    - Automatic closing of comments after a time period
    - Automatic moderation based on spam checker backends
    """

    # Settings and behavior flags from zinnia.settings
    email_reply = MAIL_COMMENT_REPLY
    email_authors = MAIL_COMMENT_AUTHORS
    enable_field = 'comment_enabled'
    auto_close_field = 'start_publication'
    close_after = AUTO_CLOSE_COMMENTS_AFTER
    spam_checker_backends = SPAM_CHECKER_BACKENDS
    auto_moderate_comments = AUTO_MODERATE_COMMENTS
    mail_comment_notification_recipients = MAIL_COMMENT_NOTIFICATION_RECIPIENTS

    def email(self, comment, content_object, request):
        """
        Send email notifications when a comment is posted.

        Emails are sent to:
        - Site staff (optional)
        - Entry authors (optional)
        - Other commenters (optional)

        Language is temporarily switched to `settings.LANGUAGE_CODE` 
        for consistent email rendering.
        """
        if comment.is_public:
            current_language = get_language()
            try:
                activate(settings.LANGUAGE_CODE)
                if self.mail_comment_notification_recipients:
                    self.do_email_notification(comment, content_object, request)
                if self.email_authors:
                    self.do_email_authors(comment, content_object, request)
                if self.email_reply:
                    self.do_email_reply(comment, content_object, request)
            finally:
                activate(current_language)

    def do_email_notification(self, comment, content_object, request):
        """
        Notify site staff (or any predefined email list) of a new comment.
        """
        site = Site.objects.get_current()
        template = loader.get_template('comments/comment_notification_email.txt')
        context = {
            'comment': comment,
            'site': site,
            'protocol': PROTOCOL,
            'content_object': content_object
        }
        subject = _('[%(site)s] New comment posted on "%(title)s"') % {
            'site': site.name,
            'title': content_object.title
        }
        message = template.render(context)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            self.mail_comment_notification_recipients,
            fail_silently=not settings.DEBUG
        )

    def do_email_authors(self, comment, content_object, request):
        """
        Notify the authors of the entry about a new comment.

        Authors who are already in the notification list are excluded.
        """
        exclude_list = self.mail_comment_notification_recipients + ['']
        recipient_list = set(
            [author.email for author in content_object.authors.all()]
        ) - set(exclude_list)

        if recipient_list:
            site = Site.objects.get_current()
            template = loader.get_template('comments/comment_authors_email.txt')
            context = {
                'comment': comment,
                'site': site,
                'protocol': PROTOCOL,
                'content_object': content_object
            }
            subject = _('[%(site)s] New comment posted on "%(title)s"') % {
                'site': site.name,
                'title': content_object.title
            }
            message = template.render(context)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=not settings.DEBUG
            )

    def do_email_reply(self, comment, content_object, request):
        """
        Notify previous commenters about a new comment.

        Excludes the current commenter, entry authors, and admin recipients.
        """
        exclude_list = self.mail_comment_notification_recipients + \
                       [author.email for author in content_object.authors.all()] + \
                       [comment.email]
        recipient_list = set(
            [other_comment.email for other_comment in content_object.comments
             if other_comment.email]
        ) - set(exclude_list)

        if recipient_list:
            site = Site.objects.get_current()
            template = loader.get_template('comments/comment_reply_email.txt')
            context = {
                'comment': comment,
                'site': site,
                'protocol': PROTOCOL,
                'content_object': content_object
            }
            subject = _('[%(site)s] New comment posted on "%(title)s"') % {
                'site': site.name,
                'title': content_object.title
            }
            message = template.render(context)
            mail = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                bcc=recipient_list
            )
            mail.send(fail_silently=not settings.DEBUG)

    def moderate(self, comment, content_object, request):
        """
        Decide whether to moderate (i.e., hold) the comment for approval.

        Moderation is triggered if:
        - AUTO_MODERATE_COMMENTS is True
        - OR the comment is detected as spam by the configured backends

        Returns:
            bool: True to moderate (hold) the comment, False to publish.
        """
        if self.auto_moderate_comments:
            return True

        if check_is_spam(comment, content_object, request, self.spam_checker_backends):
            return True

        return False
