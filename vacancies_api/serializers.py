from rest_framework import serializers
from vacancies.models import (
    Vacancy_Status, PubDate_Search, Employment_Experience, Salary_Type, Vacancy, Publish_History, Question, Candidate_Fav, Vacancy_Files, 
    VacancyStage, StageCriterion, VacancyTags, Medium, Postulate, 
    Comment, Postulate_Score, Postulate_Stage
)

class VacancyStatusSerializer(serializers.ModelSerializer):
    vacancy_count = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy_Status
        fields = ['id', 'name', 'codename', 'public', 'vacancy_count']

    def get_vacancy_count(self, obj):
        return obj.count()
    

class PubDateSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PubDate_Search
        fields = ['id', 'name', 'days', 'codename']

class EmploymentExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment_Experience
        fields = ['id', 'name', 'codename', 'order']


class SalaryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary_Type
        fields = ['id', 'name', 'codename', 'order']

class VacancySerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    age_preference = serializers.SerializerMethodField()
    employment_experience = serializers.SerializerMethodField()
    skills_as_list = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    application_url = serializers.SerializerMethodField()
    tag_cloud_html = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = '__all__'

    def get_location(self, obj):
        return obj.location()

    def get_age_preference(self, obj):
        return obj.age_preference()

    def get_employment_experience(self, obj):
        return obj.employment_experience()

    def get_skills_as_list(self, obj):
        return obj.skills_as_list()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_application_url(self, obj):
        return obj.get_application_url()

    def get_tag_cloud_html(self, obj):
        return obj.get_tag_cloud_html()

class PublishHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Publish_History
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class CandidateFavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate_Fav
        fields = '__all__'

class VacancyFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy_Files
        fields = '__all__'

class VacancyStageSerializer(serializers.ModelSerializer):
    criteria_as_list = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = VacancyStage
        fields = '__all__'

    def get_criteria_as_list(self, obj):
        return obj.criteria_as_list()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

class StageCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageCriterion
        fields = '__all__'

class VacancyTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyTags
        fields = '__all__'

class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = '__all__'

class PostulateSerializer(serializers.ModelSerializer):
    last_status = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    avg_score = serializers.SerializerMethodField()
    avg_stars = serializers.SerializerMethodField()
    file_content = serializers.SerializerMethodField()
    file_text = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    fileext = serializers.SerializerMethodField()
    timeline = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Postulate
        fields = '__all__'

    def get_last_status(self, obj):
        return obj.last_status()

    def get_full_name(self, obj):
        return obj.full_name()

    def get_avg_score(self, obj):
        return obj.avg_score()

    def get_avg_stars(self, obj):
        return obj.avg_stars()

    def get_file_content(self, obj):
        return obj.file_content()

    def get_file_text(self, obj):
        return obj.file_text()

    def get_filename(self, obj):
        return obj.filename()

    def get_fileext(self, obj):
        return obj.fileext()

    def get_timeline(self, obj):
        return [str(c) for c in obj.timeline()]

    def get_comments(self, obj):
        return [str(c) for c in obj.comments()]


class CommentSerializer(serializers.ModelSerializer):
    avg_score = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_avg_score(self, obj):
        return obj.avg_score()

class PostulateScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postulate_Score
        fields = '__all__'

class PostulateStageSerializer(serializers.ModelSerializer):
    avg_score = serializers.SerializerMethodField()

    class Meta:
        model = Postulate_Stage
        fields = '__all__'

    def get_avg_score(self, obj):
        return obj.avg_score()