from __future__ import absolute_import
from __future__ import print_function
import datefinder
import json
import re
import sys
import pdb

"""
  STATUS:
    0 - No actionable / Remove Record
    1 - Merge with records / Remove merged
    2 - Conflicted Records
    3 - New Record
"""
# def manage_date_of_birth_conflicts(candidate_profile, conflicted_profile):
    # '''
    # prints all the date_of_birth
    # conflicts that are in the 
    # two json files
    #    ''' 
    # message = ''
    # date_of_birth_conflict_list = list()
    # print(candidate_profile)
    # if candidate_profile.birthday and conflicted_profile.birthday:
        
    #    # generalised_date_one_finder = datefinder.find_dates(candidate_profile.birthday)
    #    # for date in generalised_date_one_finder:
    #    #    formatted_date_one = date 

    #    # generalised_date_two_finder = datefinder.find_dates(conflicted_profile.birthday)
    #    # for date in generalised_date_two_finder:
    #    #    formatted_date_two = date

    #    if str(formatted_date_one) == str(formatted_date_two):
    #        message = 'both date_of_birth matches'
    #        date_of_birth_conflict_list.append('NoConflict')

    #    else:
    #        message = 'date_of_births do not match'
    #        date_of_birth_conflict_list.append(candidate_profile.birthday)
    #        date_of_birth_conflict_list.append(conflicted_profile.birthday)
    
    # elif not candidate_profile.birthday and conflicted_profile.birthday:

    #    generalised_date_two_finder = datefinder.find_dates(conflicted_profile.birthday)
    #    for date in generalised_date_two_finder:
    #        formatted_date_two = date

    #    candidate_profile.birthday = formatted_date_two.split()[0]
    #    message = 'date_of_birth second copied into first'
    #    date_of_birth_conflict_list.append('')
    #    date_of_birth_conflict_list.append(conflicted_profile.birthday)

    # print message

    # return date_of_birth_conflict_list

def get_name_status(candidate_profile, conflicted_profile):
    '''
    prints the name
    conflicts that are in the 
    two json files
    ''' 
    status = 0

    first_name_status = 0
    if conflicted_profile.first_name:
        if candidate_profile.first_name:
            if conflicted_profile.first_name == candidate_profile.first_name:
                first_name_status = 1
            else:
                first_name_status = 2
        else:
            first_name_status = 1
    
    last_name_status = 0
    if conflicted_profile.last_name:
        if candidate_profile.last_name:
            if conflicted_profile.last_name == candidate_profile.last_name:
                last_name_status = 1
            else:
                last_name_status = 2
        else:
            last_name_status = 1

    if first_name_status == 2 or last_name_status == 2:
        message = 'Conflicted'
        status = 2
    elif first_name_status == 1 or last_name_status == 1:
        message = 'Merge'
        status = 1
    else:    
        message = 'No Conflict'

    print(message)
    return status

