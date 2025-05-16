"""
Entry model for Zinnia.

This module defines the final concrete Entry model used by the application.
The Entry model represents a blog post and is dynamically loaded from a base
class defined in settings.

This dynamic loading allows the project to define custom base models for blog
entries, supporting flexibility and extensibility.
"""

from zinnia.models_bases import load_model_class
from zinnia.settings import ENTRY_BASE_MODEL


class Entry(load_model_class(ENTRY_BASE_MODEL)):
    """
    The final Entry model representing a blog post.

    Inherits from a dynamically loaded base model specified in the
    ENTRY_BASE_MODEL setting. This allows customization of the blog post
    structure by changing the base class without modifying this file.

    Typically, the base model is 'zinnia.models_bases.entry.AbstractEntry'.
    """
    pass  # All fields and behaviors are inherited from the base class
