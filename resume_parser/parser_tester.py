"""
This script serves as a test driver for verifying the functionality of
the resume parser module.
"""
from __future__ import absolute_import
from __future__ import print_function
import data_extraction as de


print((de.extract_file_content(r'C:\Python27\data_extraction\Vaibhav_Garg.pdf', 'json')))
