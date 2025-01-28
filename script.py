from __future__ import absolute_import
from common.models import send_TRM_email
from companies.models import Company
companies = Company.objects.all()
for company in companies:
	company.geturl()
	company.user.email
for company in companies:
	send_TRM_email('mails/update_subject.html','mails/update_email.html',{'careers_page':company.geturl()},company.user.email)