def get_education_status(original_education, education):
    '''
    prints all education related
    conflicts that are in the 
    two json files
    ''' 
    status = 0
    education_type_match_flag = False
    start_date_match_flag = False
    not_ongoing_match_flag = False
    end_date_match_flag = False
    degree_match_flag = False
    course_name_match_flag = False
    area_match_flag = False
    school_match_flag = False
    city_match_flag = False
    state_match_flag = False
    country_match_flag = False
    education_type_status = 0
     #    if education.education_type:
        #    if original_education.education_type:
        #         if education.education_type == original_education.education_type:
        #            education_type_status = 0
        #            education_type_match_flag = True
        #        else:
        #            education_type_status = 2
        #     else:
        #         education_type_status = 1
    start_date_status = 0
    if education.start_date:
        if original_education.start_date:
            if education.start_date == original_education.start_date:
                start_date_status = 0
                start_date_match_flag = True
            else:
                start_date_status = 2
        else:
            start_date_status = 1
    status_status = 0
    if education.status:
        if original_education.status:
            if education.status == original_education.status:
                status_status = 0
                status_match_flag = True
            else:
                status_status = 2
        else:
            status_status = 1
    end_date_status = 0
    if education.end_date:
        if original_education.end_date:
            if education.end_date == original_education.end_date:
                end_date_status = 0
                end_date_match_flag = True
            else:
                end_date_status = 2
        else:
            end_date_status = 1
    degree_status = 0
    if education.degree:
        if original_education.degree:
            if education.degree == original_education.degree:
                degree_status = 0
                degree_match_flag = True
            else:
                degree_status = 2
        else:
            degree_status = 1
    course_name_status = 0
    if education.course_name:
        if original_education.course_name:
            if education.course_name == original_education.course_name:
                course_name_status = 0
                course_name_match_flag = True
            else:
                course_name_status = 2
                # courses_corpus_list = open(r'courses_corpus.txt').readlines()
                # for index, item in enumerate(courses_corpus_list):
                #    if item.strip() == original_education.course_name:
                #        if ((courses_corpus_list[index + 1]).strip() == education.course_name) or ((courses_corpus_list[index-1]).strip() == education.course_name)0
                #            course_name_match_flag = True
                #            course_name_status = 1
                #            break
        else:
            course_name_status = 1
    area_status = 0
    if education.area:
        if original_education.area:
            if education.area == original_education.area:
                area_status = 0
                area_match_flag = True
            else:
                area_status = 2
        else:
            area_status = 1
    school_status = 0
    if education.school:
        if original_education.school:
            if education.school == original_education.school:
                school_status = 0
                school_match_flag = True
            else:
                school_status = 2
        else:
            school_status = 1
    city_status = 0
    if education.city:
        if original_education.city:
            if education.city == original_education.city:
                city_status = 0
                city_match_flag = True
            else:
                city_status = 2
        else:
            city_status = 1
    state_status = 0
    if education.state:
        if original_education.state:
            if education.state == original_education.state:
                state_status = 0
                state_match_flag = True
            else:
                state_status = 2
        else:
            state_status = 1
    country_status = 0
    if education.country:
        if original_education.country:
            if education.country == original_education.country:
                country_status = 0
                country_match_flag = True
            else:
                country_status = 2
        else:
            country_status = 1
    conflict_fields = []
    if education_type_status == 2:
        conflict_fields.append('education_type')
    if status_status == 2:
        conflict_fields.append('status')
    if start_date_status == 2:
        conflict_fields.append('start_date')
    if end_date_status == 2:
        conflict_fields.append('end_date')
    if degree_status == 2:
        conflict_fields.append('degree')
    if course_name_status == 2:
        conflict_fields.append('course_name')
    if area_status == 2:
        conflict_fields.append('area')
    if country_status == 2:
        conflict_fields.append('country')
    if state_status == 2:
        conflict_fields.append('state')
    if city_status == 2:
        conflict_fields.append('city')
    if school_status == 2:
        conflict_fields.append('school')
    merge_fields = []
    if len(conflict_fields) > 0:
        status = 2
    elif education_type_match_flag or school_match_flag or degree_match_flag or area_match_flag or course_name_match_flag:
        if education_type_status == 1 or degree_status == 1 or area_status == 1 or school_status == 1 \
        or status_status == 1 or start_date_status == 1 or end_date_status == 1 \
        or course_name_status == 1 or country_status == 1 or state_status == 1 or city_status == 1:
            status = 1
            if education_type_status == 1:
                merge_fields.append('education_type')
            if degree_status == 1:
                merge_fields.append('degree')
            if area_status == 1:
                merge_fields.append('area')
            if status_status == 1:
                merge_fields.append('status')
            if start_date_status == 1:
                merge_fields.append('start_date')
            if end_date_status == 1:
                merge_fields.append('end_date')
            if course_name_status == 1:
                merge_fields.append('course_name')
            if country_status == 1:
                merge_fields.append('country')
            if state_status == 1:
                merge_fields.append('state')
            if city_status == 1:
                merge_fields.append('city')
            if school_status == 1 :
                merge_fields.append('school')
    else:
        status = 3
    return {
    		'id': education.id,
            'status' : status,
            'conflict_fields': conflict_fields,
            'merge_fields': merge_fields
        }

