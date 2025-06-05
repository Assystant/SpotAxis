from rest_framework.routers import DefaultRouter
# from candidates.views import (
#     CandidateViewSet, ExpertiseViewSet, AcademicViewSet,
#     CVLanguageViewSet, TrainingViewSet, CertificateViewSet,
#     ProjectViewSet, CurriculumViewSet
# )

router = DefaultRouter()
# router.register(r'candidates', CandidateViewSet)
# router.register(r'expertises', ExpertiseViewSet)
# router.register(r'academics', AcademicViewSet)
# router.register(r'languages', CVLanguageViewSet)
# router.register(r'trainings', TrainingViewSet)
# router.register(r'certificates', CertificateViewSet)
# router.register(r'projects', ProjectViewSet)
# router.register(r'curriculums', CurriculumViewSet)

urlpatterns = router.urls
