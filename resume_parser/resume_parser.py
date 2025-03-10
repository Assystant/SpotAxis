from __future__ import absolute_import
from __future__ import print_function
import datefinder
import docx
import json
import pdb
import pdfminer
import os
import re
import subprocess
import sys
from bs4 import BeautifulSoup
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader
from xml.dom.minidom import parseString

from unidecode import unidecode
def remove_non_ascii(text):
    return unidecode(str(text, encoding = "utf-8"))
'''
global variable declarations
'''
omit_list = ['High School','Senior Secondary School', 'Secondary School', 'Higher Secondary School', 'School']
school_college_keyword_list = ['COLLEGE','College','INSTITUTE','Institute','SCHOOL','School','School,', 'SCHOOL,', 'School)','(School' ,'UNIVERSITY','University']

# date_finder_regex = '(Jan|January|JANUARY|JAN|Feb|February|FEB|FEBRUARY|Mar|March|MARCH|MAR|Apr|April|APR|APRIL|May|MAY|Jun|June|JUN|JUNE|Jul|July|JUL|JULY|Aug|August|AUG|AUGUST|Sept|September|SEPTEMBER|SEPT|Oct|October|OCT|OCTOBER|Nov|November|NOV|NOVEMBER|Dec|December|DEC|DECEMBER)? *(?:19[7-9]\d|2\d{3}) *-? *(Jan|January|JANUARY|JAN|Feb|February|FEB|FEBRUARY|Mar|March|MARCH|MAR|Apr|April|APR|APRIL|May|MAY|Jun|June|JUN|JUNE|Jul|July|JUL|JULY|Aug|August|AUG|AUGUST|Sept|September|SEPTEMBER|SEPT|Oct|October|OCT|OCTOBER|Nov|November|NOV|NOVEMBER|Dec|December|DEC|DECEMBER)? *(?:19[7-9]\d|2\d{3}) *'
# date_finder_regex = '(Jan|January|JANUARY|JAN|Feb|February|FEB|FEBRUARY|Mar|March|MARCH|MAR|Apr|April|APR|APRIL|May|MAY|Jun|June|JUN|JUNE|Jul|July|JUL|JULY|Aug|August|AUG|AUGUST|Sept|September|SEPTEMBER|SEPT|Oct|October|OCT|OCTOBER|Nov|November|NOV|NOVEMBER|Dec|December|DEC|DECEMBER)? *[,\' ]? *(?:19[7-9]\d|2\d{3}|[0-9]{2}) *-? *(Jan|January|JANUARY|JAN|Feb|February|FEB|FEBRUARY|Mar|March|MARCH|MAR|Apr|April|APR|APRIL|May|MAY|Jun|June|JUN|JUNE|Jul|July|JUL|JULY|Aug|August|AUG|AUGUST|Sept|September|SEPTEMBER|SEPT|Oct|October|OCT|OCTOBER|Nov|November|NOV|NOVEMBER|Dec|December|DEC|DECEMBER)? *[,\' ]? *(?:19[7-9]\d|2\d{3}|[0-9]{2})'
# date_finder_regex = '(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)? *([\'|\-|,|\`]+ *(\d{2}))|([\'|\-|,|\`| ]*(19[5-9]{2}|20\d{2})){1}'
date_finder_regex = "(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) *(?:(?:[\',\` ]*(?:(?:19[5-9][0-9]|20[0-9]{2}))|(?:[\',\`]* *(?:[5-9][0-9]|[0-2][0-9])))|present|ongoing|till date|active)|[\'\`]*(?:19[5-9][0-9]|20[0-9]{2})|present|ongoing|till date|active"
re_for_alpha = '[a-zA-Z\.]' 
regex_expression_date = '(?:19[7-9]\d|2\d{3}) *-? *((?:19[7-9]\d|2\d{3})|Present|current|Current|present|ongoing|Ongoing)?'
regex_expression_school_college = 'COLLEGE|College|INSTITUTE|Institute|SCHOOL|School|UNIVERSITY|University'


# education_dict = dict()
# work_experience_dict = dict()

date_list = list()
# email_list = list()
# name_user_list = list()
# phone_list = list()
# skill_list = list()

# skill_set = set()


module_dir = os.path.dirname(__file__)  # get current directory

file_path = os.path.join(module_dir, 'courses_corpus.txt')
course_corpus_list = open(file_path).readlines()

file_path = os.path.join(module_dir, 'indian_female_list.txt')
female_list = open(file_path).readlines()