def manage_work_experience_conflicts(original_experience, experience):
    '''
    prints the work-experience related
    conflicts that are in the 
    two json files
    ''' 
    job_type_match_flag  = False
    employment_match_flag = False
    start_date_match_flag = False
    end_date_match_flag = False
    industry_match_flag = False
    function_match_flag = False
    company_match_flag = False
    country_match_flag = False
    state_match_flag = False
    city_match_flag = False
    present_match_flag = False
    tasks_match_flag = False
    job_type_status = 0
    # if experience.job_type:
    #     if original_experience.job_type:
       #      if experience.job_type == original_experience.job_type:
       #          job_type_status = 0
       #          job_type_match_flag = True
       #      else:
       #          job_type_status = 2
       #  else:
       #      job_type_status = 1
    function_status = 0
    # if experience.function:
     #    if original_experience.function:
        #     if experience.function == original_experience.function:
        #         function_status = 0
        #         function_match_flag = True
        #     else:
        #         function_status = 2
        # else:
        #     function_status = 1
    company_status = 0
    if experience.company:
        if original_experience.company:
            if experience.company == original_experience.company:
                company_status = 0
                company_match_flag = True
            else:
                company_status = 2
        else:
            company_status = 1
    industry_status = 0
    if experience.industry:
        if original_experience.industry:
            if experience.industry == original_experience.industry:
                industry_status = 0
                industry_match_flag = True
            else:
                industry_status = 2
        else:
            industry_status = 1
    country_status = 0
    if experience.country:
        if original_experience.country:
            if experience.country == original_experience.country:
                country_status = 0
                country_match_flag = True
            else:
                country_status = 2
        else:
            country_status = 1
    state_status = 0
    if experience.state:
        if original_experience.state:
            if experience.state == original_experience.state:
                state_status = 0
                state_match_flag = True
            else:
                state_status = 2
        else:
            state_status = 1
    city_status = 0
    if experience.city:
        if original_experience.city:
            if experience.city == original_experience.city:
                city_status = 0
                city_match_flag = True
            else:
                city_status = 2
        else:
            city_status = 1
    employment_status = 0
    if experience.employment:
        if original_experience.employment:
            if experience.employment == original_experience.employment:
                employment_status = 0
                employment_match_flag = True
            else:
                employment_status = 2
        else:
            employment_status = 1
    start_date_status = 0
    if experience.start_date:
        if original_experience.start_date:
            if experience.start_date == original_experience.start_date:
                start_date_status = 0
                start_date_match_flag = True
            else:
                start_date_status = 2
        else:
            start_date_status = 1
    end_date_status = 0
    if experience.end_date:
        if original_experience.end_date:
            if experience.end_date == original_experience.end_date:
                end_date_status = 0
                end_date_match_flag = True
            else:
                end_date_status = 2
        else:
            end_date_status = 1
    present_status = 0
    if experience.present:
        if original_experience.present:
            if experience.present == original_experience.present:
                present_status = 0
                present_match_flag = True
            else:
                present_status = 2
        else:
            present_status = 1
    tasks_status = 0
    if experience.tasks:
        if original_experience.tasks:
            if experience.tasks == original_experience.tasks:
                tasks_status = 0
                tasks_match_flag = True
            else:
                tasks_status = 2
        else:
            tasks_status = 1
    conflict_fields = []
    if job_type_status == 2:
        conflict_fields.append('job_type')
    if function_status == 2:
        conflict_fields.append('function')
    if company_status == 2:
        conflict_fields.append('company')
    if industry_status == 2:
        conflict_fields.append('industry')
    if start_date_status == 2:
        conflict_fields.append('start_date')
    if end_date_status == 2:
        conflict_fields.append('end_date')
    if employment_status == 2:
        conflict_fields.append('employment')
    if present_status == 2:
        conflict_fields.append('present')
    if tasks_status == 2:
        conflict_fields.append('tasks')
    if country_status == 2:
        conflict_fields.append('country')
    if state_status == 2:
        conflict_fields.append('state')
    if city_status == 2:
        conflict_fields.append('city')
    merge_fields = []
    if len(conflict_fields) > 0:
        status = 2
    elif job_type_match_flag or function_match_flag or industry_match_flag or company_match_flag or employment_match_flag:
        if job_type_status == 1 or function_status == 1 or company_status == 1 or tasks_status == 1 \
        or industry_status == 1 or start_date_status == 1 or end_date_status == 1 or present_status == 1 \
        or employment_status == 1 or country_status == 1 or state_status == 1 or city_status == 1:
            status = 1
            if job_type_status == 1:
                merge_fields.append('job_type')
            if function_status == 1:
                merge_fields.append('function')
            if company_status == 1:
                merge_fields.append('company')
            if tasks_status == 1:
                merge_fields.append('tasks')
            if start_date_status == 1:
                merge_fields.append('start_date')
            if end_date_status == 1:
                merge_fields.append('end_date')
            if industry_status == 1:
                merge_fields.append('industry')
            if country_status == 1:
                merge_fields.append('country')
            if state_status == 1:
                merge_fields.append('state')
            if city_status == 1:
                merge_fields.append('city')
            if present_status == 1 :
                merge_fields.append('present')
            if employment_status == 1 :
                merge_fields.append('employment')
    else:
        status = 3
    return {
    		'id': experience.id,
            'status': status,
            'conflict_fields': conflict_fields,
            'merge_fields': merge_fields,
        }

