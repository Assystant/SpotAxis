from rest_framework import serializers
from common.models import (
    Country, State, Municipal, Currency, Profile, User, AccountVerification,
    EmailVerification, Address, Degree, Identification_Doc, Marital_Status,
    Employment_Type, Gender, Subdomain, SocialAuth
)

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class MunicipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipal
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile', 
                 'phone', 'phone_ext', 'cellphone', 'photo', 'logued_by', 'date_joined')
        read_only_fields = ('date_joined',)


class AccountVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountVerification
        fields = '__all__'
        read_only_fields = ('activation_key',)


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = '__all__'
        read_only_fields = ('token', 'code', 'expiration_date')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('last_modified',)


class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'


class IdentificationDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Identification_Doc
        fields = '__all__'


class MaritalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marital_Status
        fields = '__all__'


class EmploymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment_Type
        fields = '__all__'


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'


class SubdomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdomain
        fields = '__all__'


class SocialAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAuth
        fields = '__all__'
        read_only_fields = ('oauth_token', 'oauth_secret', 'identifier')


