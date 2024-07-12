# -*- ENCODING: UTF-8 -*-
#!/bin/bash
# If you are in a virtualenv you need to activate it before you can run ./manage.py 'command'
# source path/to/your/virtualenv/bin/activate
echo " "
echo "Starting Copy of Records..."
echo "-----------------------------------"
echo "Common Records"
echo "Copying..."
# python manage.py loaddata common_industry
# python manage.py loaddata common_area
python manage.py loaddata common_country
python manage.py loaddata common_currency
# python manage.py loaddata common_state
# python manage.py loaddata common_municipal
python manage.py loaddata common_degree
python manage.py loaddata common_employment_type
python manage.py loaddata common_gender
# python manage.py loaddata common_identification_doc
python manage.py loaddata common_marital_status
python manage.py loaddata common_profile
echo "Common Records Copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Company Records"
echo "Copying..."
python manage.py loaddata companies_company_industry
# python manage.py loaddata companies_company_area
# python manage.py loaddata companies_recommendation_status
echo "Company Records copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Custom Field Records"
echo "Copying..."
python manage.py loaddata customfield_fieldclassification
python manage.py loaddata customfield_fieldtype
echo "Custom Field Records copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Job Records"
echo "Copying..."
python manage.py loaddata vacancies_employment_experience
python manage.py loaddata vacancies_salary_type
python manage.py loaddata vacancies_pubdate_search
python manage.py loaddata vacancies_vacancy_status
echo "Job Records Copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Candidate Records"
echo "Copying..."
python manage.py loaddata candidates_academic_area
# python manage.py loaddata candidates_academic_career
# python manage.py loaddata candidates_school_type
python manage.py loaddata candidates_academic_status
python manage.py loaddata candidates_language
# python manage.py loaddata candidates_language_level
# python manage.py loaddata candidates_software
# python manage.py loaddata candidates_software_level
echo "Candidate Records Copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Payment Records"
echo "Copying..."
python manage.py loaddata payments_servicecategory
python manage.py loaddata payments_services
python manage.py loaddata payments_package
python manage.py loaddata payments_priceslab
python manage.py loaddata payments_discount
echo "Payment Records Copied"
echo "-------------------------------------"
echo "Copy of Records Completed."
echo " "