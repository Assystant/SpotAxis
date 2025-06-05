# encoding: utf-8

from __future__ import absolute_import
from django.http import HttpResponse
import json

MIMEANY = '*/*'
MIMEJSON = 'application/json'
MIMETEXT = 'text/plain'


def response_mimetype(request):
    """
    response_mimetype -- Return a proper response mimetype, accordingly to
    what the client accepts, as available in the `HTTP_ACCEPT` header.

    request -- a HttpRequest instance.

    """
    can_json = MIMEJSON in request.META['HTTP_ACCEPT']
    can_json |= MIMEANY in request.META['HTTP_ACCEPT']
    return MIMEJSON if can_json else MIMETEXT


class JSONResponse(HttpResponse):
    """JSONResponse -- Extends HTTPResponse to handle JSON format response.

    This response can be used in any view that should return a json stream of
    data.

    Usage:

        def a_iew(request):
            content = {'key': 'value'}
            return JSONResponse(content, mimetype=response_mimetype(request))

    """
    def __init__(self, obj='', json_opts=None, mimetype=MIMEJSON, *args, **kwargs):
        """
        Initialize a JSONResponse instance by serializing an object to JSON.

        Args:
            obj (any): The Python object to be serialized to JSON. Defaults to an empty string.
            json_opts (dict, optional): Optional keyword arguments passed to json.dumps for serialization options.
            mimetype (str): The MIME type for the response content. Defaults to MIMEJSON.
            *args: Additional positional arguments passed to the superclass initializer.
            **kwargs: Additional keyword arguments passed to the superclass initializer.
        """
        json_opts = json_opts if isinstance(json_opts, dict) else {}
        content = json.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
