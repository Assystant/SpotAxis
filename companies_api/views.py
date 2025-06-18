from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.pagination import PageNumberPagination
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.db import transaction
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from decimal import Decimal
from hashids import Hashids
from datetime import date, timedelta
import traceback

from companies.models import *
from .serializers import *
from payments.models import *
# from payments_api.models import BillingSerializer
from candidates.models import *
from candidates.api.serializers import CandidateSerializer, CurriculumSerializer, ExpertiseSerializer, AcademicSerializer, CVLanguageSerializer, TrainingSerializer, ProjectSerializer, CertificateSerializer  
from vacancies_api.serializers import VacancySerializer, PostulateSerializer, VacancyStageSerializer
# VacancyFileSerializer
from common import registration_settings
from common.forms import AdressForm, UserDataForm, BasicUserDataForm, send_TRM_email, UserPhotoForm, SubdomainForm
from common.models import Profile, Country, send_email_to_TRM, Gender, Subdomain, State
from companies.forms import CompanyForm, SearchCvForm, CompanyLogoForm, MemberInviteForm
from activities.utils import post_notification, post_org_notification, post_activity
from candidates.models import Country
from common.forms import UserDataForm
from customField.forms import TemplateForm, FieldFormset
from TRM.context_processors import subdomain
from TRM.settings import SITE_URL, num_pages, number_objects_page, DEFAULT_SITE_TEMPLATE, STATIC_URL
from vacancies.forms import VacancyForm, VacancyFileForm, Public_FilesForm
from vacancies.models import Vacancy, Vacancy_Status, Postulate, Vacancy_Files, VacancyStage
from vacancies.response import JSONResponse, response_mimetype
from vacancies.serialize import serialize
from vacancies.views import save_public_application

regex = re.compile('[^A-Za-z0-9]')
subdomain_hash = Hashids(salt='TRM Subdomain',min_length=4)
invite_hash = Hashids(salt='Invitation',min_length=7)

class RecordRecruiterViewSet(viewsets.ModelViewSet):
    queryset = Recruiter.objects.all()
    serializer_class = RecruiterSerializer

    @action(detail=False, methods=['post'], url_path='record', url_name='record')
    def record_recruiter(self, request):
        if request.user.is_authenticated:
            raise Http404

        token = request.query_params.get('token')
        invitation = None
        form_user = UserDataForm(data=request.data, files=request.FILES)

        try:
            country_selected = Country.objects.get(iso2_code__exact='IN')
        except Country.DoesNotExist:
            country_selected = None

        if form_user.is_valid():
            new_user = form_user.save()
            try:
                new_user.profile = Profile.objects.get(codename='recruiter')
                new_user.logued_by = 'EL'
                new_user.save()

                recruiter, created = Recruiter.objects.get_or_create(user=new_user, user__is_active=True)

                if token:
                    invitation = RecruiterInvitation.objects.get(token=token)
                    company = invitation.invited_by.recruiter.company.first()
                    recruiter.company.add(company)
                    recruiter.membership = invitation.membership
                    recruiter.save()
                    new_user.is_active = True
                    new_user.save()

                    post_notification(user=new_user, action="Welcome to SpotAxis!")
                    RecruiterInvitation.objects.filter(email=invitation.email).delete()
                    RecruiterInvitation.objects.filter(email=new_user.email).delete()
                else:
                    form_user.send_verification_mail(new_user)

                username = form_user.cleaned_data['username']
                password = form_user.cleaned_data['password']

                if registration_settings.AUTO_LOGIN or token:
                    if registration_settings.EMAIL_ONLY:
                        username = form_user.cleaned_data['email']
                    user = authenticate(username=username, password=password)
                    if user and user.is_active:
                        login(request, user)

                redirect_url = registration_settings.REGISTRATION_REDIRECT
                if token:
                    redirect_url = 'common_redirect_after_login'

                return Response({'success': True, 'redirect_url': redirect_url}, status=status.HTTP_201_CREATED)

            except Exception as e:
                traceback.print_exc()
                new_user.delete()
                raise Http404

        else:
            errors = form_user.errors
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


class RecordCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=False, methods=['post'], url_path='record', url_name='record')
    def record_company(self, request):
        try:
            recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
        except Recruiter.DoesNotExist:
            raise Http404

        if recruiter.company.exists():
            return Response({'redirect': 'companies_company_profile'}, status=status.HTTP_302_FOUND)

        try:
            country_selected = Country.objects.get(id=request.data.get('country'))
        except:
            country_selected = None

        try:
            industry_id = request.data.get('industry')
            industry_selected = Company_Industry.objects.get(id=industry_id) if int(industry_id) != 0 else None
        except:
            industry_selected = None

        form_company = CompanyForm(data=request.data,
                                   files=request.FILES,
                                   country_selected=country_selected,
                                   industry_selected=industry_selected)

        if form_company.is_valid():
            try:
                new_company = form_company.save(commit=False)
                new_company.user = request.user

                # Generate slug and subdomain
                brand_name = slugify(new_company.name).replace('-', '')
                brand_name = regex.sub(r'[^a-zA-Z0-9]', '', brand_name)
                slug = brand_name + subdomain_hash.encode(new_company.id)
                subdomain_obj = Subdomain.objects.create(slug=slug)
                new_company.subdomain = subdomain_obj

                # Set template and static pages
                template_id = DEFAULT_SITE_TEMPLATE
                new_company.site_template = template_id
                new_company.above_jobs = render_to_string(f'careers/base/t-{template_id}/above_jobs.html', {'STATIC_URL': STATIC_URL})
                new_company.below_jobs = render_to_string(f'careers/base/t-{template_id}/below_jobs.html', {'STATIC_URL': STATIC_URL})
                new_company.save()

                # Discounts
                discounts = Discount.objects.filter(available_to_signups=True)
                for discount in discounts:
                    Discount_Usage.objects.get_or_create(discount=discount, company=new_company)

                # Associate recruiter
                recruiter.company.add(new_company)
                recruiter.membership = 3
                recruiter.save()

                # Wallet and Subscription
                Wallet.objects.create(company=new_company, available=0)
                Subscription.objects.create(company=new_company, price_slab=PriceSlab.objects.get(id=2))

                # Candidate Stages
                Stage.objects.create(name="New Candidates", company=new_company)
                Stage.objects.create(name="Onboarding", company=new_company)

                request.session['first_time'] = True
                return Response({'success': True, 'redirect': new_company.geturl()}, status=status.HTTP_201_CREATED)

            except Exception as e:
                traceback.print_exc()
                new_company.delete()
                raise Http404

        return Response({'errors': form_company.errors}, status=status.HTTP_400_BAD_REQUEST)

class EditCompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=False, methods=['post'], url_path='edit', url_name='edit_company')
    def edit_company(self, request):
        user = request.user

        if not user.email:
            return Response({'redirect': 'common_register_blank_email'}, status=status.HTTP_302_FOUND)

        company = get_object_or_404(Company, user=user)
        address = company.address

        form_user = BasicUserDataForm(request.data, request.FILES, instance=user)

        try:
            country_selected = Country.objects.get(iso2_code__exact='MX')
        except:
            country_selected = None

        try:
            state_id = int(request.data.get('state', 0))
            state_selected = None if state_id == 0 else State.objects.get(id=state_id)
        except:
            state_selected = None

        form_address = AdressForm(
            request.data, request.FILES,
            instance=address,
            country_selected=country_selected,
            state_selected=state_selected
        )

        try:
            industry_selected = Company_Industry.objects.get(pk=int(request.data.get('industry')))
        except:
            industry_selected = None

        try:
            area_id = int(request.data.get('area', 0))
            area_selected = None if area_id == 0 else Company_Area.objects.get(id=area_id)
        except:
            area_selected = None

        form_company = CompanyForm(
            request.data, request.FILES,
            instance=company,
            area_selected=area_selected,
            industry_selected=industry_selected
        )

        if form_user.is_valid() and form_company.is_valid() and form_address.is_valid():
            user = form_user.save()

            address = form_address.save(commit=False)
            address.country = country_selected
            address.save()

            company = form_company.save(commit=False)
            company.address = address
            company.save()

            # Update subdomain slug
            brand_name = slugify(company.social_name).replace('-', '')
            brand_name = regex.sub(r'[^a-zA-Z0-9]', '', brand_name)
            slug = brand_name + subdomain_hash.encode(company.id)
            sub_domain = company.subdomain
            sub_domain.slug = slug
            sub_domain.save()

            # Send notifications
            post_org_notification(
                message_chunks=[{
                    'subject': "Company Profile",
                    'subject_action': '',
                    'action_url': company.get_absolute_url(),
                }],
                user=[r.user for r in Recruiter.admins.all()],
                actor=request.user,
                action="updated",
                subject="Company Profile",
                url=company.get_absolute_url()
            )

            return Response({
                'success': True,
                'message': _('We have modified the information successfully'),
                'redirect': 'companies_company_profile'
            }, status=status.HTTP_200_OK)

        return Response({
            'form_user_errors': form_user.errors,
            'form_address_errors': form_address.errors,
            'form_company_errors': form_company.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RecruiterProfileViewSet(viewsets.ModelViewSet):
    queryset = Recruiter.objects.all()
    serializer_class = RecruiterSerializer  # Define this if not already

    @action(detail=False, methods=['get', 'post'], url_path='profile', url_name='recruiter_profile')
    def recruiter_profile(self, request):
        user = request.user
        if not user.email:
            return Response({'redirect': 'common_register_blank_email'}, status=status.HTTP_302_FOUND)

        try:
            recruiter = Recruiter.objects.get(user=user, user__is_active=True)
        except Recruiter.DoesNotExist:
            return Response({'error': 'Recruiter not found.'}, status=status.HTTP_404_NOT_FOUND)

        context = {'success': False}

        if request.method == 'POST':
            form_user = BasicUserDataForm(data=request.data, files=request.FILES, instance=user)
            form_user_photo = UserPhotoForm(data=request.data, files=request.FILES, instance=user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if form_user.is_valid():
                    form_user.save()
                    context['success'] = True
                    context['msg'] = 'Profile Updated'
                    context['img'] = user.photo.url if user.photo else None
                else:
                    context['errors'] = form_user.errors
                return Response(context, status=status.HTTP_200_OK)
            else:
                if form_user_photo.is_valid():
                    form_user_photo.save()
                    messages.success(request, "Profile Image Updated.")
                else:
                    messages.error(request, "Image not updated.")

                return Response({'success': True, 'message': "Profile updated"}, status=status.HTTP_200_OK)

        else:
            form_user = BasicUserDataForm(instance=user)
            form_user_photo = UserPhotoForm(instance=user)
            # You can optionally serialize these if needed in frontend

            return Response({
                'isProfile': True,
                'user_id': user.id,
                'recruiter_id': recruiter.id,
                'recruiter_email': user.email,
                'companies': [c.name for c in recruiter.company.all()],
                'created': False
            }, status=status.HTTP_200_OK)

class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer  # Define appropriately

    @action(detail=False, methods=['get', 'post'], url_path='profile', url_name='company_profile')
    def company_profile(self, request):
        user = request.user
        if not user.email:
            return Response({'redirect': 'common_register_blank_email'}, status=status.HTTP_302_FOUND)

        subdomain_data = subdomain(request)
        if not subdomain_data.get('active_host'):
            return Response({'error': 'Invalid subdomain'}, status=status.HTTP_404_NOT_FOUND)

        company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
        context = {'success': False}
        recruiter = None

        if user.is_authenticated:
            try:
                recruiter = Recruiter.objects.get(user=user, company=company, user__is_active=True)
            except Recruiter.DoesNotExist:
                recruiter = None

        form_company = CompanyForm(instance=company)
        logo_form = CompanyLogoForm(instance=company)

        if request.method == 'POST' and recruiter and recruiter.is_admin():
            if request.data.get('isimage', '0') == '1':
                logo_form = CompanyLogoForm(data=request.data, files=request.FILES, instance=company)
                if logo_form.is_valid():
                    logo_form.save()
                    messages.success(request, "Logo Updated.")
                else:
                    context['errors'] = logo_form.errors
            else:
                form_company = CompanyForm(data=request.data, files=request.FILES, instance=company)
                if form_company.is_valid():
                    form_company.save()
                    company = recruiter.company.all()[0]

                    brand_name = slugify(company.name).replace('-', '')
                    brand_name = regex.sub('', brand_name)
                    slug = brand_name + subdomain_hash.encode(company.id)

                    sub_domain = company.subdomain
                    if sub_domain and sub_domain.slug != slug:
                        sub_domain.slug = slug
                        sub_domain.save()
                        if not sub_domain.cname:
                            company.refresh_from_db()
                            return Response({'redirect': company.get_absolute_url()}, status=status.HTTP_302_FOUND)

                    context.update({
                        'success': True,
                        'msg': 'Profile Updated',
                        'img': company.logo.url if company.logo else None
                    })
                else:
                    context['errors'] = form_company.errors

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return Response(context, status=status.HTTP_200_OK)

        # Fetch vacancies and stages
        vacancies = Vacancy.objects.filter(company=company)
        for vacancy in vacancies:
            vacancy.stages = VacancyStage.objects.filter(vacancy=vacancy)

        return Response({
            'user_id': user.id,
            'company_id': company.id,
            'recruiter_id': recruiter.id if recruiter else None,
            'vacancy_status': list(Vacancy_Status.objects.values()),
            'vacancies': [
                {
                    'id': v.id,
                    'title': v.title,
                    'stages': list(v.stages.values('id', 'name'))
                } for v in vacancies
            ],
            'created': False,
            'isCompanyProfile': True,
            'isProfile': True,
            'logo_url': company.logo.url if company.logo else None
        }, status=status.HTTP_200_OK)

class SiteManagementViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer  # your serializer

    @action(detail=False, methods=['get', 'post'], url_path='site-management', url_name='site_management')
    def site_management(self, request):
        user = request.user
        setting = request.query_params.get("setting", "template")

        if not user.email:
            return Response({'redirect': 'common_register_blank_email'}, status=status.HTTP_302_FOUND)

        try:
            recruiter = Recruiter.objects.get(user=user, user__is_active=True)
        except Recruiter.DoesNotExist:
            return Response({'detail': 'Recruiter not found'}, status=status.HTTP_404_NOT_FOUND)

        if not recruiter.is_admin():
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        company_qs = recruiter.company.all()
        if not company_qs.exists():
            return Response({'detail': 'No company found for recruiter'}, status=status.HTTP_404_NOT_FOUND)

        company = company_qs.first()
        sub_domain = company.subdomain
        context = {
            'user': user.id,
            'recruiter': recruiter.id,
            'company': company.id,
            'sub_domain': sub_domain.slug if sub_domain else None,
            'isCompanyManagement': True,
            'success': False
        }

        if setting == 'template':
            context['isTemplatePage'] = True

        elif setting == 'subdomain' and company.check_service('CSM_CNAME'):
            context['isSubdomainPage'] = True
            if request.method == 'POST':
                form_subdomain = SubdomainForm(instance=sub_domain, data=request.data, files=request.FILES)
                if form_subdomain.is_valid():
                    form_subdomain.save()
                    messages.success(request, 'The subdomain has been successfully updated')
                    context['success'] = True
                else:
                    context['errors'] = form_subdomain.errors
            else:
                form_subdomain = SubdomainForm(instance=sub_domain)
                context['form_subdomain'] = {
                    'slug': form_subdomain['slug'].value(),
                    'cname': form_subdomain['cname'].value(),
                }

        elif setting == 'embed' and company.check_service('CSM_JOBS_WIDGET'):
            context['isEmbedPage'] = True
            context['Embedurl'] = company.geturl() + reverse('companies_job_widget')

        else:
            return Response({'detail': 'Page not found or service not enabled'}, status=status.HTTP_404_NOT_FOUND)

        return Response(context, status=status.HTTP_200_OK)

class TeamSpaceViewSet(viewsets.ModelViewSet):
    queryset = RecruiterInvitation.objects.all()
    serializer_class = RecruiterInvitationSerializer

    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        return RecruiterInvitation.objects.filter(invited_by=recruiter.user)

    def create(self, request, *args, **kwargs):
        recruiter = get_object_or_404(Recruiter, user=request.user)
        company = recruiter.company.first()

        if not company or not company.check_service('CH_ADD_TEAM'):
            return Response({'detail': 'Not authorized or no company.'}, status=status.HTTP_403_FORBIDDEN)

        form = MemberInviteForm(data=request.data)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.invited_by = request.user
            invitation.membership = int(request.data.get('membershipoptions', 1))
            invitation.save()
            invitation.token = invite_hash.encode(invitation.id)
            invitation.save()

            RecruiterInvitation.objects.filter(
                invited_by__recruiter__company__in=recruiter.company.all(),
                email=invitation.email
            ).exclude(id=invitation.id).delete()

            url = company.geturl() + reverse('companies_recruiter_invitation', args=[invitation.token])
            context_email = {
                'invitation': invitation,
                'company': company,
                'href_url': url
            }
            send_TRM_email(
                subject_template_name='mails/recruiter_invitation_subject.html',
                email_template_name='mails/recruiter_invitation.html',
                context_email=context_email,
                to_user=invitation.email
            )

            return Response({'detail': 'Invitation sent successfully'}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class FinaliseVacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        return Vacancy.objects.filter(company__in=recruiter.company.all())

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        recruiter = get_object_or_404(Recruiter, user=request.user)
        company = recruiter.company.first()
        vacancy = get_object_or_404(Vacancy, pk=pk, company=company)

        message = request.data.get('message')
        reason_map = {
            '1': "Candidates Selection Complete",
            '2': "No Suitable Candidate Found",
            '3': "Job Opening is on hold"
        }

        if message not in reason_map:
            return Response({'detail': 'Invalid message code.'}, status=status.HTTP_400_BAD_REQUEST)

        closed_status = get_object_or_404(Vacancy_Status, codename='closed')
        vacancy.status = closed_status
        vacancy.end_date = date.today()
        vacancy.vacancy_reason = reason_map[message]
        vacancy.save()

        if not vacancy.expired:
            vacancy.unpublish()

        subscribers = list(set([
            r.user for r in vacancy.company.recruiter_set.exclude(user=request.user)
        ]))
        post_activity(
            message_chunks=[{
                'subject': str(vacancy.employment),
                'subject_action': '',
                'action_url': vacancy.get_absolute_url(),
            }],
            actor=request.user,
            action='closed job opening - ',
            subject=str(vacancy.employment),
            subscribers=subscribers,
            action_url=vacancy.get_absolute_url()
        )

        return Response({'detail': _('Job Opening for "%s" has been closed') % vacancy.employment})

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        # Limit vacancies to those belonging to the current user's company
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        company = recruiter.company.first()
        return Vacancy.objects.filter(company=company)

    @action(detail=True, methods=['post'], url_path='remove')
    def remove(self, request, pk=None):
        vacancy = self.get_object()

        closed_status = get_object_or_404(Vacancy_Status, codename='closed')
        vacancy.status = closed_status
        vacancy.end_date = date.today()
        vacancy.save()

        if not vacancy.expired:
            vacancy.unpublish()

        return Response(
            {"detail": _('Job Opening for "%s" has been closed') % vacancy.employment},
            status=status.HTTP_200_OK
        )

class PublishVacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        company = recruiter.company.first()
        return Vacancy.objects.filter(company=company)

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        vacancy = self.get_object()
        publish_period = request.data.get('publish_period', None)

        try:
            if vacancy.company.check_service('JM_DURATION') and publish_period:
                start_str, end_str = [s.strip() for s in publish_period.split('-')]
                start = datetime.strptime(start_str, "%m/%d/%Y").date()
                end = datetime.strptime(end_str, "%m/%d/%Y").date()

                if start < date.today():
                    return Response({"detail": "Bad Range"}, status=status.HTTP_400_BAD_REQUEST)

                if start == date.today():
                    vacancy.publish()
                    if not vacancy.hasbeenPublished:
                        vacancy.editing_date = date.today() + timedelta(days=5)
                    vacancy.pub_after = False
                else:
                    vacancy.pub_after = True
                    vacancy.pub_date = start

                if end and end > start:
                    vacancy.unpub_date = end

            else:
                vacancy.publish()
                if not vacancy.hasbeenPublished:
                    vacancy.editing_date = date.today() + timedelta(days=5)
                vacancy.pub_after = False

            vacancy.save()
            return Response({"detail": _("Successfully Published Job")}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UnpublishVacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        company = recruiter.company.first()
        return Vacancy.objects.filter(company=company)

    @action(detail=True, methods=['post'], url_path='unpublish')
    def unpublish(self, request, pk=None):
        try:
            company = request.user.recruiter.company.all()[0]
        except IndexError:
            raise Http404("Company not found for user recruiter")

        vacancy = get_object_or_404(Vacancy, pk=pk, company=company.pk)

        vacancy.unpublish()
        vacancy.pub_after = False
        vacancy.save()

        return Response(
            {"detail": _("Successfully UnPublished Job")},
            status=status.HTTP_200_OK
        )


class ApplicationsForVacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        company = recruiter.company.first()
        return Vacancy.objects.filter(company=company)

    @action(detail=True, methods=['get', 'post'], url_path='applications')
    def applications_for_vacancy(self, request, pk=None):
        # Get vacancy and validate ownership
        vacancy = get_object_or_404(Vacancy, pk=pk, company__recruiter__user=request.user)

        if request.method == 'POST':
            candidates_ids = request.data.get('candidates_ids', [])
            if not isinstance(candidates_ids, list):
                return Response({"detail": "candidates_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)

            for candidate_id in candidates_ids:
                candidate = get_object_or_404(Candidate, pk=candidate_id)
                postulate = get_object_or_404(Postulate, vacancy=vacancy, candidate=candidate)
                postulate.discard = True
                postulate.save()
            
            # Update vacancy applications count (recalculate)
            vacancy.applications = Postulate.objects.filter(vacancy=vacancy, discard=False).count()
            vacancy.save()

            return Response({"detail": "Candidates discarded successfully"}, status=status.HTTP_200_OK)

        # GET method - list applications not discarded
        applications = Postulate.objects.filter(vacancy=vacancy, discard=False)
        # Optionally serialize with nested data or return simplified data
        serializer = PostulateSerializer(applications, many=True)

        return Response({
            'vacancy': VacancySerializer(vacancy).data,
            'applications': serializer.data,
            'today': now().date(),
        })

class DiscardCandidateViewSet(viewsets.ModelViewSet):
    queryset = Postulate.objects.all()
    serializer_class = RecommendationsSerializer

    @action(detail=False, methods=['post'], url_path='discard/(?P<vacancy_id>[^/.]+)/(?P<candidate_id>[^/.]+)')
    def discard_candidate(self, request, vacancy_id=None, candidate_id=None):
        # Verify vacancy belongs to request.user
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id, user=request.user)
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        postulate = get_object_or_404(Postulate, vacancy=vacancy, candidate=candidate)

        postulate.discard = True
        postulate.save()

        # Update vacancy applications count (better to count non-discarded postulates)
        vacancy.applications = Postulate.objects.filter(vacancy=vacancy, discard=False).count()
        vacancy.save()

        return Response(
            {"detail": f"Candidate {candidate_id} discarded from vacancy {vacancy_id}."},
            status=status.HTTP_200_OK
        )

class CurriculumDetailViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    serializer_class = CandidateSerializer  # Base serializer, will customize response

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Override retrieve to accept candidate_id and vacancy_id from URL or query params
        and return extended details.
        """
        candidate_id = self.kwargs.get('candidate_id') or request.query_params.get('candidate_id')
        vacancy_id = self.kwargs.get('vacancy_id') or request.query_params.get('vacancy_id')

        if not candidate_id or not vacancy_id:
            return Response({"detail": "candidate_id and vacancy_id are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(Candidate, pk=candidate_id)
        try:
            recruiter = Recruiter.objects.get(user=request.user)
        except Recruiter.DoesNotExist:
            raise Http404("Recruiter not found")

        vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company__in=recruiter.company.all())
        postulate = get_object_or_404(Postulate, candidate=candidate, vacancy=vacancy)

        # Mark as seen if not yet
        if not postulate.seen:
            postulate.seen = True
            postulate.save()
            # Email sending logic can be added here asynchronously if needed

        # Fetch related objects
        expertises = Expertise.objects.filter(candidate=candidate)
        academics = Academic.objects.filter(candidate=candidate)
        languages = CV_Language.objects.filter(candidate=candidate)
        trainings = Training.objects.filter(candidate=candidate)
        projects = Project.objects.filter(candidate=candidate)
        certificates = Certificate.objects.filter(candidate=candidate)
        curriculum = get_object_or_404(Curriculum, candidate=candidate)

        # Serialize everything
        data = {
            "candidate": CandidateSerializer(candidate).data,
            "vacancy": VacancySerializer(vacancy).data,
            "postulate": PostulateSerializer(postulate).data,
            "curriculum": CurriculumSerializer(curriculum).data,
            "expertises": ExpertiseSerializer(expertises, many=True).data,
            "academics": AcademicSerializer(academics, many=True).data,
            "languages": CVLanguageSerializer(languages, many=True).data,
            "trainings": TrainingSerializer(trainings, many=True).data,
            "projects": ProjectSerializer(projects, many=True).data,
            "certificates": CertificateSerializer(certificates, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)


class VacanciesSummaryViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        user = self.request.user
        vacancy_status_name = self.request.query_params.get('vacancy_status_name')
        subdomain_data = subdomain(self.request)
        if not subdomain_data.get('active_subdomain'):
            raise Http404

        try:
            company = Company.objects.get(subdomain__slug=subdomain_data['active_subdomain'])
        except Company.DoesNotExist:
            raise Http404

        recruiter = None
        if user.is_authenticated and hasattr(user, 'profile') and user.profile.codename == 'recruiter':
            try:
                recruiter = Recruiter.objects.get(user=user, user__is_active=True)
            except Recruiter.DoesNotExist:
                return Vacancy.objects.none()

        # Check vacancy_status filter
        if vacancy_status_name and not recruiter:
            raise Http404

        if recruiter and company in recruiter.company.all():
            # Recruiter filtering by status
            if vacancy_status_name == 'open':
                return Vacancy.openjobs.filter(company=company)
            elif vacancy_status_name == 'closed':
                return Vacancy.closedjobs.filter(company=company)
            else:
                return Vacancy.objects.none()
        else:
            return Vacancy.publishedjobs.filter(company=company)

    def list(self, request, *args, **kwargs):
        vacancies = self.get_queryset()
        # Add stages to each vacancy for serialization
        for vacancy in vacancies:
            vacancy.stages = VacancyStage.objects.filter(vacancy=vacancy)
        serializer = self.get_serializer(vacancies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='save-public-application')
    def save_public_application(self, request):
        user = request.user
        vacancy_id = request.data.get('vacancy')
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({"detail": "Vacancy not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recruiter = Recruiter.objects.get(user=user)
        except Recruiter.DoesNotExist:
            return Response({"detail": "Recruiter not found."}, status=status.HTTP_403_FORBIDDEN)

        # You might want to replace this with a serializer instead of a form
        public_form = Public_FilesForm(request.data, request.FILES)
        if public_form.is_valid():
            public_form.save(vacancy=vacancy, recruiter=recruiter)
            return Response({"detail": "Application saved."})
        else:
            return Response(public_form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='invite-member')
    def invite_member(self, request):
        user = request.user
        vacancy_status_name = request.query_params.get('vacancy_status_name')
        # Check permissions, recruiter status, etc.
        try:
            recruiter = Recruiter.objects.get(user=user)
            company = recruiter.company.first()
        except (Recruiter.DoesNotExist, IndexError):
            return Response({"detail": "Recruiter or company not found."}, status=status.HTTP_403_FORBIDDEN)

        if not company.check_service('CH_ADD_TEAM'):
            return Response({"detail": "Service not available."}, status=status.HTTP_403_FORBIDDEN)

        form_invite = MemberInviteForm(data=request.data)
        if form_invite.is_valid():
            invitation = form_invite.save(commit=False)
            invitation.token = invite_hash.encode(invitation.id)
            invitation.invited_by = user
            invitation.membership = int(request.data.get('membershipoptions', 1))
            invitation.save()

            # Delete old invitations with same email except this one
            RecruiterInvitation.objects.filter(
                invited_by__recruiter__company__in=recruiter.company.all(),
                email=invitation.email
            ).exclude(id=invitation.id).delete()

            # Optionally send email here...
            return Response({"detail": "Invitation sent."})
        else:
            return Response(form_invite.errors, status=status.HTTP_400_BAD_REQUEST)

# class UploadVacancyFileViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy_Files.objects.all()
#     serializer_class = VacancyFileSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     @action(detail=False, methods=['post'])
#     def upload(self, request, *args, **kwargs):
#         try:
#             # Form needs data + files
#             form = VacancyFileForm(data=request.data, files=request.FILES)

#             if request.FILES and request.FILES.getlist('file'):
#                 uploaded_files = len(request.FILES.getlist('file'))
#                 form.validate_number_files(uploaded_files)

#             if form.is_valid():
#                 vacancy = None
#                 vacancy_id = request.data.get('vacancy_id')
#                 if vacancy_id and int(vacancy_id) > 0:
#                     vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

#                 obj = form.save(vacancy=vacancy, random_number=request.session.get('random_number'))

#                 if vacancy:
#                     obj_files_count = Vacancy_Files.objects.filter(vacancy=vacancy).count()
#                 else:
#                     obj_files_count = Vacancy_Files.objects.filter(random_number=request.session.get('random_number')).count()

#                 # Use your serialize function to convert to dict/list for response
#                 files = [serialize(obj)]

#                 data = {'files': files, 'objFiles': obj_files_count}
#                 return Response(data)

#             else:
#                 errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
#                 return Response(errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             import traceback
#             tb = traceback.format_exc()
#             print(tb)
#             return Response({"detail": "Error uploading file."}, status=status.HTTP_400_BAD_REQUEST)

# class DeleteVacancyFileViewSet(viewsets.ModelViewSet):
#     queryset = Vacancy_Files.objects.all()
#     serializer_class = VacancyFileSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     @action(detail=False, methods=['post'])
#     def upload(self, request, *args, **kwargs):
#         try:
#             form = VacancyFileForm(data=request.data, files=request.FILES)
#             if request.FILES and request.FILES.getlist('file'):
#                 form.validate_number_files(len(request.FILES.getlist('file')))

#             if form.is_valid():
#                 vacancy = None
#                 vacancy_id = request.data.get('vacancy_id')
#                 if vacancy_id and int(vacancy_id) > 0:
#                     vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

#                 obj = form.save(vacancy=vacancy, random_number=request.session.get('random_number'))

#                 obj_files_count = Vacancy_Files.objects.filter(
#                     vacancy=vacancy if vacancy else None,
#                     random_number=None if vacancy else request.session.get('random_number')
#                 ).count()

#                 files = [serialize(obj)]

#                 return Response({'files': files, 'objFiles': obj_files_count})

#             else:
#                 errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
#                 return Response(errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return Response({"detail": "Error uploading file."}, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response(True)
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return Response({"detail": "Error deleting file."}, status=status.HTTP_400_BAD_REQUEST)

class AddUpdateVacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_queryset(self):
        # Limit vacancies to companies of recruiter logged in
        try:
            recruiter = Recruiter.objects.get(user=self.request.user, user__is_active=True)
        except Recruiter.DoesNotExist:
            return Vacancy.objects.none()
        return Vacancy.objects.filter(company__in=recruiter.company.all())

    def perform_create(self, serializer):
        recruiter = Recruiter.objects.get(user=self.request.user, user__is_active=True)
        company = recruiter.company.all()[0]

        # Set default fields
        vacancy = serializer.save(user=self.request.user, company=company)
        self._handle_post_save(vacancy)

    def perform_update(self, serializer):
        vacancy = serializer.save()
        self._handle_post_save(vacancy)

    def _handle_post_save(self, vacancy):
        # Create first and last stages if missing
        first_stage = Stage.objects.get(company=vacancy.company, name="New Candidates")
        last_stage = Stage.objects.get(company=vacancy.company, name="Onboarding")
        VacancyStage.objects.get_or_create(stage=first_stage, vacancy=vacancy, order=0, locked=True)
        VacancyStage.objects.get_or_create(stage=last_stage, vacancy=vacancy, order=100, locked=True)

        # Handle file moving & renaming if needed (You can implement this with signals or here)
        # This depends on your file upload strategy - you can extend here.

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # To handle file uploads alongside vacancy data
        files = request.FILES.getlist('file')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vacancy = serializer.save(user=request.user, company=request.user.recruiter.company.first())

        # Handle file uploads
        for f in files:
            Vacancy_Files.objects.create(file=f, vacancy=vacancy)

        self._handle_post_save(vacancy)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        files = request.FILES.getlist('file')
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        vacancy = serializer.save()

        for f in files:
            Vacancy_Files.objects.create(file=f, vacancy=vacancy)

        self._handle_post_save(vacancy)
        return Response(serializer.data)

class AddUpdateVacancyHiringProcessViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        # Check email exists
        if not request.user.email:
            return Response({"detail": "Email required"}, status=400)
        
        # Get subdomain info (implement this function accordingly)
        subdomain_data = subdomain(request)
        if not subdomain_data.get('active_subdomain'):
            raise NotFound("Subdomain not active")

        recruiter = get_object_or_404(Recruiter, user=request.user, user__is_active=True)
        if not recruiter.is_manager():
            raise PermissionDenied("Not a manager")
        
        # Verify company by subdomain
        company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
        if not company.check_service('JP_POST'):
            raise PermissionDenied("Service not available")
        
        vacancy = get_object_or_404(Vacancy, pk=pk, company__in=recruiter.company.all())
        vacancy_status = vacancy.status.codename
        if vacancy_status == 'removed':
            raise NotFound("Vacancy removed")
        
        finalized = vacancy_status == 'finalized'
        stages = VacancyStage.objects.filter(vacancy=vacancy)
        all_stage_ids = stages.values_list('stage_id', flat=True)
        allstages = Stage.objects.filter(company=vacancy.company).exclude(id__in=all_stage_ids)

        data = {
            "vacancy": VacancySerializer(vacancy).data,
            "vacancy_status": vacancy_status,
            "finalized": finalized,
            "stages": VacancyStageSerializer(stages, many=True).data,
            "allstages": StageSerializer(allstages, many=True).data,
            "company": company.name,
        }

        return Response(data)

class AddUpdateVacancyTalentSourcingViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        # Check user email
        if not request.user.email:
            return Response({"detail": "Email required"}, status=400)

        # Get subdomain info (implement your subdomain function accordingly)
        subdomain_data = subdomain(request)
        if not subdomain_data.get('active_subdomain'):
            raise NotFound("Subdomain not active")

        recruiter = get_object_or_404(Recruiter, user=request.user, user__is_active=True)
        if not recruiter.is_manager():
            raise PermissionDenied("Not a manager")

        company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
        if not company.check_service('JP_POST'):
            raise PermissionDenied("Service not available")

        vacancy = get_object_or_404(Vacancy, pk=pk, company__in=recruiter.company.all())
        vacancy_status = vacancy.status.codename
        if vacancy_status == 'removed':
            raise NotFound("Vacancy removed")

        finalized = vacancy_status == 'finalized'

        external_referers = ExternalReferal.objects.filter(company=company, referal_type='ER')

        data = {
            "vacancy": VacancySerializer(vacancy).data,
            "vacancy_status": vacancy_status,
            "finalized": finalized,
            "company": CompanySerializer(company).data,
            "external_referers": ExternalReferalSerializer(external_referers, many=True).data,
        }

        return Response(data)

class CompanyRecommendationsViewSet(viewsets.ViewSet):

    def list(self, request):
        # Check if user has email
        if not request.user.email:
            return Response({"detail": "Email required"}, status=400)

        company = get_object_or_404(Company, user=request.user)
        recommendations = Recommendations.objects.filter(to_company=company)
        serializer = RecommendationsSerializer(recommendations, many=True)

        return Response({
            "company": CompanySerializer(company).data,
            "recommendations": serializer.data,
        })

class FirstSearchCurriculaAPIView(APIView):

    def post(self, request):
        # If the user is logged in but has no email, return an error response
        if not request.user.email:
            return Response({"detail": "Email is required."}, status=400)

        session = request.session

        # Vacancies search sessions reset
        session['vacancies_search_industry'] = []
        session['vacancies_search_area'] = []
        session['vacancies_search_state'] = []
        session['vacancies_search_employment_type'] = []
        session['vacancies_search_pub_date'] = []
        session['vacancies_search_text'] = []
        session['pub_dates'] = []
        session['industries'] = []
        session['states'] = []
        session['employment_types'] = []

        # Curricula search sessions reset
        session['candidates_cvs'] = []
        session['first_search_cvs'] = True
        session['degrees'] = None
        session['status'] = None
        session['area'] = None
        session['careers'] = None
        session['state'] = None
        session['municipal'] = None

        indistinct_gender = Gender.objects.get(codename='indistinct')
        session['gender'] = indistinct_gender.id  # Store ID or codename based on your usage

        session['min_age'] = 18
        session['max_age'] = 65
        session['travel'] = None
        session['residence'] = None
        session['language_1'] = None
        session['level_1'] = None
        session['language_2'] = None
        session['level_2'] = None
        session['candidates_cvs'] = []

        session.save()

        # Return JSON response indicating success
        return Response({"detail": "Search sessions reset successfully."})

class SearchCurriculaViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.none()  # Default fallback

    # Inline pagination class
    class InlinePagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = 'page_size'
        max_page_size = 100

    def paginate_queryset(self, queryset):
        paginator = self.InlinePagination()
        page = paginator.paginate_queryset(queryset, self.request, view=self)
        self._paginator = paginator
        return page

    def get_paginated_response(self, data):
        return self._paginator.get_paginated_response(data)

    def get_queryset(self):
        queryset = Candidate.objects.filter(
            pk__in=Curriculum.objects.filter(advance__gt=50).values('candidate')
        ).order_by('-last_modified')

        params = self.request.query_params

        # Filter: gender
        gender_codename = params.get('gender')
        if gender_codename and gender_codename != 'indistinct':
            queryset = queryset.filter(gender__codename=gender_codename)

        # Filter: state/municipal
        state = params.get('state')
        if state:
            queryset = queryset.filter(state__id=state)
            municipals = params.getlist('municipal')
            if municipals:
                queryset = queryset.filter(municipal__id__in=municipals)

        # Filter: age
        today = date.today()
        min_age = params.get('min_age')
        max_age = params.get('max_age')
        if min_age:
            try:
                max_birthdate = today - relativedelta(years=int(min_age))
                queryset = queryset.filter(birthday__lte=max_birthdate)
            except ValueError:
                pass
        if max_age:
            try:
                min_birthdate = today - relativedelta(years=int(max_age))
                queryset = queryset.filter(birthday__gte=min_birthdate)
            except ValueError:
                pass

        # Filter: travel / residence
        travel = params.get('travel')
        if travel:
            queryset = queryset.filter(travel=travel)

        residence = params.get('residence')
        if residence:
            queryset = queryset.filter(residence=residence)

        # Academic filters
        degrees = params.getlist('degrees')
        area = params.get('area')
        careers = params.getlist('careers')
        statuses = params.getlist('status')
        if degrees or area or careers or statuses:
            academic_qs = Academic.objects.filter(candidate__in=queryset)
            if degrees:
                academic_qs = academic_qs.filter(degree__id__in=degrees)
            if area:
                academic_qs = academic_qs.filter(area__id=area)
            if careers:
                academic_qs = academic_qs.filter(career__id__in=careers)
            if statuses:
                academic_qs = academic_qs.filter(status__in=statuses)
            queryset = queryset.filter(pk__in=academic_qs.values('candidate'))

        # Language filters
        language_1 = params.get('language_1')
        level_1 = params.getlist('level_1')
        language_2 = params.get('language_2')
        level_2 = params.getlist('level_2')
        if language_1 or language_2:
            lang_qs = CV_Language.objects.filter(candidate__in=queryset)
            if language_1:
                lang_qs_1 = lang_qs.filter(language__id=language_1, level__in=level_1)
            else:
                lang_qs_1 = None
            if language_2:
                lang_qs_2 = lang_qs.filter(language__id=language_2, level__in=level_2)
            else:
                lang_qs_2 = None

            if lang_qs_1 and lang_qs_2:
                lang_qs = lang_qs_1.filter(candidate__in=lang_qs_2.values('candidate'))
            elif lang_qs_1:
                lang_qs = lang_qs_1
            elif lang_qs_2:
                lang_qs = lang_qs_2

            queryset = queryset.filter(pk__in=lang_qs.values('candidate'))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CompanyWalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer

    def get_queryset(self):
        company = get_object_or_404(Company, user=self.request.user)
        return Wallet.objects.filter(company=company)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        company = instance.company
        movements_qs = Wallet_Movements.objects.filter(company=company).order_by('-id')
        last_movement = movements_qs.first()

        # Inline pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_movements = paginator.paginate_queryset(movements_qs, request)

        return paginator.get_paginated_response({
            'wallet': self.get_serializer(instance).data,
            'last_movement': WalletMovementsSerializer(last_movement).data if last_movement else None,
            'wallet_movements': WalletMovementsSerializer(paginated_movements, many=True).data
        })

class WidgetJobsViewSet(viewsets.ModelViewSet):
    serializer_class = VacancySerializer
    http_method_names = ['get']

    def paginate_queryset(self, queryset):
        class InlinePagination(PageNumberPagination):
            page_size = 10
            page_size_query_param = 'page_size'
            max_page_size = 100

        paginator = InlinePagination()
        return paginator.paginate_queryset(queryset, self.request, view=self), paginator

    def get_queryset(self):
        request = self.request
        subdomain_data = subdomain(request)
        if not subdomain_data.get('active_subdomain'):
            raise Http404("Subdomain not found")

        self.company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])

        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.codename == 'recruiter':
                try:
                    self.recruiter = Recruiter.objects.get(user=request.user, user__is_active=True)
                except Recruiter.DoesNotExist:
                    raise Http404("Recruiter not found")
            else:
                self.recruiter = None
        else:
            self.recruiter = None

        vacancy_status_codename = request.query_params.get('status', 'open')
        self.vacancy_status = get_object_or_404(Vacancy_Status, codename=vacancy_status_codename)

        self.preview = bool(request.query_params.get('preview'))

        return Vacancy.publishedjobs.filter(company=self.company, status=self.vacancy_status)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginated_queryset, paginator = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return paginator.get_paginated_response({
            'company': self.company.name,
            'vacancy_status': self.vacancy_status.codename,
            'preview': self.preview,
            'vacancies': serializer.data
        })

# class BillingViewSet(viewsets.ModelViewSet):
#     http_method_names = ['get']
#     serializer_class = BillingSerializer
#     queryset = Subscription.objects.none()

#     def list(self, request, *args, **kwargs):
#         user = request.user

#         # Access validation
#         if not hasattr(user, 'profile') or user.profile.codename != 'recruiter':
#             raise NotFound("User must be a recruiter.")
#         recruiter = getattr(user, 'recruiter', None)
#         if not recruiter or not recruiter.is_admin():
#             raise PermissionDenied("Only admin recruiters may access billing.")

#         company_qs = recruiter.company.all()
#         if not company_qs.exists():
#             raise NotFound("Recruiter is not associated with any company.")
#         company = company_qs.first()

#         # Subscription logic
#         try:
#             subscription = company.subscription
#         except:
#             subscription = Subscription.objects.create(
#                 company=company,
#                 price_slab=PriceSlab.objects.get(id=2)
#             )
#             company.refresh_from_db()

#         current_slab = subscription.price_slab
#         slab = current_slab
#         future_slab = None
#         amount_to_pay = Decimal('0.00')
#         carried_forward_balance = Decimal('0.00')
#         carried_forward_message = None
#         renewal = slab.amount or Decimal('0.00')
#         user_count = company.recruiter_set.count()

#         # Slab update logic
#         post_payment = 'slab' in request.session or 'plan' in request.query_params
#         if post_payment:
#             plan_id = request.session.pop('slab', request.query_params.get('plan'))
#             slab = PriceSlab.objects.get(id=plan_id)

#             try:
#                 future_slab = company.scheduledtransactions_set.first().price_slab
#             except:
#                 future_slab = slab

#             max_users = slab.package.max_users
#             consolidation_ratio = Decimal(
#                 (subscription.expiry - datetime.now()).days
#             ) / Decimal(current_slab.expiry_period or 1)
#             consolidation_ratio = max(consolidation_ratio, 1)

#             if current_slab != slab:
#                 days_left = Decimal((subscription.expiry - datetime.now()).days)
#                 period = Decimal(current_slab.expiry_period or 1)
#                 carried_forward_balance = (days_left / period) * (current_slab.amount or 0)
#                 amount_to_pay = slab.amount - carried_forward_balance
#                 amount_to_pay = max(amount_to_pay, 0)

#             user_amount_to_pay = (
#                 subscription.added_users *
#                 current_slab.price_per_user *
#                 consolidation_ratio
#             )
#             carried_forward_balance += user_amount_to_pay
#             carried_forward_message = (
#                 f"From slab: {round(carried_forward_balance - user_amount_to_pay, 2)} "
#                 f"and users: {round(user_amount_to_pay, 2)}"
#             )
#             if current_slab == slab:
#                 carried_forward_balance = Decimal('0.00')

#             renewal += (
#                 max(0, user_count - slab.package.free_users)
#                 * slab.price_per_user
#             )

#         else:
#             if subscription.added_users > 0:
#                 renewal += subscription.added_users * current_slab.price_per_user

#         data = {
#             'company': company.name,
#             'current_slab': current_slab.name,
#             'future_slab': future_slab.name if future_slab else None,
#             'renewal': round(renewal, 2),
#             'amount_to_pay': round(amount_to_pay, 2),
#             'carried_forward_balance': round(carried_forward_balance, 2),
#             'carried_forward_message': carried_forward_message,
#             'post_payment': post_payment,
#         }

#         serializer = self.get_serializer(data)
#         return Response(serializer.data)

class TemplateEditorViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    pagination_class = PageNumberPagination
    def get_queryset(self):
        user = self.request.user

        # Permission check equivalent to your codename & manager check
        try:
            if not (user.profile.codename == 'recruiter' and user.recruiter.is_manager()):
                raise Http404
        except Exception:
            raise Http404
        
        # Filter companies related to the user's recruiter companies
        return Company.objects.filter(subdomain__slug__in=[c.subdomain.slug for c in user.recruiter.company.all()])

    def retrieve(self, request, *args, **kwargs):
        company = self.get_object()

        # Validate template existence
        template_path = f'careers/base/t-{company.site_template}/jobs.html'
        try:
            get_template(template_path)
        except Exception:
            return Response(
                {"detail": "Oops! The requested template was not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(company)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# class SiteTemplatePreviewViewSet(viewsets.ModelViewSet):
#     queryset = Company.objects.all()
#     serializer_class = CompanySiteTemplateSerializer

#     class StandardResultsSetPagination(PageNumberPagination):
#         page_size = 10
#         page_size_query_param = 'page_size'
#         max_page_size = 100

#     pagination_class = StandardResultsSetPagination

#     def get_queryset(self):
#         user = self.request.user
#         if not hasattr(user, 'recruiter'):
#             return Company.objects.none()
#         return Company.objects.filter(recruiter__user=user).distinct()

#     def perform_update(self, serializer):
#         user = self.request.user
#         company = serializer.instance
#         recruiter = getattr(user, 'recruiter', None)
#         if not recruiter or company not in recruiter.company.all():
#             raise PermissionDenied("You do not manage this company.")
#         if not recruiter.is_manager():
#             raise PermissionDenied("Only managers can update templates.")
#         serializer.save()

class GetSiteTemplateViewSet(viewsets.ViewSet):
    """
    A ViewSet that handles retrieving a company's site template info along with paginated vacancies,
    with all logic including permission and pagination inside the class.
    """

    class IsRecruiterManager(permissions.BasePermission):
        def has_permission(self, request, view):
            user = request.user
            return (
                user.is_authenticated and
                hasattr(user, 'profile') and
                user.profile.codename == 'recruiter' and
                hasattr(user, 'recruiter') and
                user.recruiter.is_manager()
            )
    
    permission_classes = [IsRecruiterManager]
    pagination_class = PageNumberPagination

    def list(self, request):
        # Optional: You can disable list or raise 405 if not needed
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        # pk is the Company ID or you can change lookup_field if needed
        
        # Permission check handled by permission_classes
        user = request.user

        # Subdomain logic
        subdomain_data = subdomain(request)
        active_subdomain = subdomain_data.get('active_subdomain')
        active_host = subdomain_data.get('active_host')
        if not active_host or not active_subdomain:
            raise Http404

        # Get company by pk and subdomain and user's company membership
        try:
            company = Company.objects.get(id=pk, subdomain__slug=active_subdomain, recruiter__user=user)
        except Company.DoesNotExist:
            raise Http404
        
        # Validate template existence
        template_num = company.site_template
        template_path = f'careers/base/t-{template_num}/jobs.html'
        try:
            get_template(template_path)
        except TemplateDoesNotExist:
            return Response(
                {"detail": "Requested template not found. Please select a valid template."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Query vacancies
        vacancies_qs = Vacancy.publishedjobs.filter(company=company)

        # Paginate vacancies inside the class
        paginator = self.pagination_class()
        paginated_vacancies = paginator.paginate_queryset(vacancies_qs, request, view=self)
        vacancy_serializer = VacancySerializer(paginated_vacancies, many=True)

        company_serializer = CompanySerializer(company)

        return paginator.get_paginated_response({
            'company': company_serializer.data,
            'vacancies': vacancy_serializer.data,
            'editing': True,
            'above_jobs_template': f'careers/base/t-{template_num}/above_jobs.html',
            'jobs_template': f'careers/base/t-{template_num}/jobs.html',
            'below_jobs_template': f'careers/base/t-{template_num}/below_jobs.html',
            'stylesheet': f'sa-ui-kit/t-{template_num}/style.css',
        })