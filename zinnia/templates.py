"""Templates module for Zinnia"""
from __future__ import absolute_import
import os

from django.template.defaultfilters import slugify


def append_position(path, position, separator=''):
    """
    Concatenate a path and a position,
    between the filename and the extension.
    """
    filename, extension = os.path.splitext(path)
    return ''.join([filename, separator, str(position), extension])


def loop_template_list(loop_positions, instance, instance_type,
                       default_template, registery={}):
    """
    Build a list of templates from a position within a loop
    and a registery of templates.
    """
    templates = []
    local_loop_position = loop_positions[1]
    global_loop_position = loop_positions[0]
    instance_string = slugify(str(instance))

    for key in ['%s-%s' % (instance_type, instance_string),
                instance_string,
                instance_type,
                'default']:
        try:
            templates.append(registery[key][global_loop_position])
        except KeyError:
            pass

    templates.append(
        append_position(default_template, global_loop_position, '-'))
    templates.append(
        append_position(default_template, local_loop_position, '_'))
    templates.append(default_template)

    return templates
