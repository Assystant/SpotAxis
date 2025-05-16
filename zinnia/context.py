"""Context module for Zinnia

Provides utility functions for safely accessing objects and positional data
from the Django template context — particularly useful in Zinnia templates
that involve paginated lists or multiple context variable names.
"""


def get_context_first_matching_object(context, context_lookups):
    """
    Return the first key-object pair found in the context from a list of possible keys.

    This is useful when templates pass in different keys depending on view logic,
    and you want to find the first one that exists.

    Args:
        context (dict): Django template context.
        context_lookups (list of str): List of keys to look for in order.

    Returns:
        tuple: (key, object) where key is the matched key, and object is the value.
               Returns (None, None) if no key matches.
    """
    for key in context_lookups:
        context_object = context.get(key)
        if context_object:
            return key, context_object
    return None, None


def get_context_first_object(context, context_lookups):
    """
    Return the first object found in the context from a list of keys.

    This is a simplified version of `get_context_first_matching_object`
    that returns only the object, not the key.

    Args:
        context (dict): Django template context.
        context_lookups (list of str): List of possible keys.

    Returns:
        object or None: The first object found, or None if not found.
    """
    return get_context_first_matching_object(context, context_lookups)[1]


def get_context_loop_positions(context):
    """
    Return the loop position in paginated and unpaginated formats.

    Used for templates with pagination to calculate both:
    - global position in the full list (total_loop_counter)
    - current position within the current page (loop_counter)

    Args:
        context (dict): Django template context with 'forloop' and 'page_obj'.

    Returns:
        tuple: (total_loop_counter, loop_counter)
    """
    try:
        loop_counter = context['forloop']['counter']
    except KeyError:
        return 0, 0
    try:
        page = context['page_obj']
    except KeyError:
        return loop_counter, loop_counter
    total_loop_counter = ((page.number - 1) * page.paginator.per_page +
                          loop_counter)
    return total_loop_counter, loop_counter
