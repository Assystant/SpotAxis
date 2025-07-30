"""
This script serves as a test driver for verifying the functionality of
the resume parser module.
"""
from __future__ import absolute_import
from __future__ import print_function
import combined_parser as pr


print((pr.extract_file_content(r'test_resume.pdf', 'json')))
print((pr.extract_file_content(r'test1.pdf', 'json')))
print((pr.extract_file_content(r'test2.pdf', 'json')))
print((pr.extract_file_content(r'deedy-resume-reversed.pdf', 'json')))