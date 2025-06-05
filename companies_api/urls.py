from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(r'recruiter', RecordRecruiterViewSet, basename='recruiter')
router.register(r'company', RecordCompanyViewSet, basename='company')
router.register(r'company-edit', EditCompanyViewSet, basename='company-edit')
router.register(r'recruiter-profile', RecruiterProfileViewSet, basename='recruiter-profile')
router.register(r'company-profile', CompanyProfileViewSet, basename='company-profile')
router.register(r'site-management', SiteManagementViewSet, basename='site-management')
router.register(r'team-space', TeamSpaceViewSet, basename='team-space')
router.register(r'vacancy-finalise', FinaliseVacancyViewSet, basename='vacancy-finalise')
router.register(r'vacancy', VacancyViewSet, basename='vacancy')
router.register(r'vacancy-publish', PublishVacancyViewSet, basename='vacancy-publish')
router.register(r'vacancy-unpublish', UnpublishVacancyViewSet, basename='vacancy-unpublish')
router.register(r'vacancy-applications', ApplicationsForVacancyViewSet, basename='vacancy-applications')
router.register(r'discard-candidate', DiscardCandidateViewSet, basename='discard-candidate')
router.register(r'curriculum-detail', CurriculumDetailViewSet, basename='curriculum-detail')
router.register(r'vacancy-summary', VacanciesSummaryViewSet, basename='vacancy-summary')
# router.register(r'vacancy-file-upload', UploadVacancyFileViewSet, basename='vacancy-file-upload')
# router.register(r'vacancy-file-delete', DeleteVacancyFileViewSet, basename='vacancy-file-delete')
router.register(r'vacancy-add-update', AddUpdateVacancyViewSet, basename='vacancy-add-update')
router.register(r'vacancy-hiring-process', AddUpdateVacancyHiringProcessViewSet, basename='vacancy-hiring-process')
router.register(r'vacancy-talent-sourcing', AddUpdateVacancyTalentSourcingViewSet, basename='vacancy-talent-sourcing')
router.register(r'company-recommendations', CompanyRecommendationsViewSet, basename='company-recommendations')
router.register(r'search-curricula', SearchCurriculaViewSet, basename='search-curricula')
router.register(r'company-wallet', CompanyWalletViewSet, basename='company-wallet')
router.register(r'widget-jobs', WidgetJobsViewSet, basename='widget-jobs')
# router.register(r'billing', BillingViewSet, basename='billing')
router.register(r'template-editor', TemplateEditorViewSet, basename='template-editor')
# router.register(r'template-preview', SiteTemplatePreviewViewSet, basename='template-preview')
router.register(r'site-template-info', GetSiteTemplateViewSet, basename='site-template-info')

urlpatterns = [
    path('', include(router.urls)),
    path('curricula/first-search/', FirstSearchCurriculaAPIView.as_view(), name='first-search-curricula'),
]
