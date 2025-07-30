# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.urls import path, re_path, include
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
from django.urls import reverse_lazy
# from socialmultishare import views as socialmultishare_views
from TRM import settings
# from django.views.generic.simple import direct_to_template
from companies.views import upload_vacancy_file, delete_vacancy_file
from django.shortcuts import redirect
from TRM.views import custom_logout_view, comments_entrypoint

admin.autodiscover()
handler500 = 'TRM.views.handler500'

urlpatterns = [

    # Index
    # url(r'^$', vacancy_views.search_vacancies, {'template_name': 'index.html'}, name='TRM-index'),
    path('', companies_views.vacancies_summary, name='TRM-Subindex'),
    path('activities/', activities_views.activities, name="activity_view"),
    path('activities/<int:activity_id>/', activities_views.activities, name="activity_view"),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type= 'text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type= 'text/plain')),
    path('google7467b69f25fa8f1e.html', TemplateView.as_view(template_name='google7467b69f25fa8f1e.html')),
    path('aboutus/',  TRM_views.about_us, name="about_us"),
    path('product/',  TRM_views.product, name="product"),
    path('pricing/',  TRM_views.pricing, name="pricing"),
    path('contact/',  TRM_views.contact, name="contact"),
    path('comingsoon/',  TRM_views.comingsoon, name="comingsoon"),
    path('jobs/',  TRM_views.job_board, name="job_board"),
    path('resources/comments/', comments_entrypoint),
    path('resources/comments/', include('django_comments.urls')),
    # url(r'resources/', include('zinnia.urls')),
    # url(r'help/', include('helpdesk.urls')),
    path('modal/', TemplateView.as_view(template_name='careers/modal.html')),


    # Candidates - candidates.views.py
    path('signup/talent/', candidates_views.record_candidate, name='candidates_register_candidate'),
    path('profile/', candidates_views.edit_curriculum, name='candidates_edit_curriculum'),
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
    path('profile/pdf/<int:candidate_id>/', candidates_views.curriculum_to_pdf, name='vacancies_curriculum_to_pdf'),
    path('appliedjobs/', candidates_views.vacancies_postulated, name='candidates_vacancies_postuladed'),
    path('applylater/', candidates_views.vacancies_favorites, name='candidates_vacancies_favourites'),
    # url(r'^resumebuilder/$', candidates_views.resume_builder, name="candidates_resume_builder"),
    
    # Common - Django Contrib Auth
    # url(r'^', include('common.common_auth_urls')),
    
    #path('login/', django_auth_views.login, {'template_name': 'old_login.html'}, name='auth_login'),
    #path('logout/', django_auth_views.logout, {'next_page': '/'}, name='auth_logout'),
    #path('password/change/', django_auth_views.password_change,
    #    {'post_change_redirect': 'common_password_change_done',
    #     'template_name': 'password_change.html',
    #     'password_change_form': ChangePasswordForm},
    #    name='auth_password_change'),
    path('password/reset/', django_auth_views.PasswordResetView.as_view(),
        {'password_reset_form': CustomPasswordResetForm,
            'template_name': 'password_reset.html',
            'email_template_name': 'mails/password_reset_email.html',
            'subject_template_name': 'mails/password_reset_subject.html', },
        name='auth_password_reset'),
    #path('password/reset/<uidb64>[0-9A-Za-z]+>-<token>.+/',
    #    django_auth_views.password_reset_confirm,
    #    {'template_name': 'password_reset_confirm.html',
    #     'post_reset_redirect': 'custom_password_reset_complete'},
    #    name='auth_password_reset_confirm'),
    #path('password/reset/done/', django_auth_views.password_reset_done,
    #    {'template_name': 'password_reset_done.html'},
    #    name='password_reset_done'),
    #path('username/recover/', django_auth_views.password_reset,
    #    {'password_reset_form': RecoverUserForm,
    #     'template_name': 'recover_user.html',
    #     'email_template_name': 'mails/recover_user_email.html',
    #     'subject_template_name': 'mails/recover_user_subject.html',
    #     'post_reset_redirect': 'common_recover_user_requested', },
    #    name='recover_user'),
    path('login/', django_auth_views.LoginView.as_view(template_name='old_login.html'), name='auth_login'),
    path('logout/', custom_logout_view , name='auth_logout'),
    #path('logout/', django_auth_views.LogoutView.as_view(next_page='/'), name='auth_logout'),
    path('password/change/', django_auth_views.PasswordChangeView.as_view(
        template_name='password_change.html',
        success_url='common_password_change_done',
        form_class=ChangePasswordForm
    ), name='auth_password_change'),

    path(
        'password/reset/<uidb64>/<token>/',
        django_auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='custom_password_reset_complete',
        ),
        name='password_reset_confirm'
    ),

    path(
        'password/reset/done/',
        django_auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'username/recover/',
        django_auth_views.PasswordResetView.as_view(
            template_name='recover_user.html',
            email_template_name='mails/recover_user_email.html',
            subject_template_name='mails/recover_user_subject.html',
            form_class=RecoverUserForm,
            success_url=reverse_lazy('common_recover_user_requested')
        ),
        name='recover_user'
    ),
    # Common - common.views.py
    path('login/social/<str:social_code>/', common_views.social_login, name="social_login"),
    path('login/social/<str:social_code>/<int:vacancy_id>/', common_views.social_login, name="social_login"),
    path('login/social/<str:social_code>/<int:vacancy_id>/<int:recruiter_id>/', common_views.social_login, name="social_login"),
    path('redirect/', common_views.redirect_after_login, name='common_redirect_after_login'),
    path('signup/completed/', common_views.registration_complete, name='common_registration_complete'),
    path('email/change/', common_views.email_change, name='common_email_change'),
    path('email/changerequested/', common_views.email_change_requested, name='common_email_change_requested'),
    path('email/verify/<str:token>/<str:code>/', common_views.email_change_approve,
        name='common_email_change_approve'),
    path('activate/<str:activation_key>/', common_views.registration_activate, name='common_registration_activate'),
    #path('password/changed/', common_views.password_change_done, name='common_password_change_done'),
    path('password/change/done/', common_views.password_change_done, name='common_password_change_done'),
    path('password/reset/completed/', common_views.custom_password_reset_complete, name='custom_password_reset_complete'),
    path('username/recover/requested/', common_views.recover_user_requested, name='common_recover_user_requested'),
    # url(r'^contactus/$', common_views.ContactFormView.as_view(), name='common_contact_form'),
    # url(r'^sent/$', TemplateView.as_view(template_name='contact_form_sent.html'), name='common_contact_form_sent'),
    # url(r'^register_email/$', common_views.register_blank_email, name='common_register_blank_email'),

    # Common Ajax - common.ajax.py
    path('ajax/login/', common_ajax_views.ajax_login, name='ajax_login'),
    path('ajax/companies-change-academic-area/', common_ajax_views.companies_change_academic_area),
    path('ajax/companies-allow-career/', common_ajax_views.companies_allow_career),
    # url(r'^ajax/companies-change-state/$', common_ajax_views.companies_change_state),
    path('ajax/candidates-change-degree/', common_ajax_views.candidates_change_degree),
    # url(r'^ajax/candidates-change-career/$', common_ajax_views.candidates_change_career),
    path('ajax/candidates-change-academic-status/', common_ajax_views.candidates_change_academic_status),
    # url(r'^ajax/get-company-areas/$', common_ajax_views.get_company_areas),
    path('ajax/vacancies-postulate/', common_ajax_views.vacancies_postulate),
    # url(r'^ajax/get-municipals/$', common_ajax_views.get_municipals),
    # url(r'^ajax/get-common-areas/$', common_ajax_views.get_common_areas),
    path('ajax/get-salarytype-codename/', common_ajax_views.get_salarytype_codename),
    path('ajax/vacancies-answer-question/', common_ajax_views.vacancies_answer_question),
    path('ajax/mark-vacancy-asfavorite/', common_ajax_views.mark_unmark_vacancy_as_favorite),
    path('ajax/addstage/', common_ajax_views.add_stage),
    path('ajax/validate_personal_form/',common_ajax_views.validate_personal_form),
    path('ajax/validate_contact_form/',common_ajax_views.validate_contact_form),
    path('ajax/validate_academic_form/',common_ajax_views.validate_academic_form),
    path('ajax/validate_experience_form/',common_ajax_views.validate_experience_form),
    path('ajax/validate_training_form/',common_ajax_views.validate_training_form),
    path('ajax/validate_project_form/',common_ajax_views.validate_project_form),
    path('ajax/validate_certificate_form/',common_ajax_views.validate_certificate_form),
    path('ajax/validate_objective_form/',common_ajax_views.validate_objective_form),
    path('ajax/validate_interests_form/',common_ajax_views.validate_interests_form),
    path('ajax/validate_hobbies_form/',common_ajax_views.validate_hobbies_form),
    path('ajax/validate_extra_curriculars_form/',common_ajax_views.validate_extra_curriculars_form),
    path('ajax/validate_others_form/',common_ajax_views.validate_others_form),
    path('ajax/validate_language_form/',common_ajax_views.validate_language_form),
    path('ajax/updatevacancystage/', common_ajax_views.update_vacancy_stage),
    path('ajax/upgradepostulate/', common_ajax_views.upgrade_postulate),
    path('ajax/downgradepostulate/', common_ajax_views.downgrade_postulate),
    path('ajax/archivepostulate/', common_ajax_views.archive_postulate),
    path('ajax/delete_section/',common_ajax_views.delete_section),
    path('ajax/publicapplication/', common_ajax_views.public_application),
    path('ajax/updatepermissions/', common_ajax_views.update_permissions),
    path('ajax/removemember/', common_ajax_views.remove_member),
    path('ajax/changeownership/', common_ajax_views.change_ownership),
    path('ajax/addmembertojob/', common_ajax_views.add_member_to_job),
    path('ajax/removememberfromjob/', common_ajax_views.remove_member_from_job),
    path('ajax/addmembertojobprocess/', common_ajax_views.add_member_to_job_process),
    path('ajax/removememberfromjobprocess/', common_ajax_views.remove_member_from_job_process),
    path('ajax/updatecriteria/', common_ajax_views.update_criteria),
    path('ajax/comment/', common_ajax_views.comment),
    path('ajax/comment/retrieveall/', common_ajax_views.retreive_comments),
    path('ajax/rate/', common_ajax_views.rate),
    path('ajax/spot/', common_ajax_views.spot),
    path('ajax/rate/retrieveall/', common_ajax_views.retreive_ratings),
    path('ajax/tag/', common_ajax_views.tag),
    path('ajax/get-schedule/', common_ajax_views.get_upcoming_schedule),
    path('ajax/schedule/', common_ajax_views.schedule),
    path('ajax/remove-schedule/', common_ajax_views.remove_schedule),
    path('ajax/withdraw/', common_ajax_views.withdraw),
    path('ajax/filter-candidates/', common_ajax_views.filter_candidates),
    path('ajax/post/', common_ajax_views.post_message_to_stream),
    path('ajax/mark_as_read/', common_ajax_views.mark_as_read),
    path('ajax/set_plan/', common_ajax_views.set_plan),
    path('ajax/verify_code/', common_ajax_views.verify_code),
    path('ajax/update_recurring/', common_ajax_views.update_recurring),
    path('ajax/renew_now/', common_ajax_views.renew_now),
    path('ajax/smart-share/<int:id>/', common_ajax_views.smart_share),
    path('ajax/socialshare/', common_ajax_views.socialshare),
    path('ajax/revokesocial/<str:social_code>/', common_ajax_views.revoke_social_auth),
    path('ajax/template/', common_ajax_views.custom_template),
    path('ajax/template-form/', common_ajax_views.template_form),
    path('ajax/get-candidate-form-data/', common_ajax_views.template_form_data),
    path('ajax/updatesitetemplate/', common_ajax_views.update_site_template),
    path('ajax/save_template/', common_ajax_views.save_template),
    path('ajax/get_evaluators/', common_ajax_views.get_evaluators),
    path('ajax/get_process_criterias/', common_ajax_views.get_process_criterias),
    path('ajax/template/', common_ajax_views.custom_template),
    path('ajax/template-form/', common_ajax_views.template_form),
    path('ajax/get-candidate-form-data/', common_ajax_views.template_form_data),
    path('ajax/resolve_conflicts_delete/', common_ajax_views.resolve_conflicts_delete),
    path('ajax/resolve_conflicts_unconflict/', common_ajax_views.resolve_conflicts_unconflict),
    path('ajax/resolve_conflicts_merge/', common_ajax_views.resolve_conflicts_merge),
    path('ajax/add_external_referal/', common_ajax_views.add_external_referal),
    path('ajax/remove_external_referal/', common_ajax_views.remove_external_referal),

    # Companies - companies.views.py
    path('signup/employer/', companies_views.record_recruiter, name='companies_record_recruiter'),
    path('signup/employer/<str:token>/', companies_views.record_recruiter, name='companies_recruiter_invitation'),
    path('profile/company/create/', companies_views.record_company, name='companies_record_company'),
    path('profile/employer/', companies_views.recruiter_profile, name='companies_recruiter_profile'),
    path('profile/company/', companies_views.company_profile, name='companies_company_profile'),
    path('careerssite/editor/', companies_views.template_editor, name="companies_edit_template"),
    path('careerssite/get_site_template/', companies_views.get_site_template, name="companies_get_site_template"),
    path('careerssite/preview/<int:template_id>/', companies_views.site_template_preview, name="companies_site_template_preview"),
    path('careerssite/<str:setting>/', companies_views.site_management, name='companies_site_management'),
    path('team/', companies_views.team_space, name = 'companies_company_team_space'),
    path('billing/', companies_views.billing, name = 'companies_billing'),
    path('payment/', payments_views.payment, name = 'companies_payment'),
    path('checkout/', payments_views.checkout, name = 'payments_checkout'),
    # url(r'^profile/company/change/$', companies_views.edit_company, name='companies_edit_company'),
    # url(r'^summary/jobs/$', companies_views.vacancies_summary, name='companies_vacancies_summary'),
    path('job/edit/', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    path('job/edit/<int:vacancy_id>/', companies_views.add_update_vacancy, name='companies_add_update_vacancy'),
    path('job/edit_hiring_process/<int:vacancy_id>/', companies_views.add_update_vacancy_hiring_process, name='companies_add_update_vacancy_hiring_process'),
    path('job/edit_talent_sourcing/<int:vacancy_id>/', companies_views.add_update_vacancy_talent_sourcing, name='companies_add_update_vacancy_talent_sourcing'),
    path('Finalizevacancy/<int:vacancy_id>/<str:message>/', companies_views.finalize_vacancy, name='companies_finalize_vacancy'),
    # url(r'^Removevacancy/(?P<vacancy_id>\d+)/$', companies_views.remove_vacancy, name='companies_remove_vacancy'),
    path('Publishvacancy/<int:vacancy_id>/', companies_views.publish_vacancy, name='companies_publish_vacancy'),
    path('UnPublishvacancy/<int:vacancy_id>/', companies_views.unpublish_vacancy, name='companies_unpublish_vacancy'),
    # url(r'^apply/job/(?P<vacancy_id>\d+)/$', companies_views.applications_for_vacancy,
    #     name='companies_applications_for_vacancy'),
    # url(r'^curricula/$', companies_views.first_search_curricula, name='companies_first_search_curricula'),
    # url(r'^search/curricula/$', companies_views.search_curricula, name='companies_search_curricula'),
    path('profile/candidate/<int:candidate_id>/', companies_views.curriculum_detail, name='companies_curriculum_detail'),
    path('profile/candidate/<int:candidate_id>/<int:vacancy_id>/', companies_views.curriculum_detail,
        name='companies_curriculum_detail'),
    # url(r'^public/candidate/(?P<candidate_id>\d+)/(?P<vacancy_id>\d+)/$', companies_views.public_curriculum_detail,
        # name='companies_public_curriculum_detail'),
    # url(r'^profile/discard/candidate/(?P<vacancy_id>\d+)/(?P<candidate_id>\d+)/$', companies_views.discard_candidate,
        # name='companies_discard_candidate'),
    # url(r'^recommendations/$', companies_views.company_recommendations, name='companies_company_recommendations'),
    # url(r'^money/$', companies_views.company_wallet, name='companies_company_wallet'),

    # TRM - TRM.views.py
    # url(r'^companies/$', TRM_views.companies, name='TRM_companies'),
    path('privacypolicy/', TRM_views.privacy_policy, name='TRM_privacy_policy'),
    path('termsandconditions/', TRM_views.terms_and_conditions, name='TRM_terms_and_conditions'),
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
    path('jobs/<int:vacancy_id>/', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details'),
    path('jobs/<int:vacancy_id>/ref-<str:referer>/', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_referal'),
    path('jobs/<int:vacancy_id>/eref-<str:external_referer>/', vacancy_views.vacancy_details, name='vacancies_get_vacancy_details_with_external_referal'),
    path('jobs/<int:vacancy_id>/apply/', vacancy_views.public_apply, name='vacancies_public_apply'),
    path('jobs/<int:vacancy_id>/apply/ref-<str:referer>/', vacancy_views.public_apply, name='vacancies_public_apply_with_referal'),
    path('jobs/<int:vacancy_id>/apply/eref-<str:external_referer>/', vacancy_views.public_apply, name='vacancies_public_apply_with_external_referal'),
    path('jobs/<int:vacancy_id>/new_application/', vacancy_views.new_application, name='vacancies_new_application'),
    path('jobs/<int:vacancy_id>/new_application/resolve/<str:card_type>/', vacancy_views.new_application_resolve_conflicts, name='vacancies_new_application_resolve_conflicts'),
    path('jobs/<int:vacancy_id>/complete_application/', vacancy_views.complete_application, name='vacancies_complete_application'),
    path('jobs/<int:vacancy_id>/talent_sourcing/', vacancy_views.vacancy_talent_sourcing, name="vacancies_talent_sourcing"),
    path('jobs/<int:vacancy_id>/process/<int:vacancy_stage>/', vacancy_views.vacancy_stage_details, name='vacancies_get_vacancy_stage_details'),
    path('jobs/<int:vacancy_id>/process/<int:vacancy_stage>/<int:stage_section>/', vacancy_views.vacancy_stage_details, name='vacancies_get_vacancy_stage_details'),
    path('jobs/<int:vacancy_id>/social/<str:social_code>/', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    path('jobs/<int:vacancy_id>/<str:social_code>/', vacancy_views.vacancy_details, name='social_verification'),
    # url(r'^jobs/(?P<vacancy_id>\d+)/social/(?P<social_code>\w+)/(?P<social_auth_id>\d+)/$', vacancy_views.vacancy_details, name='vacancies_apply_via_social'),
    # url(r'^jobs/company/(?P<company_id>\d+)/$', vacancy_views.vacancies_by_company, name='vacancies_vacancies_by_company'),
    # url(r'^jobs/create/$', vacancy_views.create_vacancies, name='vacancies_create_vacancies'),
    path('jobs/pdf/<int:vacancy_id>/', vacancy_views.vacancy_to_pdf, name='vacancies_vacancy_to_pdf'),

    #Social Multi Share views
    # url(r'^job/share/(?P<vacancy_id>\d+)/$', socialmultishare_views.share_to_social_media, name='socialmultishare_share_to_social_media'),
    # url(r'^twitter_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_twitter, name='socialmultishare_connect_to_twitter'),
    # url(r'^facebook_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_facebook, name='socialmultishare_connect_to_facebook'),
    # url(r'^linkedin_connect/(?P<vacancy_id>\d+)/$', socialmultishare_views.connect_to_linkedin, name='socialmultishare_connect_to_linkedin'),

    # Google Verification
    # url(r'^google279fe40bd6505938\.html$',
    #  lambda r: HttpResponse("google-site-verification: google279fe40bd6505938.html", content_type="text/plain")),

    # Includes
    path('i18n/', include('django.conf.urls.i18n')),
    path('ajax-uploads/', include('upload_logos.urls')),
    # path('rosetta/', include('rosetta.urls')),
    path('ckeditor/', include('ckeditor.urls')),
    # path('', include('social.apps.django_app.urls', namespace='social')),  # Auth con face, google, twitter
    # path('', include('django.contrib.auth.urls', namespace='auth')),  # Auth con face, google, twitter
    path('upload/file/', upload_vacancy_file, name='upload-file'),
    path('delete/file/', delete_vacancy_file, name='delete-file'),
    path('pricing-request/', common_ajax_views.pricing_request, name="pricing_request"),
    path('compare-candidates/', common_ajax_views.compare_candidates, name="compare_candidates"),
    path('notifications/', common_ajax_views.notifications, name="notifications"),
    re_path(r'^(?P<vacancy_status_name>\w+)/$', companies_views.vacancies_summary, name="companies_vacancies_by_status"),

    #Widget Urls
    path('widget/jobs/', companies_views.widget_jobs, name="companies_job_widget"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]