"""
This module provides functionality to parse resumes using BeautifulSoup.
"""
from __future__ import absolute_import
from __future__ import print_function
import re
from bs4 import BeautifulSoup
import os

os.system("python pdf2txt.py -o output.html -t html Vaibhav_Garg.pdf")
#please change directory to where you are running this code
soup = BeautifulSoup(open('output.html'))

span_tag_list = soup.find_all('span')
#print span_tag_list

max_font_size = 0

st = ''

keyword_list = ['EDUCATION', 'Education', 'OBJECTIVE', 'Objective', 'SKILLS', 'Skills', 'PROJECT', 'Project']
keyword_dict = dict()

for item in span_tag_list:
	"""
	Iterates through all span tags in the HTML content.

	Args:
		item (bs4.element.Tag): A BeautifulSoup span tag.
	"""

	if item.descendants is not None:
		for child in item.descendants:
			if 'NavigableString' in str(type(child)):
				if ('font-family' in item.attrs['style']) and ('font-size' in item.attrs['style']):
					font_size_list = re.findall('(\d+)',item.attrs['style'])
					max_font_size = max(int(font_size_list[0]),max_font_size)
					print((item.attrs['style'])) 
					for word in keyword_list:
						if word in str(child.encode('utf-8')):
							keyword_dict[word] = item.attrs['style']

print(max_font_size)
print(keyword_dict)
