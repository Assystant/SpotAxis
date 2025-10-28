# SpotAxis

Version: 1.0 

SpotAxis is an Open-source (MIT Licensed) Applicant Tracking System to streamline your hiring process.

Our vision is to create the most adapted open-source Applicant Tracking System (ATS) that helps businesses to seamlessly manage the entire recruitment process, from attracting candidates to scheduling interviews, making hiring decisions and onboarding.

## SpotAxis can satisfy the use cases of two types of users ##

### 1. End users(Companies): ###
These are organizations that want to directly manage their own recruitment process using Spotaxis.

The key features for end users include the following
1. Post jobs and maintain job templates
2. Get your custom branded Career websites
3. Parse resumes of each applicant
4. Provide custom application form to candidates
5. Collaborative hiring
6. Custom hiring pipeline for each job
7. Custom rating for candidates in each hiring round
8. Compare ratings of each candidate

### 2. Developers/Entrepreneurs: ###
Can customize Spotaxis, add features, and host it for other companies to use as a subscription service(SaaS).

The key features for this user type include the following
1. Everything of End users
2. Manage multiple organizations as a super admin
3. Use the default Job Board that is pulled from all the organizations.
4. Manage jobs and applicants as a super admin
5. Subscription/Pricing Management for ATS

If you need support implementing this ATS on your server, please reach out to holesh+ats@assystant.com

## Contributors required ##

1. You can submit bugs  and help us verify as they are live
2. Contribute to bug fixes
3. Review and collaborate on source code changes
4. Write and improve SpotAxis documentation
5. Contribute new feature development

## Project Dependencies ##

* python>=3.12
* autodoc>=0.5.0,
* beautifulsoup4>=4.13.4,
* datefinder>=0.7.3,
* dicttoxml>=1.7.16,
* django>=5.2.1,
* django-bootstrap-form>=3.4,
* django-contrib-comments>=2.2.0,
* django-crontab>=0.7.1,
* django-extensions>=4.1,
* django-filter>=25.1,
* django-mptt>=0.17.0,
* django-nested-formset>=0.1.4,
* django-phonenumber-field>=8.1.0,
* django-rosetta>=0.10.2,
* django-tagging>=0.5.0,
* django-xmlrpc>=0.1.8,
* djangorestframework>=3.16.0,
* docutils>=0.21.2,
* dotenv>=0.9.9,
* email-reply-parser>=0.5.12,
* hashids>=1.3.1,
* ipgetter2>=1.1.10,
* mammoth>=1.9.1,
* markdown>=3.8,
* markdownify>=1.1.0,
* mots-vides>=2015.5.11,
* nltk>=3.9.1,
* oauth2>=1.9.0.post1,
* pandas>=2.2.3,
* paypalrestsdk>=1.13.3,
* pdfminer-six>=20250506,
* phonenumbers>=9.0.7,
* pillow>=11.2.1,
* pymysql>=1.1.1,
* pypdf>=5.5.0,
* pyth>=0.6.0,
* python-dateutil>=2.9.0.post0,
* python-docx>=1.1.2,
* python-linkedin>=4.1,
* requests>=2.32.3,
* requests-oauthlib>=2.0.0,
* rosetta>=0.3,
* scipy>=1.15.3,
* selenium>=4.33.0,
* setuptools>=80.9.0,
* six>=1.17.0,
* south>=1.0.2,
* stop-words>=2018.7.23,
* striprtf>=0.0.29,
* textile>=4.0.3,
* unidecode>=1.4.0,
* validate-email>=1.3,
* weasyprint>=65.1,
* xvfbwrapper>=0.2.13,



## tool.setuptools ##
packages = [
    "TRM",
    "activities",
    "candidates",
    "ckeditor",
    "common",
    "companies",
    "customField",
    "el_pagination",
    "example",
    "helpdesk",
    "locale",
    "payments",
    "resume_parser",
    "scheduler",
    "socialmultishare",
    "ssl",
    "upload_logos",
    "zinnia",
    "vacancies"
]