def load_json_file(json_file):
    with open(json_file) as data_file:
        return json.load(data_file)

def least_conflicted(conflicts_list):
    if conflicts_list:
        least_conflicts = 0
        least_conflicted = 0
        for i,conflict in enumerate(conflicts_list):
            if i == 0:
                least_conflicts = len(conflict['conflict_fields'])
            elif len(conflict['conflict_fields']) < least_conflicts:
                least_conflicts = len(conflict['conflict_fields'])
                least_conflicted = i
        return conflicts_list[least_conflicted]
    else:
        return conflicts_list

def calculate_status(conflicts_list):
    if conflicts_list:
        for conflict in conflicts_list:
            if conflict['status'] == 0:
                return 0
        for conflict in conflicts_list:
            if conflict['status'] == 1:
                return 1
        for conflict in conflicts_list:
            if conflict['status'] == 2:
                return 2
        return 3
    else:
        return 3

def get_conflicts(candidate_profile, conflicted_profile):
    conflicts = {}
    # conflicts['dob'] = manage_date_of_birth_conflicts(candidate_profile, conflicted_profile)
    
    name_status = get_name_status(candidate_profile, conflicted_profile)
    if name_status == 2:
        conflicts['name'] = [conflicted_profile.id]
    elif name_status == 1:
        conflicted_profile.first_name = ""
        conflicted_profile.last_name = ""
        conflicted_profile.save()
    conflicts['education'] = []
    if candidate_profile.academic_set.all():
        for education in conflicted_profile.academic_set.all():
            temp_conflicts = []
            for original_education in candidate_profile.academic_set.all():
                temp_conflicts.append(get_education_status(original_education, education))
            education_status = calculate_status(temp_conflicts)
            if education_status == 0:
                education.remove()
            elif education_status == 1:
                for conflicted_education in temp_conflicts:
                    if conflicted_education['status'] == 1:
                        # merge the fields required
                        pass
                education.remove()
            elif education_status == 2:
                l_conflicted = least_conflicted(temp_conflicts)
                l_conflicted['conflicting_to'] = original_education.id
                conflicts['education'].append(l_conflicted)
            elif education_status == 3:
                education.candidate = candidate_profile
                education.save()
    else:
        for education in conflicted_profile.academic_set.all():
            education.candidate = candidate_profile
            education.save()
    conflicts['experience'] = []
    if candidate_profile.expertise_set.all():
        for experience in conflicted_profile.expertise_set.all():
            temp_conflicts = []
            for original_experience in candidate_profile.expertise_set.all():
                temp_conflicts.append(get_experience_status(original_experience, experience))
            experience_status = calculate_status(temp_conflicts)
            if experience_status == 0:
                experience.remove()
            elif experience_status == 1:
                for conflicted_experience in temp_conflicts:
                    if conflicted_experience['status'] == 1:
                        # merge the fields required
                        for field in conflicted_experience['merge_fields']:
                        	pass
                experience.remove()
            elif experience_status == 2:
                l_conflicted = least_conflicted(temp_conflicts)
                l_conflicted['conflicting_to'] = original_experience.id
                conflicts['education'].append(l_conflicted)
            elif experience_status == 3:
                experience.candidate = candidate_profile
                experience.save()
    else:
        for experience in conflicted_profile.expertise_set.all():
            experience.candidate = candidate_profile
            experience.save()
    return conflicts