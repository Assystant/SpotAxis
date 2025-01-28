# encoding: utf-8
from __future__ import absolute_import
import mimetypes
import re

def order_name(name):
    """order_name -- Limit a text to 30 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.
    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 30:
        return name
    return name[:20] + "..." + name[-7:]


def serialize(instance, file_attr='file'):
    """serialize -- Serialize a File instance into a dict.
    This method is used to upload a file, returns a list of what we want
     Instance - Object / instance
    file_attr -- attribute name that contains the FileField or ImageField
    """
    obj = getattr(instance, file_attr)
    return {
        'url': obj.url,
        'name': order_name(obj.name),
        'type': mimetypes.guess_type(obj.path)[0],
        'size': obj.size,
        'pk': instance.pk,
    }
