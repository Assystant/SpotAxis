from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.forms import CustomPasswordResetForm, RecoverUserForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
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


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("This email is already registered. Please try a new one."))
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Username already exists. Please try again."))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.is_active = False
        user.save()
        AccountVerification.objects.send_verification_mail(new_user=user)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def validate_old_password(self, value):
        if not self.user.check_password(value):
            raise serializers.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password1'])
        self.user.save()
        return self.user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError(_("There is no user registered with the specified email address."))
        return value

    def save(self):
        form = CustomPasswordResetForm(data=self.validated_data)
        if form.is_valid():
            form.save()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data['uid']).decode()
            self.user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(_("Invalid token for password reset."))

        if not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError(_("Invalid token for password reset."))

        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        return self.user


class UsernameRecoverSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError(_("There is no user registered with the specified email address."))
        return value

    def save(self):
        form = RecoverUserForm(data=self.validated_data)
        if form.is_valid():
            form.save()

