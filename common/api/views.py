from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from common.models import (
    Country, State, Municipal, Currency, Profile, User, AccountVerification,
    EmailVerification, Address, Degree, Identification_Doc, Marital_Status,
    Employment_Type, Gender, Subdomain, SocialAuth
)
from .serializers import (
    CountrySerializer, StateSerializer, MunicipalSerializer, CurrencySerializer,
    ProfileSerializer, UserSerializer, AccountVerificationSerializer, EmailVerificationSerializer,
    AddressSerializer, DegreeSerializer, IdentificationDocSerializer, MaritalStatusSerializer,
    EmploymentTypeSerializer, GenderSerializer, SubdomainSerializer, SocialAuthSerializer,
    SignUpSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, UsernameRecoverSerializer
)

class CountryList(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class StateList(generics.ListCreateAPIView):
    queryset= State.objects.all()
    serializer_class = StateSerializer


class StateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer


class MunicipalList(generics.ListCreateAPIView):
    queryset = Municipal.objects.all()
    serializer_class = MunicipalSerializer


class MunicipalDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Municipal.objects.all()
    serializer_class = MunicipalSerializer


class CurrencyList(generics.ListCreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class CurrencyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class AccountVerificationList(generics.ListCreateAPIView):
    queryset = AccountVerification.objects.all()
    serializer_class = AccountVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

class AccountVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountVerification.objects.all()
    serializer_class = AccountVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

class EmailVerificationList(generics.ListCreateAPIView):
    queryset = EmailVerification.objects.all()
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

class EmailVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailVerification.objects.all()
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.IsAdminUser]

class AddressList(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

class AddressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

class DegreeList(generics.ListCreateAPIView):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer
    permission_classes = [permissions.IsAdminUser]

class DegreeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer
    permission_classes = [permissions.IsAdminUser]

class IdentificationDocList(generics.ListCreateAPIView):
    queryset = Identification_Doc.objects.all()
    serializer_class = IdentificationDocSerializer
    permission_classes = [permissions.IsAdminUser]

class IdentificationDocDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Identification_Doc.objects.all()
    serializer_class = IdentificationDocSerializer
    permission_classes = [permissions.IsAdminUser]

class MaritalStatusList(generics.ListCreateAPIView):
    queryset = Marital_Status.objects.all()
    serializer_class = MaritalStatusSerializer
    permission_classes = [permissions.IsAdminUser]

class MaritalStatusDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Marital_Status.objects.all()
    serializer_class = MaritalStatusSerializer
    permission_classes = [permissions.IsAdminUser]

class EmploymentTypeList(generics.ListCreateAPIView):
    queryset = Employment_Type.objects.all()
    serializer_class = EmploymentTypeSerializer
    permission_classes = [permissions.IsAdminUser]

class EmploymentTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employment_Type.objects.all()
    serializer_class = EmploymentTypeSerializer
    permission_classes = [permissions.IsAdminUser]

class GenderList(generics.ListCreateAPIView):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer
    permission_classes = [permissions.IsAdminUser]

class GenderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer
    permission_classes = [permissions.IsAdminUser]

class SubdomainList(generics.ListCreateAPIView):
    queryset = Subdomain.objects.all()
    serializer_class = SubdomainSerializer
    permission_classes = [permissions.IsAdminUser]

class SubdomainDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subdomain.objects.all()
    serializer_class = SubdomainSerializer
    permission_classes = [permissions.IsAdminUser]

class SocialAuthList(generics.ListCreateAPIView):
    queryset = SocialAuth.objects.all()
    serializer_class = SocialAuthSerializer
    permission_classes = [permissions.IsAdminUser]

class SocialAuthDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SocialAuth.objects.all()
    serializer_class = SocialAuthSerializer
    permission_classes = [permissions.IsAdminUser]


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'signup':
            return SignUpSerializer
        elif self.action == 'password_change':
            return PasswordChangeSerializer
        elif self.action == 'password_reset':
            return PasswordResetSerializer
        elif self.action == 'password_reset_confirm':
            return PasswordResetConfirmSerializer
        elif self.action == 'username_recover':
            return UsernameRecoverSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Verification email has been sent.")}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='verify/(?P<activation_key>[^/.]+)')
    def verify(self, request, activation_key):
        user = AccountVerification.objects.activate_user(activation_key)
        if user:
            return Response({'detail': _('Account activated successfully.')})
        else:
            return Response({'detail': _('Invalid activation key.')}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been changed successfully.")})

    @action(detail=False, methods=['post'])
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password reset e-mail has been sent.")})

    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been reset successfully.")})

    @action(detail=False, methods=['post'])
    def username_recover(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Username recovery e-mail has been sent.")})