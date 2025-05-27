
"""
Module to facilitate automatic discovery and loading of unit tests for the Django helpdesk app.

This module defines a `suite` function which uses Python's `unittest` framework to discover
and collect all test modules matching the pattern `test_*.py` within the `helpdesk.tests` package.

This approach ensures compatibility with Django versions <= 1.5, which do not have built-in
automatic test discovery.

References:
    - StackOverflow discussion: http://stackoverflow.com/a/15780326/1382740

Imports:
    - unittest: Python's built-in unit testing framework.
"""

# import all test_*.py files in directory.
# neccessary for automatic discovery in django <= 1.5
# http://stackoverflow.com/a/15780326/1382740

from __future__ import absolute_import
import unittest


def suite():
    """
    Discovers and loads all unit tests matching 'test_*.py' in the 'helpdesk.tests' package.

    Returns:
        unittest.TestSuite: A test suite comprising all discovered test cases.

    This function enables running all tests in the specified directory using unittest's
    discover mechanism, supporting older Django versions that lack automatic test detection.
    """
    return unittest.TestLoader().discover("helpdesk.tests", pattern="test_*.py")
