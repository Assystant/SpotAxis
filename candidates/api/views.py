from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from candidates.models import (
    Candidate, Expertise, Academic, CV_Language,
    Training, Certificate, Project, Curriculum
)
from candidates.serializers import (
    CandidateSerializer, ExpertiseSerializer, AcademicSerializer, 
    CVLanguageSerializer, TrainingSerializer, CertificateSerializer, 
    ProjectSerializer, CurriculumSerializer
)

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ExpertiseViewSet(viewsets.ModelViewSet):
    queryset = Expertise.objects.all()
    serializer_class = ExpertiseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AcademicViewSet(viewsets.ModelViewSet):
    queryset = Academic.objects.all()
    serializer_class = AcademicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CVLanguageViewSet(viewsets.ModelViewSet):
    queryset = CV_Language.objects.all()
    serializer_class = CVLanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