file_path = os.path.join(module_dir, 'indian_male_list.txt')
male_list = open(file_path).readlines()

file_path = os.path.join(module_dir, 'skill_data_json.json')
with open(file_path) as data:
    json_data = json.load(data)

def pdf_to_text(filename):
    '''
    converts the pdf to text and returns the result
    to extract_file_content() method
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(filename, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()

    return text

def pdf_to_text_for_direct_upload(fp):
    '''
    converts the pdf to text and returns the result
    to extract_file_content() method
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()

    return text

def get_dates(file_content):
    '''
    extracts dates from file-content
    '''
    local_date_list = list()
    output_dates = datefinder.find_dates(file_content)
    for date in output_dates:
        local_date_list.append(date) 
    return local_date_list

def get_education(file_content):
    '''
    extacts the education
    or academic details
    of the resume-holder
    '''
    college_school_list = list()
    education_string = ''
    education_found_flag = False

    education_details_dict = dict()

    education_date_list = list()
    education_course_list = list()
    
    try:
        for line in file_content.split('\n'):
            
            if ('EDUCATION' in line) or ('Education' in line) or ('ACADEMIC' in line) or ('Academic' in line) :
                education_found_flag = True
                education_string += line.strip()
                continue
            if education_found_flag:
                if 'SKILL' in line or 'Skill' in line or 'PROJECT' in line or 'Project' in line \
                    or 'WORK' in line or 'Work' in line or 'EXPERIENCE' in line or 'Experience' in line \
                    or 'PROFILE' in line or 'Profile' in line or 'INTEREST' in line or 'Interest' in line \
                    or 'HOBBIES' in line or 'Hobbies' in line or 'HOBBY' in line or 'Hobby' in line \
                    or 'ACTIVITIES' in line or 'Activities' in line or 'ACTIVITY' in line or 'Activity' in line:
                    break
                if line.strip():
                    education_string += '\n' + line.strip()
        education_list = education_string.split('\n')
        for item in education_list:
            if bool(re.search(regex_expression_date, item)):
                education_date_list.append(re.search(regex_expression_date, item).group())
                
            if bool(re.search(regex_expression_school_college, item)):
                item_copy = item
                school_college_name = ''
                item_copy = item_copy.split()

                for index, element in enumerate(item_copy):
                    if ',' in item_copy[index]:     
                        element = element.split(',',1)[0]
                        if element.strip():       
                            item_copy[index] = element.strip()
                    
                for index, element in enumerate(item_copy):
                    
                    while (item_copy[index] not in school_college_keyword_list) and index < len(item_copy)-1:
                        
                        index += 1 
                    
                    school_college_name = item_copy[index]
                    
                    index_copy_backward = index - 1
                    index_copy_forward = index + 1
                    
                    if (index_copy_backward >= 0):
                        
                        while (item_copy[index_copy_backward][0].isupper() or item_copy[index_copy_backward] == 'of') and (index_copy_backward >= 0):

                            school_college_name = item_copy[index_copy_backward] + ' ' + school_college_name
                            index_copy_backward -= 1
                    
                    
                    if (index_copy_forward < len(item_copy)):

                        while (index_copy_forward < len(item_copy)) and (item_copy[index_copy_forward][0].isupper() or item_copy[index_copy_forward] == 'of') and bool(re.search(re_for_alpha, item_copy[index_copy_forward][0])):
                            
                            school_college_name = school_college_name + ' ' + item_copy[index_copy_forward]
                            index_copy_forward += 1
                    
                    college_school_list.append(school_college_name)
                    break
            
            for course in course_corpus_list:
                if course.strip() in item:
                    education_course_list.append(course)
                    break
        for item in college_school_list:
            for omit_item in omit_list:
                if omit_item in item:
                    item_copy = item
                    item_copy = item_copy.replace(omit_item, '')
                    if not bool(re.search('[a-zA-Z]',item_copy)):
                        college_school_list.remove(item)
    except:
        pass
    education_details_dict['education-dates'] = [li.strip() for li in education_date_list]
    education_details_dict['school-college'] = [li.strip() for li in college_school_list]
    education_details_dict['education-degrees'] = [li.strip() for li in education_course_list]

    return education_details_dict

def get_email(file_content):

    '''
    extract e-mails from the file-content 
    '''
    match = list()
    temp_match = list()
    # return the first regex email match
    for line in file_content.split('\n'):
        temp_match = (re.findall(r'[\w\.-]+@[\w\.-]+', str(line)))
        if temp_match:
            match = match + temp_match
    return match

