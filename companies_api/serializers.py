from rest_framework import serializers
from companies.models import (
    Company_Industry, Company, Recruiter, Ban, RecruiterInvitation, Wallet,
    Recommendation_Status, Recommendations, Stage, ExternalReferal
)


class CompanyIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_Industry
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = '__all__'


class BanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ban
        fields = '__all__'


class RecruiterInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterInvitation
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class RecommendationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation_Status
        fields = '__all__'


class RecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = '__all__'


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'


class ExternalReferalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalReferal
        fields = '__all__'