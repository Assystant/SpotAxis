from rest_framework import serializers
from candidates.models import (
    Candidate, Expertise, Academic, CV_Language,
    Training, Certificate, Project, Curriculum
)

# Candidate Serializer
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'


# Expertise Serializer
class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = '__all__'


# Academic Serializer
class AcademicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Academic
        fields = '__all__'


# CV Language Serializer
class CVLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV_Language
        fields = '__all__'


# Training Serializer
class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'


# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'


# Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


# Curriculum Serializer
class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = '__all__'