def get_name(file_content):
    '''
    extracts name from file-content
    '''
    name_user_set = set()
    iter_count = 0
    local_name_block_string = ''
    name_user = ''
    local_list_name_block = list()

    # If skill, objective or experience, top section is over, no need to look for name below
    for line in file_content.split('\n'):
        if 'SKILL' in line or 'Skill' in line or 'OBJECTIVE' in line or 'Objective' in line or 'EXPERIENCE' in line or 'Experience' in line:
            break
        if line.strip():
            local_name_block_string += line.strip() + '\n'
    # Remove all empty sections and return upper block
    local_list_name_block = [_f for _f in local_name_block_string.split('\n') if _f]
    # while (iter_count <3) and (name_user == ''):
    for item in local_list_name_block:
        if ('NAME' in item) or ('Name' in item):
            name_user = item.replace('Name','')
            name_user = name_user.replace('NAME','')
            name_user = re.sub('[a-zA-Z \.]','',name_user)
            name_user_set.update([name_user])
        # remove lines with numbers
        if bool(re.search(r'\d',item)):
            local_list_name_block.remove(item)
            continue    
        item_copy = item
        for member in item_copy.split():
            for male_name in male_list:
                
                male_name = male_name.split(' ')
                
                if len(male_name) == 1:
                    if member.lower() == male_name[0]:
                        # f.write(str(male_name))
                        name_user_set.update([item])
                        name_user = item
                        break
                if len(male_name) == 2:
                    if member.lower() == male_name[0] or member.lower() == male_name[1]:
                        # f.write(str(male_name))
                        name_user_set.update([item])
                        name_user = item
                        break
                if len(male_name) == 3:
                    if member.lower() == male_name[0] or member.lower() == male_name[1] or member.lower() == male_name[2]:
                        # f.write(str(male_name))
                        name_user_set.update([item])
                        name_user = item
                        break
            if name_user == '':
                for female_name in female_list:

                    female_name = female_name.split()
                    if len(female_name) == 1:
                        if member.lower() == female_name[0]:
                            name_user_set.update([item])
                            name_user = item
                            break
                    if len(female_name) == 2:
                        if member.lower() == female_name[0] or member.lower() == female_name[1]:
                            name_user_set.update([item])
                            name_user = item
                            break
                    if len(male_name) == 3:
                        if member.lower() == female_name[0] or member.lower() == female_name[1] or member.lower() == female_name[2]:
                            name_user_set.update([item])
                            name_user = item
                            break
        # iter_count += 1
    # f.write(str(name_user_set) + '\n')

    return name_user_set

def get_phone_number(file_content):
    '''
    extracts phone-number from file-content
    '''
    local_phone_list = list()
    for line in file_content.split('\n'):
        # find mobile
        for i in re.findall(r'\+[-()\s\d]+?(?=\s*[a-zA-Z])|[-()\s\d]+?(?=\s*[a-zA-Z]|$)', line.rstrip()):
            if len(i.strip()) >= 10 and not bool(re.findall(r'\d{4} *- *\d{4}',i.strip())):
                local_phone_list.append(i.strip())    
    return local_phone_list

def get_skills(file_content):    
    '''
    extracts skills from file-content
    '''
    local_skill_flag = ''
    local_skill_string = ''
    skill_set = set()
    for line in file_content.split('\n'):
        if ('SKILL' in line) or ('Skill' in line) or ('EXPERTISE' in line) or ('Expertise' in line):
            local_skill_flag = True
        elif local_skill_flag == True:
            if 'INTEREST' in line or 'PROJECT' in line or 'ACCOMPLISHMENT' in line or 'Interest' in line or 'Project' in line or 'Accomplishment' in line:
                break
        if local_skill_flag == True:
            local_skill_string += line
    local_skill_string = local_skill_string.replace(',',' ')
    for word in local_skill_string.split():
        found_in_key_flag = False
        for key in json_data:
            if word.lower().replace(' ','') == key.encode('ascii','ignore'):
                skill_set.update([key])
                found_in_key_flag = True
        if not found_in_key_flag:
            for key in json_data:
                value_list = json_data[key]
                for value in value_list:
                    if (word.lower() == value.encode('ascii','ignore')):
                        skill_set.update([value, key])
    return skill_set

def get_ratio(sentence):
    '''
    returns the ratio 
    between number of words
    beginning  with capital
    letter to total words in sentence
    '''
    # print sentence
    caps_word_count = 0
    for word in sentence.split():
        if word[0].isupper():
            caps_word_count += 1
    if len(sentence.split()):
        return float(caps_word_count)/len(sentence.split())
    else:
        return 0

