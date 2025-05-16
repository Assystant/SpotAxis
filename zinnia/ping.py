"""
Pings utilities for Zinnia

This module provides threaded utilities to notify external services and
directories about new or updated blog entries via:
- XML-RPC pinging of web directories (e.g., Technorati)
- Pingbacks to external URLs referenced in blog entries

It defines:
- `DirectoryPinger`: Notifies directory services about new blog entries.
- `ExternalUrlsPinger`: Notifies external websites that a blog post links to them.
"""

import socket
import threading
from logging import getLogger

# Compatibility for Python 2 and 3
try:
    from urllib.request import urlopen
    from urllib.parse import urlsplit
    from xmlrpc.client import Error, ServerProxy
except ImportError:  # Python 2 fallback
    from urllib2 import urlopen
    from urlparse import urlsplit
    from xmlrpclib import Error, ServerProxy

from bs4 import BeautifulSoup
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from zinnia.flags import PINGBACK
from zinnia.settings import PROTOCOL


class URLRessources(object):
    """
    A helper object that defines URLs related to the current blog site:
    - Full site URL
    - Blog index URL
    - Blog feed URL
    """

    def __init__(self):
        self.current_site = Site.objects.get_current()
        self.site_url = '%s://%s' % (PROTOCOL, self.current_site.domain)
        self.blog_url = '%s%s' % (self.site_url,
                                  reverse('zinnia:entry_archive_index'))
        self.blog_feed = '%s%s' % (self.site_url,
                                   reverse('zinnia:entry_feed'))


class DirectoryPinger(threading.Thread):
    """
    Threaded pinger that sends blog updates to directory services
    (e.g., Google Blog Search, Technorati, etc.)

    Args:
        server_name (str): XML-RPC URL of the directory.
        entries (list): List of Entry instances to ping.
        timeout (int): Socket timeout duration.
        start_now (bool): Whether to start pinging immediately.
    """

    def __init__(self, server_name, entries, timeout=10, start_now=True):
        self.results = []
        self.timeout = timeout
        self.entries = entries
        self.server_name = server_name
        self.server = ServerProxy(self.server_name)
        self.ressources = URLRessources()

        threading.Thread.__init__(self)
        if start_now:
            self.start()

    def run(self):
        """
        Thread entrypoint to ping each entry to the directory.
        """
        logger = getLogger('zinnia.ping.directory')
        socket.setdefaulttimeout(self.timeout)
        for entry in self.entries:
            reply = self.ping_entry(entry)
            self.results.append(reply)
            logger.info('%s : %s' % (self.server_name, reply['message']))
        socket.setdefaulttimeout(None)

    def ping_entry(self, entry):
        """
        Ping an individual entry to the directory server.

        Returns:
            dict: Server response or error message.
        """
        entry_url = '%s%s' % (self.ressources.site_url, entry.get_absolute_url())
        categories = '|'.join([c.title for c in entry.categories.all()])

        try:
            reply = self.server.weblogUpdates.extendedPing(
                self.ressources.current_site.name,
                self.ressources.blog_url, entry_url,
                self.ressources.blog_feed, categories)
        except Exception:
            try:
                reply = self.server.weblogUpdates.ping(
                    self.ressources.current_site.name,
                    self.ressources.blog_url, entry_url, categories)
            except Exception:
                reply = {
                    'message': '%s is an invalid directory.' % self.server_name,
                    'flerror': True
                }
        return reply


class ExternalUrlsPinger(threading.Thread):
    """
    Threaded pinger that sends pingbacks to external URLs linked from a blog entry.

    Args:
        entry (Entry): The Entry instance to scan for outbound links.
        timeout (int): Timeout for socket/network requests.
        start_now (bool): Whether to begin pinging immediately.
    """

    def __init__(self, entry, timeout=10, start_now=True):
        self.results = []
        self.entry = entry
        self.timeout = timeout
        self.ressources = URLRessources()
        self.entry_url = '%s%s' % (self.ressources.site_url,
                                   self.entry.get_absolute_url())

        threading.Thread.__init__(self)
        if start_now:
            self.start()

    def run(self):
        """
        Main logic: find external links, identify pingback servers, and ping them.
        """
        logger = getLogger('zinnia.ping.external_urls')
        socket.setdefaulttimeout(self.timeout)

        external_urls = self.find_external_urls(self.entry)
        external_urls_pingable = self.find_pingback_urls(external_urls)

        for url, server_name in external_urls_pingable.items():
            reply = self.pingback_url(server_name, url)
            self.results.append(reply)
            logger.info('%s : %s' % (url, reply))

        socket.setdefaulttimeout(None)

    def is_external_url(self, url, site_url):
        """
        Determine if a URL is external to the current blog site.

        Returns:
            bool: True if the link is external.
        """
        url_splitted = urlsplit(url)
        if not url_splitted.netloc:
            return False
        return url_splitted.netloc != urlsplit(site_url).netloc

    def find_external_urls(self, entry):
        """
        Parse the entry's HTML content to find all external <a href="..."> links.

        Returns:
            list: List of external URL strings.
        """
        soup = BeautifulSoup(entry.html_content, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True)
                if self.is_external_url(a['href'], self.ressources.site_url)]

    def find_pingback_href(self, content):
        """
        Parse the HTML to look for <link rel="pingback" href="...">.

        Returns:
            str or None: Pingback server URL if found.
        """
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('link'):
            attrs = dict(link.attrs)
            if 'rel' in attrs and 'href' in attrs:
                for rel_type in attrs['rel']:
                    if rel_type.lower() == PINGBACK:
                        return attrs.get('href')

    def find_pingback_urls(self, urls):
        """
        Determine pingback server URLs for each external link.

        Returns:
            dict: Mapping from target URL → pingback server URL.
        """
        pingback_urls = {}

        for url in urls:
            try:
                page = urlopen(url)
                headers = page.info()
                server_url = headers.get('X-Pingback')

                # If X-Pingback header is missing, check HTML content
                if not server_url:
                    content_type = headers.get('Content-Type', '').split(';')[0].strip().lower()
                    if content_type in ['text/html', 'application/xhtml+xml']:
                        server_url = self.find_pingback_href(page.read(5 * 1024))

                # Normalize relative server URLs
                if server_url:
                    server_url_splitted = urlsplit(server_url)
                    if not server_url_splitted.netloc:
                        url_splitted = urlsplit(url)
                        server_url = '%s://%s%s' % (
                            url_splitted.scheme,
                            url_splitted.netloc,
                            server_url
                        )
                    pingback_urls[url] = server_url
            except IOError:
                pass

        return pingback_urls

    def pingback_url(self, server_name, target_url):
        """
        Call the pingback XML-RPC method to notify a target URL.

        Returns:
            str: Reply message or failure note.
        """
        try:
            server = ServerProxy(server_name)
            return server.pingback.ping(self.entry_url, target_url)
        except (Error, socket.error):
            return '%s cannot be pinged.' % target_url
