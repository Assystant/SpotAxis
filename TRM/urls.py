# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.urls import path, re_path, include
# from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, include
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib.auth import views as django_auth_views
from common.forms import ChangePasswordForm, RecoverUserForm, CustomPasswordResetForm
from candidates import views as candidates_views
from common import views as common_views
from common import ajax as common_ajax_views
from companies import views as companies_views
from TRM import views as TRM_views
from TRM.static_views import RobotsTxtView, SitemapXmlView, GoogleVerificationView
from example import views as example_views
from payments import views as payments_views
from vacancies import views as vacancy_views
# from socialmultishare import views as socialmultishare_views
from TRM import settings
# from django.views.generic.simple import direct_to_template
from companies.views import upload_vacancy_file, delete_vacancy_file

admin.autodiscover()
handler500 = 'TRM.views.handler500'

urlpatterns = [
    # Admin:
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('robots.txt', RobotsTxtView.as_view()),
    path('sitemap.xml', SitemapXmlView.as_view()),
    path('google7467b69f25fa8f1e.html', GoogleVerificationView.as_view()),
  
    # API URLs
    re_path(r'^api/common/', include('common.api.urls')),
    re_path(r'^api/activities/',include('activities.api.urls')),
    re_path(r'^api/vacancy/', include('vacancies_api.urls')),
    # url(r'^api/zinnia/',include('zinna.api.urls')),
    re_path(r'^api/ckeditor/', include('ckeditor.api.urls')),
    re_path(r'api/companies/', include('companies_api.urls')),
    re_path(r'^api/candidates/', include('candidates.api.urls')),

    # Resources
    re_path(r'resources/comments/', include('django_comments.urls')),
    # url(r'resources/', include('zinnia.urls')),
    # url(r'help/', include('helpdesk.urls')),

    # Index
    #path('', vacancy_views.search_vacancies, name='TRM-index'),
    path('', TRM_views.index, name='TRM-index'),
    path('aboutus/', TRM_views.about_us, name="about_us"),
    path('product/', TRM_views.product, name="product"),
    path('pricing/', TRM_views.pricing, name="pricing"),
    path('contact/', TRM_views.contact, name="contact"),
    path('comingsoon/', TRM_views.comingsoon, name="comingsoon"),
    path('jobs/', TRM_views.job_board, name="job_board"),

    # Candidates - candidates.views.py
    path('signup/talent/', candidates_views.record_candidate, name='candidates_register_candidate'),
    path('profile/', candidates_views.edit_curriculum, name='candidates_edit_curriculum'),
    re_path(r'^profile/(?P<candidate_id>\d+)/$', candidates_views.edit_curriculum, name='candidates_edit_curriculum'),
    #url(r'^profile/personal/$', candidates_views.cv_personal_info, name='candidates_cv_personal_info'),
    #url(r'^profile/objective/$', candidates_views.cv_objective, name='candidates_cv_objective'),
    # url(r'^profile/courses/$', candidates_views.cv_courses, name='candidates_cv_courses'),
    #url(r'^profile/experience/$', candidates_views.cv_expertise, name='candidates_cv_expertise'),
    #url(r'^profile/experience/(?P<expertise_id>\d+)/$', candidates_views.cv_expertise, name='candidates_cv_expertise'),
    #url(r'^profile/academic/$', candidates_views.cv_academic, name='candidates_cv_academic'),
    #url(r'^profile/academic/(?P<academic_id>\d+)/$', candidates_views.cv_academic, name='candidates_cv_academic'),
    #url(r'^profile/language/$', candidates_views.cv_language, name='candidates_cv_language'),
    # url(r'^profile/informatica/$', candidates_views.cv_software, name='candidates_cv_software'),
    # url(r'^profile/informatica/(?P<software_id>\d+)/$', candidates_views.cv_software, name='candidates_cv_software'),
    #url(r'^profile/del-expertise/(?P<expertise_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_expertise'),
    #url(r'^profile/del-academic/(?P<academic_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_academic'),
    # url(r'^profile/del-software/(?P<software_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_software'),
    #url(r'^create-candidates/$', candidates_views.create_candidates, name='candidates_create_candidates'),
    re_path(r'^profile/pdf/(?P<candidate_id>\d+)/$', candidates_views.curriculum_to_pdf, name='vacancies_curriculum_to_pdf'),
    re_path(r'^profile/pdf/(?P<candidate_id>\d+)/(?P<template>\d+)/$', candidates_views.curriculum_to_pdf, name='vacancies_curriculum_to_pdf_with_template'),
    re_path(r'^appliedjobs/$', candidates_views.vacancies_postulated, name='candidates_vacancies_postuladed'),
    re_path(r'^applylater/$', candidates_views.vacancies_favorites, name='candidates_vacancies_favourites'),
    # url(r'^resumebuilder/$', candidates_views.resume_builder, name="candidates_resume_builder"),
    # url(r'^resumebuilder/templates/(?P<candidate_id>\d+)/$', candidates_views.resume_builder_templates, name="candidates_resume_builder_templates"),
    
    # Common - Django Contrib Auth
    # url(r'^', include('common.common_auth_urls')),
    path('login/', django_auth_views.LoginView.as_view(), name='auth_login'),
    path('logout/', django_auth_views.LogoutView.as_view(), name='auth_logout'),
    path('password/change/', django_auth_views.PasswordChangeView.as_view(), name='auth_password_change'),
    path('password/reset/', django_auth_views.PasswordResetView.as_view(), name='auth_password_reset'),
    re_path(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', django_auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/done/', django_auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('username/recover/', django_auth_views.PasswordResetView.as_view(), name='recover_user'),

    # Common - common.views.py
    re_path(r'^login/social/(?P<social_code>\w+)/$', common_views.social_login, name="social_login"),
    re_path(r'^login/social/(?P<social_code>\w+)/(?P<vacancy_id>\d+)/$', common_views.social_login, name="social_login"),
    re_path(r'^login/social/(?P<social_code>\w+)/(?P<vacancy_id>\d+)/(?P<recruiter_id>\d+)/$', common_views.social_login, name="social_login"),
    # url(r'^login/social/(?P<social_code>\w+)/(?P<vacancy_id>\d+)/(?P<redirect_type>\d+)/$', common_views.social_login, name="social_login"),
    path('redirect/', common_views.redirect_after_login, name='common_redirect_after_login'),
    path('signup/complete/', common_views.registration_complete, name='common_registration_complete'),
    path('email/change/', common_views.email_change, name='common_email_change'),
    path('email/changerequested/', common_views.email_change_requested, name='common_email_change_requested'),
    re_path(r'^email/verify/(?P<token>[0-9A-Za-z-]+)/(?P<code>[0-9A-Za-z-]+)/$', common_views.email_change_approve, name='common_email_change_approve'),
    re_path(r'^activate/(?P<activation_key>\w+)/$', common_views.registration_activate, name='common_registration_activate'),
    re_path(r'^password/changed/$', common_views.password_change_done, name='common_password_change_done'),
    re_path(r'^password/reset/completed/$', common_views.custom_password_reset_complete, name='custom_password_reset_complete'),
    re_path(r'^username/recover/requested/$', common_views.recover_user_requested, name='common_recover_user_requested'),
    # url(r'^contactus/$', common_views.ContactFormView.as_view(), name='common_contact_form'),
    # url(r'^contactus/$', common_views.contact_form, name = 'common_contact_form'),
    # url(r'^sent/$', TemplateView.as_view(template_name='contact_form_sent.html'), name='common_contact_form_sent'),
    # url(r'^register_email/$', common_views.register_blank_email, name='common_register_blank_email'),

    # Common Ajax - common.ajax.py
    re_path(r'^ajax/login/$', common_ajax_views.ajax_login, name='ajax_login'),
    re_path(r'^ajax/companies-change-academic-area/$', common_ajax_views.companies_change_academic_area),
    re_path(r'^ajax/companies-allow-career/$', common_ajax_views.companies_allow_career),
    # url(r'^ajax/companies-change-state/$', common_ajax_views.companies_change_state),
    re_path(r'^ajax/candidates-change-degree/$', common_ajax_views.candidates_change_degree),
    # url(r'^ajax/candidates-change-career/$', common_ajax_views.candidates_change_career),
    re_path(r'^ajax/candidates-change-academic-status/$', common_ajax_views.candidates_change_academic_status),
    # url(r'^ajax/get-company-areas/$', common_ajax_views.get_company_areas),
    re_path(r'^ajax/jobs-postulate/$', common_ajax_views.vacancies_postulate),
    # url(r'^ajax/get-municipals/$', common_ajax_views.get_municipals),
    # url(r'^ajax/get-common-areas/$', common_ajax_views.get_common_areas),
    re_path(r'^ajax/get-salarytype-codename/$', common_ajax_views.get_salarytype_codename),
    re_path(r'^ajax/jobs-answer-question/$', common_ajax_views.vacancies_answer_question),
    re_path(r'^ajax/mark-vacancy-asfavorite/$', common_ajax_views.mark_unmark_vacancy_as_favorite),
    re_path(r'^ajax/addstage/$', common_ajax_views.add_stage),
    re_path(r'^ajax/validate_personal_form/$',common_ajax_views.validate_personal_form),
    re_path(r'^ajax/validate_contact_form/$',common_ajax_views.validate_contact_form),
    re_path(r'^ajax/validate_academic_form/$',common_ajax_views.validate_academic_form),
    re_path(r'^ajax/validate_experience_form/$',common_ajax_views.validate_experience_form),
    re_path(r'^ajax/validate_training_form/$',common_ajax_views.validate_training_form),
    re_path(r'^ajax/validate_project_form/$',common_ajax_views.validate_project_form),
    re_path(r'^ajax/validate_certificate_form/$',common_ajax_views.validate_certificate_form),
    re_path(r'^ajax/validate_objective_form/$',common_ajax_views.validate_objective_form),
    re_path(r'^ajax/validate_interests_form/$',common_ajax_views.validate_interests_form),
    re_path(r'^ajax/validate_hobbies_form/$',common_ajax_views.validate_hobbies_form),
    re_path(r'^ajax/validate_extra_curriculars_form/$',common_ajax_views.validate_extra_curriculars_form),
    re_path(r'^ajax/validate_others_form/$',common_ajax_views.validate_others_form),
    re_path(r'^ajax/validate_language_form/$',common_ajax_views.validate_language_form),
    re_path(r'^ajax/delete_section/$',common_ajax_views.delete_section),
    re_path(r'^ajax/generate_public_cv/$',common_ajax_views.generate_public_cv),
    re_path(r'^ajax/pricingrequest/$', common_ajax_views.public_contact_form),
    re_path(r'^ajax/updatepermissions/$', common_ajax_views.update_permissions),
    re_path(r'^ajax/removemember/$', common_ajax_views.remove_member),
    re_path(r'^ajax/changeownership/$', common_ajax_views.change_ownership),
    re_path(r'^ajax/withdraw/$', common_ajax_views.withdraw),
    re_path(r'^ajax/set_plan/$', common_ajax_views.set_plan),
    re_path(r'^ajax/verify_code/$', common_ajax_views.verify_code),
    re_path(r'^ajax/update_recurring/$', common_ajax_views.update_recurring),
    re_path(r'^ajax/renew_now/$', common_ajax_views.renew_now),
    re_path(r'^ajax/mark_as_read/$', common_ajax_views.mark_as_read),
    re_path(r'^ajax/add_external_referal/$', common_ajax_views.add_external_referal),
    re_path(r'^ajax/remove_external_referal/$', common_ajax_views.remove_external_referal),
    # Companies - companies.views.py
    re_path(r'^signup/employer/$', companies_views.record_recruiter, name='companies_record_recruiter'),
    re_path(r'^signup/employer/(?P<token>\w+)/$', companies_views.record_recruiter, name='companies_recruiter_invitation'),
    re_path(r'^profile/company/create/$', companies_views.record_company, name='companies_record_company'),
    re_path(r'^profile/employer/$', companies_views.recruiter_profile, name='companies_recruiter_profile'),
    re_path(r'^profile/company/$', companies_views.company_profile, name='companies_company_profile'),
    re_path(r'^careerssite/(?P<setting>\w+)/$', companies_views.site_management, name='companies_site_management'),
    re_path(r'^team/$', companies_views.team_space, name = 'companies_company_team_space'),
    re_path(r'^billing/$', companies_views.billing, name = 'companies_billing'),
    re_path(r'^payment/$', payments_views.payment, name = 'companies_payment'),
    re_path(r'^checkout/$', payments_views.checkout, name = 'payments_checkout'),
    # url(r'^profile/company/change/$', companies_views.edit_company, name='companies_edit_company'),
    # url(r'^summary/jobs/$', companies_views.vacancies_summary, name='companies_vacancies_summary'),
    re_path(r'^job/edit/$', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    re_path(r'^job/edit/(?P<vacancy_id>\d+)/$', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    # url(r'^Finalizevacancy/(?P<vacancy_id>\d+)/$', companies_views.finalize_vacancy, name='companies_finalize_vacancy'),
    # url(r'^Removevacancy/(?P<vacancy_id>\d+)/$', companies_views.remove_vacancy, name='companies_remove_vacancy'),
    # url(r'^Publishvacancy/(?P<vacancy_id>\d+)/$', companies_views.publish_vacancy, name='companies_publish_vacancy'),
    # url(r'^apply/job/(?P<vacancy_id>\d+)/$', companies_views.applications_for_vacancy,
        # name='companies_applications_for_vacancy'),
    # url(r'^curricula/$', companies_views.first_search_curricula, name='companies_first_search_curricula'),
    # url(r'^search/curricula/$', companies_views.search_curricula, name='companies_search_curricula'),
    re_path(r'^profile/candidate/(?P<candidate_id>\d+)/$', companies_views.curriculum_detail, name='companies_curriculum_detail'),
    re_path(r'^profile/candidate/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', companies_views.curriculum_detail,
        name='companies_curriculum_detail'),
    # url(r'^public/candidate/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', companies_views.public_curriculum_detail,
        # name='companies_public_curriculum_detail'),
    # url(r'^profile/discard/candidate/(?P<vacancy_id>\d+)/(?P<candidate_id>\d+)/$', companies_views.discard_candidate,
        # name='companies_discard_candidate'),
    # url(r'^recommendations/$', companies_views.company_recommendations, name='companies_company_recommendations'),
    # url(r'^money/$', companies_views.company_wallet, name='companies_company_wallet'),

    # TRM - TRM.views.py
    # url(r'^companies/$', TRM_views.companies, name='TRM_companies'),
    re_path(r'^privacypolicy/$', TRM_views.privacy_policy, name='TRM_privacy_policy'),
    re_path(r'^termsandconditions/$', TRM_views.terms_and_conditions, name='TRM_terms_and_conditions'),
    # url(r'^campaigns/0$', TRM_views.email_campaign_0, name='TRM_email_campaign_0'),

    # Example - example.views.py
    # url(r'^test/$', example_views.test, name='test'),

    # Vacancies - vacancies.views.py
    # url(r'^search/vacancies/$', vacancy_views.first_search, name='vacancies_first_search'),
    # url(r'^vacancies/$', vacancy_views.search_vacancies, {'template_name': 'search_vacancies.html'},
    #     name='vacancies_search_vacancies'),
    # url(r'^jobs/fetch/(?P<days>\d+)/$', vacancy_views.filter_vacancies_by_pub_date,
    #     name='vacancies_filter_vacancies_by_pub_date'),
    # url(r'^jobs/industry/(?P<industry_id>\d+)/$', vacancy_views.filter_vacancies_by_industry,
    #     name='vacancies_filter_vacancies_by_industry'),
    # url(r'^jobs/state/(?P<state_id>\d+)/$', vacancy_views.filter_vacancies_by_state,
    #     name='vacancies_filter_vacancies_by_state'),
    # url(r'^jobs/type/(?P<employmentType_id>\d+)/$', vacancy_views.filter_vacancies_by_employment_type,
    #     name='vacancies_filter_vacancies_by_employmentType'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/social/(?P<social_code>\w+)/$', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/(?P<social_code>\w+)/$', vacancy_views.vacancy_details, name='social_verification'),
    # url(r'^jobs/(?P<vacancy_id>\d+)/social/(?P<social_code>\w+)/(?P<social_auth_id>\d+)/$', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/ref-(?P<referer>\w+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_referal'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/eref-(?P<external_referer>\w+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_external_referal'),
    re_path(r'^jobs/(?P<vacancy_id>\d+)/(?P<vacancy_stage>\d+)/$', vacancy_views.vacancy_stage_details, name='vacancies_get_vacancy_stage_details'),
    # url(r'^jobs/company/(?P<company_id>\d+)/$', vacancy_views.vacancies_by_company, name='vacancies_vacancies_by_company'),
    # url(r'^jobs/create/$', vacancy_views.create_vacancies, name='vacancies_create_vacancies'),
    re_path(r'^jobs/pdf/(?P<vacancy_id>\d+)/$', vacancy_views.vacancy_to_pdf, name='vacancies_vacancy_to_pdf'),

    #Social Multi Share views
    # url(r'^job/share/(?P<vacancy_id>\d+)/$', socialmultishare_views.share_to_social_media, name='socialmultishare_share_to_social_media'),
    # url(r'^twitter_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_twitter, name='socialmultishare_connect_to_twitter'),
    # url(r'^facebook_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_facebook, name='socialmultishare_connect_to_facebook'),
    # url(r'^linkedin_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_linkedin, name='socialmultishare_connect_to_linkedin'),

    # Google Verification
    # url(r'^google279fe40bd6505938\.html$',
    #  lambda r: HttpResponse("google-site-verification: google279fe40bd6505938.html", content_type="text/plain")),

    # Includes
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^ajax-uploads/', include('upload_logos.urls')),
    # re_path(r'^rosetta/', include('rosetta.urls')),
    re_path(r'^ckeditor/', include('ckeditor.urls')),
    # url('', include('social.apps.django_app.urls', namespace='social')),  # Auth con face, google, twitter
    # url('', include('django.contrib.auth.urls', namespace='auth')),  # Auth con face, google, twitter
    re_path(r'^upload/file/$', upload_vacancy_file, name='upload-file'),
    re_path(r'^delete/file/$', delete_vacancy_file, name='delete-file'),
    re_path(r'^pricing-request/$', common_ajax_views.pricing_request, name = "pricing_request"),
    re_path(r'^notifications/$', common_ajax_views.notifications, name = "notifications"),

    #Widget Urls
    re_path(r'^widget/jobs/$', companies_views.widget_jobs, name="companies_job_widget"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]