def get_work_experience(file_content):

    '''
    extracts out the work experience
    of the resume holder
    '''
    above_line_ratio = 0.0
    below_line_ratio = 0.0
    same_line_ratio = 0.0
    work_string = ''
    work_experience_found_flag = False
    not_above_line_ratio_flag = False
    work_list = list()
    work_dict = dict()
    for line in file_content.split('\n'):
        if ('WORK' in line) or ('Work' in line) or ('EXPERIENCE' in line) or ('Experience' in line):
            work_experience_found_flag = True
        if work_experience_found_flag:
            if 'SKILL' in line or 'Skill' in line or 'PROJECT' in line or 'Project' in line \
            or 'EDUCATION' in line or 'Education' in line or 'PROFILE' in line or 'Profile' in line \
            or 'INTEREST' in line or 'Interest' in line or 'HOBBIES' in line or 'Hobbies' in line \
            or 'ACTIVITIES' in line or 'Activities' in line or 'ACTIVITY' in line or 'Activity' in line:
                break

            line = line.strip(' \n')
            if line:
                work_string += line + '\n'
    work_list = work_string.strip('\n').split('\n')
    try:
        for index, word in enumerate(work_list):
            
            if ('Work Experience' in word) or ('WORK EXPERIENCE' in word):
                continue
            if ('WORK' in word) or ('Work' in word):
                continue
            if ('EXPERIENCE' in word) or ('Experience' in word):
                continue
            if (not word.strip()):
                continue
            word = remove_non_ascii(word)
            try:
                find_date = re.findall(date_finder_regex,word, re.IGNORECASE)
            except:
                find_date = 'not found'
            if find_date == 'not found' or not find_date or not len(find_date) == 2:
                continue
            else:
                print(word)
                print(find_date)
                find_date = ' - '.join([fd.strip() for fd in find_date])
                work_dict[find_date] = ''
                
                if work_list[index] > 0:
                    index_copy = index - 1
                    while work_list[index_copy] == ''  and index_copy > 0:
                        index_copy -= 1
                    above_line_ratio = get_ratio(work_list[index_copy])
                    
                
                # if work_list[index] < (len(work_list) - 1):
                if index < (len(work_list) - 1):
                    index_copy = index + 1
                    while work_list[index_copy] == '' and index_copy < len(work_list):
                        index_copy += 1
                    below_line_ratio = get_ratio(work_list[index_copy])
                    
                word_copy = word
                word_copy = re.sub(find_date,'',word_copy)
                
                if bool(re.search('[a-zA-Z]',word_copy)):
                    same_line_ratio = get_ratio(word_copy)
                
                if (('WORK' in work_list[index_copy]) or ('Work' in work_list[index_copy]) or ('EXPERIENCE' in work_list[index_copy]) or ('Experience' in work_list[index_copy]) or ('WORK EXPERIENCE' in work_list[index_copy]) or ('Word Experience' in work_list[index_copy])):
                    not_above_line_ratio_flag = True

                if not_above_line_ratio_flag:

                    if max(below_line_ratio, same_line_ratio) == below_line_ratio:
                        work_dict[find_date] = work_list[index_copy]
                    if max(below_line_ratio, same_line_ratio) == same_line_ratio:
                        work_dict[find_date] = word_copy
                
                else:    
                    if max(above_line_ratio, below_line_ratio, same_line_ratio) == above_line_ratio:
                        work_dict[find_date] = work_list[index_copy]

                    if max(above_line_ratio, below_line_ratio, same_line_ratio) == below_line_ratio:
                        work_dict[find_date] = work_list[index_copy]
                    if max(above_line_ratio, below_line_ratio, same_line_ratio) == same_line_ratio:
                        work_dict[find_date] = word_copy
        for key in work_dict:
            work_dict[key] = re.sub(r'[^\x00-\x7F]+','', work_dict[key])
            work_dict[key] = [key,work_dict[key]]
    except:
        pass
    return work_dict
         
def output_in_json(date_list, email_list, name_list, phone_list, skill_list, education_dict, work_experience_dict):
    '''
    prints the result in json format
    '''
    result_json_dict = {}
    
    result_json_dict['emails'] = email_list
    result_json_dict['name'] = name_list
    result_json_dict['phones'] = phone_list
    result_json_dict['skills'] = skill_list
    result_json_dict['experience'] = work_experience_dict
    result_json_dict['education'] = education_dict
    return result_json_dict
    # print json.dumps(result_json_dict, indent = 3)

