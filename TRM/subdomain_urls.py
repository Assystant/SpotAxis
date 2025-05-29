# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.conf.urls import *
# from django.conf import settings
from django.conf.urls.static import static
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
from activities import views as activities_views
from TRM import views as TRM_views
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

    # Index
    # url(r'^$', vacancy_views.search_vacancies, {'template_name': 'index.html'}, name='TRM-index'),
    url(r'^$', companies_views.vacancies_summary, name='TRM-Subindex'),
    url(r'^activities/$', activities_views.activities, name="activity_view"),
    url(r'^activities/(?P<activity_id>\d+)/$', activities_views.activities, name="activity_view"),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type= 'text/plain')),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type= 'text/plain')),
    url(r'^google7467b69f25fa8f1e\.html$', TemplateView.as_view(template_name='google7467b69f25fa8f1e.html')),
    url(r'^aboutus/$',  TRM_views.about_us, name="about_us"),
    url(r'^product/$',  TRM_views.product, name="product"),
    url(r'^pricing/$',  TRM_views.pricing, name="pricing"),
    url(r'^contact/$',  TRM_views.contact, name="contact"),
    url(r'^comingsoon/$',  TRM_views.comingsoon, name="comingsoon"),
    url(r'^jobs/$',  TRM_views.job_board, name="job_board"),
    url(r'resources/comments/', include('django_comments.urls')),
    # url(r'resources/', include('zinnia.urls')),
    # url(r'help/', include('helpdesk.urls')),
    url(r'modal/', TemplateView.as_view(template_name='careers/modal.html')),


    # Candidates - candidates.views.py
    url(r'^signup/talent/$', candidates_views.record_candidate, name='candidates_register_candidate'),
    url(r'^profile/$', candidates_views.edit_curriculum, name='candidates_edit_curriculum'),
    # url(r'^profile/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', candidates_views.view_curriculum, name='candidates_edit_curriculum'), # TODO CHECAR / AL FINAL DE LA URL
    # url(r'^profile/personal/$', candidates_views.cv_personal_info, name='candidates_cv_personal_info'),
    # url(r'^profile/objective/$', candidates_views.cv_objective, name='candidates_cv_objective'),
    # url(r'^profile/courses/$', candidates_views.cv_courses, name='candidates_cv_courses'),
    # url(r'^profile/expertise/$', candidates_views.cv_expertise, name='candidates_cv_expertise'),
    # url(r'^profile/expertise/(?P<expertise_id>\d+)/$', candidates_views.cv_expertise, name='candidates_cv_expertise'),
    # url(r'^profile/academic/$', candidates_views.cv_academic, name='candidates_cv_academic'),
    # url(r'^profile/academic/(?P<academic_id>\d+)/$', candidates_views.cv_academic, name='candidates_cv_academic'),
    # url(r'^profile/language/$', candidates_views.cv_language, name='candidates_cv_language'),
    # url(r'^profile/informatica/$', candidates_views.cv_software, name='candidates_cv_software'),
    # url(r'^profile/informatica/(?P<software_id>\d+)/$', candidates_views.cv_software, name='candidates_cv_software'),
    # url(r'^profile/del-expertise/(?P<expertise_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_expertise'),
    # url(r'^profile/del-academic/(?P<academic_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_academic'),
    # url(r'^profile/del-software/(?P<software_id>\d+)/$', candidates_views.cv_delete_item, name='candidates_cv_delete_software'),
    # url(r'^create-candidates/$', candidates_views.create_candidates, name='candidates_create_candidates'),
    url(r'^profile/pdf/(?P<candidate_id>\d+)/$', candidates_views.curriculum_to_pdf, name='vacancies_curriculum_to_pdf'),
    url(r'^appliedjobs/$', candidates_views.vacancies_postulated, name='candidates_vacancies_postuladed'),
    url(r'^applylater/$', candidates_views.vacancies_favorites, name='candidates_vacancies_favourites'),
    # url(r'^resumebuilder/$', candidates_views.resume_builder, name="candidates_resume_builder"),
    
    # Common - Django Contrib Auth
    # url(r'^', include('common.common_auth_urls')),
    url(r'^login/$', django_auth_views.login, {'template_name': 'old_login.html'}, name='auth_login'),
    url(r'^logout/$', django_auth_views.logout, {'next_page': '/'}, name='auth_logout'),
    url(r'^password/change/$', django_auth_views.password_change,
        {'post_change_redirect': 'common_password_change_done',
         'template_name': 'password_change.html',
         'password_change_form': ChangePasswordForm},
        name='auth_password_change'),
    url(r'^password/reset/$', django_auth_views.password_reset,
        {'password_reset_form': CustomPasswordResetForm,
         'template_name': 'password_reset.html',
         'email_template_name': 'mails/password_reset_email.html',
         'subject_template_name': 'mails/password_reset_subject.html', },
        name='auth_password_reset'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        django_auth_views.password_reset_confirm,
        {'template_name': 'password_reset_confirm.html',
         'post_reset_redirect': 'custom_password_reset_complete'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/done/$', django_auth_views.password_reset_done,
        {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),
    url(r'^username/recover/$', django_auth_views.password_reset,
        {'password_reset_form': RecoverUserForm,
         'template_name': 'recover_user.html',
         'email_template_name': 'mails/recover_user_email.html',
         'subject_template_name': 'mails/recover_user_subject.html',
         'post_reset_redirect': 'common_recover_user_requested', },
        name='recover_user'),

    # Common - common.views.py
    url(r'^login/social/(?P<social_code>\w+)/$', common_views.social_login, name="social_login"),
    url(r'^login/social/(?P<social_code>\w+)/(?P<vacancy_id>\d+)/$', common_views.social_login, name="social_login"),
    url(r'^login/social/(?P<social_code>\w+)/(?P<vacancy_id>\d+)/(?P<recruiter_id>\d+)/$', common_views.social_login, name="social_login"),
    url(r'^redirect/$', common_views.redirect_after_login, name='common_redirect_after_login'),
    url(r'^signup/completed/$', common_views.registration_complete, name='common_registration_complete'),
    url(r'^email/change/$', common_views.email_change, name='common_email_change'),
    url(r'^email/changerequested/$', common_views.email_change_requested, name='common_email_change_requested'),
    url(r'^email/verify/(?P<token>[0-9A-Za-z-]+)/(?P<code>[0-9A-Za-z-]+)/$', common_views.email_change_approve,
        name='common_email_change_approve'),
    url(r'^activate/(?P<activation_key>\w+)/$', common_views.registration_activate, name='common_registration_activate'),
    url(r'^password/changed/$', common_views.password_change_done, name='common_password_change_done'),
    url(r'^password/reset/completed/$', common_views.custom_password_reset_complete, name='custom_password_reset_complete'),
    url(r'^username/recover/requested/$', common_views.recover_user_requested, name='common_recover_user_requested'),
    # url(r'^contactus/$', common_views.ContactFormView.as_view(), name='common_contact_form'),
    # url(r'^sent/$', TemplateView.as_view(template_name='contact_form_sent.html'), name='common_contact_form_sent'),
    # url(r'^register_email/$', common_views.register_blank_email, name='common_register_blank_email'),

    # Common Ajax - common.ajax.py
    url(r'^ajax/login/$', common_ajax_views.ajax_login, name='ajax_login'),
    url(r'^ajax/companies-change-academic-area/$', common_ajax_views.companies_change_academic_area),
    url(r'^ajax/companies-allow-career/$', common_ajax_views.companies_allow_career),
    # url(r'^ajax/companies-change-state/$', common_ajax_views.companies_change_state),
    url(r'^ajax/candidates-change-degree/$', common_ajax_views.candidates_change_degree),
    # url(r'^ajax/candidates-change-career/$', common_ajax_views.candidates_change_career),
    url(r'^ajax/candidates-change-academic-status/$', common_ajax_views.candidates_change_academic_status),
    # url(r'^ajax/get-company-areas/$', common_ajax_views.get_company_areas),
    url(r'^ajax/vacancies-postulate/$', common_ajax_views.vacancies_postulate),
    # url(r'^ajax/get-municipals/$', common_ajax_views.get_municipals),
    # url(r'^ajax/get-common-areas/$', common_ajax_views.get_common_areas),
    url(r'^ajax/get-salarytype-codename/$', common_ajax_views.get_salarytype_codename),
    url(r'^ajax/vacancies-answer-question/$', common_ajax_views.vacancies_answer_question),
    url(r'^ajax/mark-vacancy-asfavorite/$', common_ajax_views.mark_unmark_vacancy_as_favorite),
    url(r'^ajax/addstage/$', common_ajax_views.add_stage),
    url(r'^ajax/validate_personal_form/$',common_ajax_views.validate_personal_form),
    url(r'^ajax/validate_contact_form/$',common_ajax_views.validate_contact_form),
    url(r'^ajax/validate_academic_form/$',common_ajax_views.validate_academic_form),
    url(r'^ajax/validate_experience_form/$',common_ajax_views.validate_experience_form),
    url(r'^ajax/validate_training_form/$',common_ajax_views.validate_training_form),
    url(r'^ajax/validate_project_form/$',common_ajax_views.validate_project_form),
    url(r'^ajax/validate_certificate_form/$',common_ajax_views.validate_certificate_form),
    url(r'^ajax/validate_objective_form/$',common_ajax_views.validate_objective_form),
    url(r'^ajax/validate_interests_form/$',common_ajax_views.validate_interests_form),
    url(r'^ajax/validate_hobbies_form/$',common_ajax_views.validate_hobbies_form),
    url(r'^ajax/validate_extra_curriculars_form/$',common_ajax_views.validate_extra_curriculars_form),
    url(r'^ajax/validate_others_form/$',common_ajax_views.validate_others_form),
    url(r'^ajax/validate_language_form/$',common_ajax_views.validate_language_form),
    url(r'^ajax/updatevacancystage/$', common_ajax_views.update_vacancy_stage),
    url(r'^ajax/upgradepostulate/$', common_ajax_views.upgrade_postulate),
    url(r'^ajax/downgradepostulate/$', common_ajax_views.downgrade_postulate),
    url(r'^ajax/archivepostulate/$', common_ajax_views.archive_postulate),
    url(r'^ajax/delete_section/$',common_ajax_views.delete_section),
    url(r'^ajax/publicapplication/$', common_ajax_views.public_application),
    url(r'^ajax/updatepermissions/$', common_ajax_views.update_permissions),
    url(r'^ajax/removemember/$', common_ajax_views.remove_member),
    url(r'^ajax/changeownership/$', common_ajax_views.change_ownership),
    url(r'^ajax/addmembertojob/$', common_ajax_views.add_member_to_job),
    url(r'^ajax/removememberfromjob/$', common_ajax_views.remove_member_from_job),
    url(r'^ajax/addmembertojobprocess/$', common_ajax_views.add_member_to_job_process),
    url(r'^ajax/removememberfromjobprocess/$', common_ajax_views.remove_member_from_job_process),
    url(r'^ajax/updatecriteria/$', common_ajax_views.update_criteria),
    url(r'^ajax/comment/$', common_ajax_views.comment),
    url(r'^ajax/comment/retrieveall/$', common_ajax_views.retreive_comments),
    url(r'^ajax/rate/$', common_ajax_views.rate),
    url(r'^ajax/spot/$', common_ajax_views.spot),
    url(r'^ajax/rate/retrieveall/$', common_ajax_views.retreive_ratings),
    url(r'^ajax/tag/$', common_ajax_views.tag),
    url(r'^ajax/get-schedule/$', common_ajax_views.get_upcoming_schedule),
    url(r'^ajax/schedule/$', common_ajax_views.schedule),
    url(r'^ajax/remove-schedule/$', common_ajax_views.remove_schedule),
    url(r'^ajax/withdraw/$', common_ajax_views.withdraw),
    url(r'^ajax/filter-candidates/$', common_ajax_views.filter_candidates),
    url(r'^ajax/post/$', common_ajax_views.post_message_to_stream),
    url(r'^ajax/mark_as_read/$', common_ajax_views.mark_as_read),
    url(r'^ajax/set_plan/$', common_ajax_views.set_plan),
    url(r'^ajax/verify_code/$', common_ajax_views.verify_code),
    url(r'^ajax/update_recurring/$', common_ajax_views.update_recurring),
    url(r'^ajax/renew_now/$', common_ajax_views.renew_now),
    url(r'^ajax/smart-share/(?P<id>\d+)/$', common_ajax_views.smart_share),
    url(r'^ajax/socialshare/$', common_ajax_views.socialshare),
    url(r'^ajax/revokesocial/(?P<social_code>\w+)/$', common_ajax_views.revoke_social_auth),
    url(r'^ajax/template/$', common_ajax_views.custom_template),
    url(r'^ajax/template-form/$', common_ajax_views.template_form),
    url(r'^ajax/get-candidate-form-data/$', common_ajax_views.template_form_data),
    url(r'^ajax/updatesitetemplate/$', common_ajax_views.update_site_template),
    url(r'^ajax/save_template/$', common_ajax_views.save_template),
    url(r'^ajax/get_evaluators/$', common_ajax_views.get_evaluators),
    url(r'^ajax/get_process_criterias/$', common_ajax_views.get_process_criterias),
    url(r'^ajax/template/$', common_ajax_views.custom_template),
    url(r'^ajax/template-form/$', common_ajax_views.template_form),
    url(r'^ajax/get-candidate-form-data/$', common_ajax_views.template_form_data),
    url(r'^ajax/resolve_conflicts_delete/$', common_ajax_views.resolve_conflicts_delete),
    url(r'^ajax/resolve_conflicts_unconflict/$', common_ajax_views.resolve_conflicts_unconflict),
    url(r'^ajax/resolve_conflicts_merge/$', common_ajax_views.resolve_conflicts_merge),
    url(r'^ajax/add_external_referal/$', common_ajax_views.add_external_referal),
    url(r'^ajax/remove_external_referal/$', common_ajax_views.remove_external_referal),

    # Companies - companies.views.py
    url(r'^signup/employer/$', companies_views.record_recruiter, name='companies_record_recruiter'),
    url(r'^signup/employer/(?P<token>\w+)/$', companies_views.record_recruiter, name='companies_recruiter_invitation'),
    url(r'^profile/company/create/$', companies_views.record_company, name='companies_record_company'),
    url(r'^profile/employer/$', companies_views.recruiter_profile, name='companies_recruiter_profile'),
    url(r'^profile/company/$', companies_views.company_profile, name='companies_company_profile'),
    url(r'^careerssite/editor/$', companies_views.template_editor, name="companies_edit_template"),
    url(r'^careerssite/get_site_template/$', companies_views.get_site_template, name="companies_get_site_template"),
    url(r'^careerssite/preview/(?P<template_id>\d+)/$', companies_views.site_template_preview, name="companies_site_template_preview"),
    url(r'^careerssite/(?P<setting>\w+)/$', companies_views.site_management, name='companies_site_management'),
    url(r'^team/$', companies_views.team_space, name = 'companies_company_team_space'),
    url(r'^billing/$', companies_views.billing, name = 'companies_billing'),
    url(r'^payment/$', payments_views.payment, name = 'companies_payment'),
    url(r'^checkout/$', payments_views.checkout, name = 'payments_checkout'),
    # url(r'^profile/company/change/$', companies_views.edit_company, name='companies_edit_company'),
    # url(r'^summary/jobs/$', companies_views.vacancies_summary, name='companies_vacancies_summary'),
    url(r'^job/edit/$', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    url(r'^job/edit/(?P<vacancy_id>\d+)/$', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    url(r'^job/edit_hiring_process/(?P<vacancy_id>\d+)/$', companies_views.add_update_vacancy_hiring_process, name='companies_add_update_vacancy_hiring_process'),
    url(r'^job/edit_talent_sourcing/(?P<vacancy_id>\d+)/$', companies_views.add_update_vacancy_talent_sourcing, name='companies_add_update_vacancy_talent_sourcing'),
    url(r'^Finalizevacancy/(?P<vacancy_id>\d+)/(?P<message>\d+)/$', companies_views.finalize_vacancy, name='companies_finalize_vacancy'),
    # url(r'^Removevacancy/(?P<vacancy_id>\d+)/$', companies_views.remove_vacancy, name='companies_remove_vacancy'),
    url(r'^Publishvacancy/(?P<vacancy_id>\d+)/$', companies_views.publish_vacancy, name='companies_publish_vacancy'),
    url(r'^UnPublishvacancy/(?P<vacancy_id>\d+)/$', companies_views.unpublish_vacancy, name='companies_unpublish_vacancy'),
    # url(r'^apply/job/(?P<vacancy_id>\d+)/$', companies_views.applications_for_vacancy,
    #     name='companies_applications_for_vacancy'),
    # url(r'^curricula/$', companies_views.first_search_curricula, name='companies_first_search_curricula'),
    # url(r'^search/curricula/$', companies_views.search_curricula, name='companies_search_curricula'),
    url(r'^profile/candidate/(?P<candidate_id>\d+)/$', companies_views.curriculum_detail, name='companies_curriculum_detail'),
    url(r'^profile/candidate/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', companies_views.curriculum_detail,
        name='companies_curriculum_detail'),
    # url(r'^public/candidate/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', companies_views.public_curriculum_detail,
        # name='companies_public_curriculum_detail'),
    # url(r'^profile/discard/candidate/(?P<vacancy_id>\d+)/(?P<candidate_id>\d+)/$', companies_views.discard_candidate,
        # name='companies_discard_candidate'),
    # url(r'^recommendations/$', companies_views.company_recommendations, name='companies_company_recommendations'),
    # url(r'^money/$', companies_views.company_wallet, name='companies_company_wallet'),

    # TRM - TRM.views.py
    # url(r'^companies/$', TRM_views.companies, name='TRM_companies'),
    url(r'^privacypolicy/$', TRM_views.privacy_policy, name='TRM_privacy_policy'),
    url(r'^termsandconditions/$', TRM_views.terms_and_conditions, name='TRM_terms_and_conditions'),
    # url(r'^campaigns/0$', TRM_views.email_campaign_0, name='TRM_email_campaign_0'),

    # Example - example.views.py
    # url(r'^test/$', example_views.test, name='test'),

    # Vacancies - vacancies.views.py
    # url(r'^search/jobs/$', vacancy_views.first_search, name='vacancies_first_search'),
    # url(r'^jobs/$', vacancy_views.search_vacancies, {'template_name': 'search_vacancies.html'},
        # name='vacancies_search_vacancies'),
    # url(r'^jobs/fetch/(?P<days>\d+)/$', vacancy_views.filter_vacancies_by_pub_date,
    #     name='vacancies_filter_vacancies_by_pub_date'),
    # url(r'^jobs/industry/(?P<industry_id>\d+)/$', vacancy_views.filter_vacancies_by_industry,
    #     name='vacancies_filter_vacancies_by_industry'),
    # url(r'^jobs/state/(?P<state_id>\d+)/$', vacancy_views.filter_vacancies_by_state,
    #     name='vacancies_filter_vacancies_by_state'),
    # url(r'^jobs/type/(?P<employmentType_id>\d+)/$', vacancy_views.filter_vacancies_by_employment_type,
    #     name='vacancies_filter_vacancies_by_employmentType'),
    url(r'^jobs/(?P<vacancy_id>\d+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details'),
    url(r'^jobs/(?P<vacancy_id>\d+)/ref-(?P<referer>\w+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_referal'),
    url(r'^jobs/(?P<vacancy_id>\d+)/eref-(?P<external_referer>\w+)/$', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_external_referal'),
    url(r'^jobs/(?P<vacancy_id>\d+)/apply/$', vacancy_views.public_apply, name='vacancies_public_apply'),
    url(r'^jobs/(?P<vacancy_id>\d+)/apply/ref-(?P<referer>\w+)/$', vacancy_views.public_apply, name='vacancies_public_apply_with_referal'),
    url(r'^jobs/(?P<vacancy_id>\d+)/apply/eref-(?P<external_referer>\w+)/$', vacancy_views.public_apply, name='vacancies_public_apply_with_external_referal'),
    url(r'^jobs/(?P<vacancy_id>\d+)/new_application/$', vacancy_views.new_application, name='vacancies_new_application'),
    url(r'^jobs/(?P<vacancy_id>\d+)/new_application/resolve/(?P<card_type>\w+)/$', vacancy_views.new_application_resolve_conflicts, name='vacancies_new_application_resolve_conflicts'),
    url(r'^jobs/(?P<vacancy_id>\d+)/complete_application/$', vacancy_views.complete_application, name='vacancies_complete_application'),
    url(r'^jobs/(?P<vacancy_id>\d+)/talent_sourcing/$', vacancy_views.vacancy_talent_sourcing, name="vacancies_talent_sourcing"),
    url(r'^jobs/(?P<vacancy_id>\d+)/process/(?P<vacancy_stage>\d+)/$', vacancy_views.vacancy_stage_details, name='vacancies_get_vacancy_stage_details'),
    url(r'^jobs/(?P<vacancy_id>\d+)/process/(?P<vacancy_stage>\d+)/(?P<stage_section>\d+)/$', vacancy_views.vacancy_stage_details, name='vacancies_get_vacancy_stage_details'),
    url(r'^jobs/(?P<vacancy_id>\d+)/social/(?P<social_code>\w+)/$', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    url(r'^jobs/(?P<vacancy_id>\d+)/(?P<social_code>\w+)/$', vacancy_views.vacancy_details, name='social_verification'),
    # url(r'^jobs/(?P<vacancy_id>\d+)/social/(?P<social_code>\w+)/(?P<social_auth_id>\d+)/$', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    # url(r'^jobs/company/(?P<company_id>\d+)/$', vacancy_views.vacancies_by_company, name='vacancies_vacancies_by_company'),
    # url(r'^jobs/create/$', vacancy_views.create_vacancies, name='vacancies_create_vacancies'),
    url(r'^jobs/pdf/(?P<vacancy_id>\d+)/$', vacancy_views.vacancy_to_pdf, name='vacancies_vacancy_to_pdf'),

    #Social Multi Share views
    # url(r'^job/share/(?P<vacancy_id>\d+)/$', socialmultishare_views.share_to_social_media, name='socialmultishare_share_to_social_media'),
    # url(r'^twitter_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_twitter, name='socialmultishare_connect_to_twitter'),
    # url(r'^facebook_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_facebook, name='socialmultishare_connect_to_facebook'),
    # url(r'^linkedin_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_linkedin, name='socialmultishare_connect_to_linkedin'),

    # Google Verification
    # url(r'^google279fe40bd6505938\.html$',
    #  lambda r: HttpResponse("google-site-verification: google279fe40bd6505938.html", content_type="text/plain")),

    # Includes
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^ajax-uploads/', include('upload_logos.urls')),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    # url('', include('social.apps.django_app.urls', namespace='social')),  # Auth con face, google, twitter
    # url('', include('django.contrib.auth.urls', namespace='auth')),  # Auth con face, google, twitter
    url(r'^upload/file/$', upload_vacancy_file, name='upload-file'),
    url(r'^delete/file/$', delete_vacancy_file, name='delete-file'),
    url(r'^pricing-request/$', common_ajax_views.pricing_request, name = "pricing_request"),
    url(r'^compare-candidates/$', common_ajax_views.compare_candidates, name = "compare_candidates"),
    url(r'^notifications/$', common_ajax_views.notifications, name = "notifications"),
    url(r'^(?P<vacancy_status_name>\w+)/$', companies_views.vacancies_summary, name="companies_vacancies_by_status"),

    #Widget Urls
    url(r'^widget/jobs/$', companies_views.widget_jobs, name="companies_job_widget"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]