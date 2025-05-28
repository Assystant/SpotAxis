from rest_framework import generics, permissions
from common.models import (
    Country, State, Municipal, Currency, Profile, User, AccountVerification,
    EmailVerification, Address, Degree, Identification_Doc, Marital_Status,
    Employment_Type, Gender, Subdomain, SocialAuth
)
from .serializers import (
    CountrySerializer, StateSerializer, MunicipalSerializer, CurrencySerializer,
    ProfileSerializer, UserSerializer, AccountVerificationSerializer, EmailVerificationSerializer,
    AddressSerializer, DegreeSerializer, IdentificationDocSerializer, MaritalStatusSerializer,
    EmploymentTypeSerializer, GenderSerializer, SubdomainSerializer, SocialAuthSerializer
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