def output_in_xml(date_list, email_list, phone_list, education_dict, work_experience_dict):
    '''
    prints the result in xml format
    '''
    result_xml_dict= {}

    result_xml_dict['emails'] = email_list
    result_xml_dict['name'] = name_list
    result_xml_dict['phones'] = phone_list
    result_xml_dict['skills'] = skill_list
    result_xml_dict['experience'] = work_experience_dict
    result_xml = dicttoxml.dicttoxml(result_xml_dict, root = False)
    result_xml_indented = parseString(result_xml)
    # print result_xml_indented.toprettyxml()

def extract_file_content(filename,  output_type):
    '''
    extracts the file content and 
    passes the file content to
    get_email(), get_phone_number(), get_dates() methods
    '''
    file_content = ''
    filename, file_extension = os.path.splitext(filename)
    try:
        if file_extension == '.txt':
            file1 = open(filename,'r')
            file_content = file2.read()

        elif file_extension == '.docx':
            document = docx.Document(filename + '.docx')
            for paragraph in document.paragraphs:
                file_content += paragraph.text.encode('utf-8')
        
        elif file_extension == '.pdf':
            file_content = pdf_to_text(filename + '.pdf')

        elif file_extension == '.rtf':
            doc = Rtf15Reader.read(open(filename + '.rtf'))
            file_content = PlaintextWriter.write(doc).getvalue()

        elif file_extension == '.doc':
            content,errors = subprocess.Popen(
                                [
                                    "antiword", 
                                    filename + '.doc',
                                    "-f",
                                    "-i", 
                                    "1"
                                ],
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                stdin = subprocess.PIPE
                            ).communicate()
            file_content = content

        elif file_extension == '.html':
            soup = BeautifulSoup(html)
            file_content = soup.get_text()
    except:
        file_content = ""
    # print file_content
    # f = open("filecontent.txt","w+")
    # f.write(file_content)
    # f.close()
    name_list = list()
    email_list = list()
    phone_list = list()
    skill_list = list()
    work_experience_dict = list()
    education_dict= list()
    if file_content:
        try:
            name_list = list(get_name(file_content))
        except:
            name_list = list()
        try:
            email_list = list(get_email(file_content))
        except:
            email_list = list()
        try:
            phone_list = get_phone_number(file_content)
        except:
            phone_list = list()
        try:
            skill_list = list(get_skills(file_content))
        except:
            skill_list = list()
        
    work_experience_dict = get_work_experience(file_content)
    education_dict = get_education(file_content)
    
    if output_type == 'json':
        return output_in_json(date_list, email_list, name_list, phone_list, skill_list, education_dict, work_experience_dict)

    else:
        return output_in_xml(date_list, email_list, name_list, phone_list, skill_list, education_dict, work_experience_dict)

def read_file_content_directly(file_object, output_type = 'json'):
    
    file_content = ''
    filename = str(file_object)
    filename, file_extension = os.path.splitext(filename)

    if file_extension == '.txt':
        file_content = file_object.read()

    elif file_extension == '.docx':
        
        for paragraph in file_object.paragraphs:
            file_content += paragraph.text.encode('utf-8')
    
    elif file_extension == '.pdf':
        fp = file_object.open('rb')
        file_content = pdf_to_text_for_direct_upload(file_object)

    elif file_extension == '.rtf':
        file_content = PlaintextWriter.write(file_object).getvalue()

    elif file_extension == '.doc':
        content,errors = subprocess.Popen(
                            [
                                "antiword", 
                                path,
                                "-f",
                                "-i", 
                                "1"
                                ],
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            stdin = subprocess.PIPE
                        ).communicate()
        file_content = content

    elif file_extension == '.html':
        soup = BeautifulSoup(html)
        file_content = soup.get_text()


    name_list = list(get_name(file_content))
    email_list = get_email(file_content)
    phone_list = get_phone_number(file_content)
    skill_list = list(get_skills(file_content))
    education_dict = get_education(file_content)
    work_experience_dict = get_work_experience(file_content)
    
    
    if output_type == 'json':
        return output_in_json(date_list, email_list, name_list, phone_list, skill_list, education_dict, work_experience_dict)

    else:
        return output_in_xml(date_list, email_list, name_list, phone_list, skill_list, education_dict, work_experience_dict)

# file_name = sys.argv[1]
# output_type = sys.argv[2]
# extractstract_file_content(file_name, output_type)    