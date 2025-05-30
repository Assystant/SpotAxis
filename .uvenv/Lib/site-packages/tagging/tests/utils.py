"""
Tests utils for tagging.
"""
from django.template import Origin
from django.template.loaders.base import Loader


class VoidLoader(Loader):
    """
    Template loader which is always returning
    an empty template.
    """
    is_usable = True
    _accepts_engine_in_init = True

    def get_template_sources(self, template_name):
        yield Origin(
            name='voidloader',
            template_name=template_name,
            loader=self)

    def get_contents(self, origin):
        return ''

    def load_template_source(self, template_name, template_dirs=None):
        return ('', 'voidloader:%s' % template_name)
