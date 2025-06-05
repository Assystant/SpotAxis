from __future__ import absolute_import
from __future__ import print_function
import re
from bs4 import BeautifulSoup
import os
from . import pdf2txt 

def extract_font_size_font_family(font_string):
	"""
    Extracts the font family and font size from a CSS style string.

    Args:
        font_string (str): The CSS style string containing font information.

    Returns:
        tuple: A tuple containing the font family (str) and font size (int).
    """
	
	font_family = ''
	font_size_integer = 0

	if ';' in font_string:
		font_string = font_string.split(';')
		if 'font-family' in font_string[0]:
			font_family = font_string[0].split(':')[1].strip()
		if 'font-size' in font_string[1]:
			font_size_string = font_string[1].split(':')[1].strip()
			print(font_size_string)
			font_size_integer = int((re.findall('\d+', font_size_string))[0])

	return (font_family, font_size_integer)



pdf2txt.main('Shubham_Jain.pdf', 'output.html', 'html')
#please change directory to where you are running this code
soup = BeautifulSoup(open('C:\\Python27\\output.html'))

span_tag_list = soup.find_all('span')
#print span_tag_list

max_font_size = 0

st = ''

keyword_list = ['EDUCATION', 'Education', 'OBJECTIVE', 'Objective', 'SKILLS', 'Skills', 'PROJECT', 'Project']
keyword_dict = dict()

for item in span_tag_list:

	if item.descendants is not None:
		for child in item.descendants:
			if 'NavigableString' in str(type(child)):
				if ('font-family' in item.attrs['style']) and ('font-size' in item.attrs['style']):
					font_size_list = re.findall('(\d+)',item.attrs['style'])
					max_font_size = max(int(font_size_list[0]),max_font_size)
					#print item.attrs['style'] 
					for word in keyword_list:
						if word in str(child.encode('utf-8')):
							(font_family, font_size) = extract_font_size_font_family(item.attrs['style'])
							keyword_dict[str(child.encode('utf-8'))] = [font_family, font_size]


atleast_once_occurence_flag = False


for key1 in keyword_dict:
	for key2 in keyword_dict:
		if keyword_dict[key1][0] == keyword_dict[key2][0]:
			atleast_once_occurence_flag = True
			break
	if not atleast_once_occurence_flag:
		del keyword_dict[key1]


print(max_font_size)
print(keyword_dict)
