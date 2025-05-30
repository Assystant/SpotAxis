# -*- coding: utf-8 -*-
"""
    autodoc.compat
    ~~~~~~~~~~~~~~

    Compatible to Python2.7 and Python3.x

    This module is copyed from Werkzeug's `_compat.py`.

    https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/_compat.py

    :copyright: (c) 2014-2018 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import sys

PY2 = sys.version_info[0] == 2


if PY2:
    from urlparse import parse_qsl as parse_qsl  # noqa F401
    from urllib import urlencode as urlencode  # noqa F401
    text_type = unicode  # noqa F821

    iterkeys = lambda d: d.iterkeys()  # noqa E731
    itervalues = lambda d: d.itervalues()  # noqa E731
    iteritems = lambda d: d.iteritems()  # noqa E731
else:
    from urllib.parse import parse_qsl as parse_qsl  # noqa F401
    from urllib.parse import urlencode as urlencode  # noqa F401
    text_type = str

    iterkeys = lambda d: iter(d.keys())  # noqa E731
    itervalues = lambda d: iter(d.values())  # noqa E731
    iteritems = lambda d: iter(d.items())  # noqa E731


def to_unicode(x, charset=sys.getdefaultencoding(), errors='strict',
               allow_none_charset=False):
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    if charset is None and allow_none_charset:
        return x
    return x.decode(charset, errors)
