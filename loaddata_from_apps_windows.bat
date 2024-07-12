echo " "
echo "Starting Copy of Records..."
echo "-----------------"
echo "Common Records"
echo "Copying..."
rem python manage.py loaddata common_industry.json
rem python manage.py loaddata common_area.json
python manage.py loaddata common_country.json
python manage.py loaddata common_currency.json
rem python manage.py loaddata common_state.json
rem python manage.py loaddata common_municipal.json
python manage.py loaddata common_degree.json
python manage.py loaddata common_employment_type.json
python manage.py loaddata common_gender.json
rem python manage.py loaddata common_identification_doc.json
python manage.py loaddata common_marital_status.json
python manage.py loaddata common_profile.json
echo "Common Records Copied"
echo " "
echo "-----------------"
echo " "
echo "Company Records"
echo "Copying..."
python manage.py loaddata companies_company_industry.json
rem python manage.py loaddata companies_company_area.json
rem python manage.py loaddata companies_recommendation_status.json
echo "Company Records Copied"
echo " "
echo "-----------------"
echo " "
echo "Custom Field Records"
echo "Copying..."
python manage.py loaddata customfield_fieldclassification.json
python manage.py loaddata customfield_fieldtype.json
echo "Custom Field Records copied"
echo " "
echo "-------------------------------------"
echo " "
echo "Job Records"
echo "Copying..."
python manage.py loaddata vacancies_employment_experience.json
python manage.py loaddata vacancies_salary_type.json
rem python manage.py loaddata vacancies_pubdate_search.json
python manage.py loaddata vacancies_vacancy_status.json
echo "Job Records Copied"
echo " "
echo "-----------------"
echo " "
echo "Candidate Records"
echo "Copying..."
python manage.py loaddata candidates_academic_area.json
rem python manage.py loaddata candidates_academic_career.json
rem python manage.py loaddata candidates_school_type.json
python manage.py loaddata candidates_academic_status.json
python manage.py loaddata candidates_language.json
rem python manage.py loaddata candidates_language_level.json
rem python manage.py loaddata candidates_software.json
rem python manage.py loaddata candidates_software_level.json
echo "Cadidate Records Copied"
echo " "
echo "-----------------"
echo "Payment Records"
echo "Copying..."
python manage.py loaddata payments_servicecategory.json
python manage.py loaddata payments_services.json
python manage.py loaddata payments_package.json
python manage.py loaddata payments_priceslab.json
python manage.py loaddata payments_discount.json
echo "Payment Records Copied"
echo "-----------------"
echo "Copy of Records Completed."
echo " "
echo " "
pause
