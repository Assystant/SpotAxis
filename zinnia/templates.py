"""
Templates module for Zinnia

This module provides utility functions to assist with dynamically selecting
and naming templates based on loop position, instance type, and template
registration dictionaries. These utilities help Zinnia determine which
template to render in different loop or object contexts.

Main Features:
- Dynamically generate template names based on position and type
- Support fallback templates using default structures
"""

import os
from django.template.defaultfilters import slugify


def append_position(path, position, separator=''):
    """
    Append a position value to the filename part of a path before its extension.

    Args:
        path (str): Full path to a template or file (e.g., "entry.html")
        position (int): Numeric position to inject (e.g., loop index)
        separator (str, optional): Character used to separate filename and position.
                                   Defaults to '' (no separator).

    Returns:
        str: Modified path with the position appended before the extension.

    Example:
        >>> append_position("entry.html", 1, "-")
        'entry-1.html'
    """
    filename, extension = os.path.splitext(path)
    return ''.join([filename, separator, str(position), extension])


def loop_template_list(loop_positions, instance, instance_type,
                       default_template, registery={}):
    """
    Generate a prioritized list of template names based on loop positions,
    instance identity, and type.

    This is useful for customizing templates per object in loops,
    allowing fallbacks and default rendering.

    Args:
        loop_positions (tuple): A pair of (global_position, local_position)
                                where:
                                - global_position: index in full queryset loop
                                - local_position: index within the current subloop
        instance (object): The current model instance (e.g., Entry, Author)
        instance_type (str): A string identifier for the instance type
                             (e.g., "entry", "author")
        default_template (str): Path to the fallback default template
                                (e.g., "zinnia/entry_detail.html")
        registery (dict): A dictionary mapping instance identifiers to lists of
                          pre-configured template paths by position

                          Example:
                          {
                            'entry-hello-world': ['custom1.html', 'custom2.html'],
                            'entry': ['generic1.html'],
                            'default': ['fallback1.html']
                          }

    Returns:
        list: A list of possible templates, ordered by priority.

    Priority Order:
        1. From registery using:
           - specific instance key (e.g., "entry-hello-world")
           - just instance slug (e.g., "hello-world")
           - type fallback (e.g., "entry")
           - global "default"
        2. default_template with global_position injected (with '-')
        3. default_template with local_position injected (with '_')
        4. The original default_template

    Example:
        >>> loop_template_list((1, 0), Entry(title="Hello World"), "entry", "entry.html", registry)
        ['entry-hello-world.html', 'hello-world.html', 'entry.html',
         'entry-1.html', 'entry_0.html', 'entry.html']
    """
    templates = []
    global_loop_position = loop_positions[0]
    local_loop_position = loop_positions[1]
    instance_string = slugify(str(instance))

    for key in [
        f'{instance_type}-{instance_string}',  # e.g. entry-hello-world
        instance_string,                       # e.g. hello-world
        instance_type,                         # e.g. entry
        'default'                              # fallback
    ]:
        try:
            templates.append(registery[key][global_loop_position])
        except KeyError:
            pass

    # Fallbacks using position in filename
    templates.append(
        append_position(default_template, global_loop_position, '-')
    )
    templates.append(
        append_position(default_template, local_loop_position, '_')
    )
    templates.append(default_template)

    return templates
