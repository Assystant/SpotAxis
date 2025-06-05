from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.db.models import Q, Count
#from django.utils.timezone import utc, now
from datetime import timezone
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from django.middleware import csrf
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta, date
from weasyprint import HTML
import tempfile
import random
import traceback
from hashids import Hashids
from urllib.parse import urlparse

from candidates.models import Candidate, Curriculum, Academic, Academic_Status, Expertise, Degree
from candidates.forms import CandidateMiniForm, ExpertiseFormset, AcademicFormset
from common.forms import ContactForm
from common.models import Employment_Type, Country, Gender, User, Profile, SocialAuth, State, send_TRM_email
from common.views import debug_token, get_fb_user_groups, get_fb_user_pages, get_li_companies
from companies.models import Company, Stage, Recruiter, Company_Industry as Industry, ExternalReferal
from customField.forms import TemplatedForm
from payments.models import *
from TRM.settings import MEDIA_URL, LOGO_COMPANY_DEFAULT
from TRM.context_processors import subdomain
from TRM.settings import days_default_search, SITE_URL, LOGO_COMPANY_DEFAULT, num_pages, number_objects_page, MEDIA_ROOT
from vacancies.forms import BasicSearchVacancyForm, QuestionVacancyForm, Public_FilesForm, Public_Files_OnlyForm, get_notice_period
from vacancies.models import Vacancy, PubDate_Search, Vacancy_Status, Postulate, Salary_Type, \
    Employment_Experience, Degree, Question, Vacancy_Files, Candidate_Fav, VacancyStage, \
    Postulate_Stage, Postulate_Score, Comment, Medium, Industry
from .serializers import (VacancyStatusSerializer, PubDateSearchSerializer, EmploymentExperienceSerializer, SalaryTypeSerializer,
    VacancySerializer, PublishHistorySerializer, QuestionSerializer, CandidateFavSerializer, 
    VacancyFilesSerializer, VacancyStageSerializer, StageCriterionSerializer, VacancyTagsSerializer, MediumSerializer, 
    PostulateSerializer, CommentSerializer, PostulateScoreSerializer, PostulateStageSerializer)

days_default_search = 30
referer_hash = Hashids(salt='Job Referal', min_length = 5)
external_referer_hash = Hashids(salt='Job External Referal', min_length=5)

class VacancyActiveStatusAPIView(APIView):
    """
    API view to retrieve the Vacancy_Status instance with codename 'open'.
    """

    def get(self, request):
        try:
            active_status = Vacancy_Status.objects.get(codename='open')
        except Vacancy_Status.DoesNotExist:
            return Response({"detail": "Active vacancy status not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VacancyStatusSerializer(active_status)
        return Response(serializer.data, status=status.HTTP_200_OK)

def get_vacancy_active_status():
    """
    Retrieve the Vacancy_Status instance with codename 'open' representing active vacancies.

    Returns:
        Vacancy_Status or None: The Vacancy_Status object with codename 'open', or None if not found.
    """
    try:
        status = Vacancy_Status.objects.get(codename='open')
    except Vacancy_Status.DoesNotExist:
        return None
    return status

class FirstSearchAPIView(APIView):
    """
    API view that initializes session-based search filters and handles recruiter-specific CV search setup.
    """

    def get(self, request):
        if request.user.is_authenticated and not request.user.email:
            return Response({
                "redirect": reverse('common_register_blank_email'),
                "reason": "User is authenticated but missing an email."
            }, status=status.HTTP_302_FOUND)

        session_defaults = {
            'vacancies_search_industry': [],
            'vacancies_search_area': [],
            'vacancies_search_state': [],
            'vacancies_search_employment_type': [],
            'vacancies_search_pub_date': [],
            'vacancies_search_text': [],
            'pub_dates': [],
            'industries': [],
            'states': [],
            'employment_types': []
        }

        request.session.update(session_defaults)

        if request.user.is_authenticated:
            profile_codename = getattr(request.user.profile, 'codename', None)
            if profile_codename == 'recruiter':
                recruiter_defaults = {
                    'candidates_cvs': [],
                    'first_search_cvs': None,
                    'degrees': None,
                    'status': None,
                    'area': None,
                    'careers': None,
                    'state': None,
                    'municipal': None,
                    'gender': None,
                    'min_age': None,
                    'max_age': None,
                    'travel': None,
                    'residence': None,
                    'language_1': None,
                    'level_1': None,
                    'language_2': None,
                    'level_2': None,
                }
                request.session.update(recruiter_defaults)

        return Response({
            "redirect": reverse('vacancies_search_vacancies'),
            "message": "Session search filters initialized."
        }, status=status.HTTP_200_OK)

class CommentsAPIView(APIView):
    """
    API view to retrieve all comments (Question objects).
    """

    def get(self, request):
        comments = Question.objects.all()
        serializer = QuestionSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VacancyAndFilterAPIView(APIView):
    """
    API to retrieve filtered vacancies and associated sidebar filter data.
    """

    def get(self, request):
        session = request.session
        all_vacancies = Vacancy.publishedjobs.all()
        vacancies = all_vacancies

        vacancies_search_industry = session.get('vacancies_search_industry')
        vacancies_search_area = session.get('vacancies_search_area')
        vacancies_search_state = session.get('vacancies_search_state')
        vacancies_search_employment_type = session.get('vacancies_search_employment_type')
        vacancies_search_pub_date = session.get('vacancies_search_pub_date')
        vacancies_search_text = session.get('vacancies_search_text')

        del_filters = False

        if vacancies_search_industry:
            vacancies = vacancies.filter(industry_id=vacancies_search_industry)
            del_filters = True
        if vacancies_search_area:
            vacancies = vacancies.filter(area_id=vacancies_search_area)
            del_filters = True
        if vacancies_search_state:
            vacancies = vacancies.filter(state_id=vacancies_search_state)
            del_filters = True
        if vacancies_search_employment_type:
            vacancies = vacancies.filter(employmentType_id=vacancies_search_employment_type)
            del_filters = True
        if vacancies_search_text:
            vacancies = vacancies.filter(
                Q(employment__icontains=vacancies_search_text) |
                Q(description__icontains=vacancies_search_text)
            )
            del_filters = True

        session['del_filters'] = del_filters

        now = datetime.utcnow().replace(tzinfo=timezone.utc)

        if not vacancies_search_pub_date:
            vacancies_search_pub_date = now - timedelta(days=days_default_search)
            session['vacancies_search_pub_date_days'] = get_object_or_404(PubDate_Search, days=days_default_search)

        vacancies = vacancies.filter(pub_date__gte=vacancies_search_pub_date)

        pub_dates = []
        for pubDate in PubDate_Search.objects.all():
            search_date = now - timedelta(days=pubDate.days)
            filtered = all_vacancies.filter(pub_date__gte=search_date)

            if vacancies_search_state:
                filtered = filtered.filter(state_id=vacancies_search_state)
            if vacancies_search_employment_type:
                filtered = filtered.filter(employmentType_id=vacancies_search_employment_type)
            if vacancies_search_text:
                filtered = filtered.filter(
                    Q(employment__icontains=vacancies_search_text) |
                    Q(description__icontains=vacancies_search_text)
                )

            count = filtered.count()
            if count:
                pub_dates.append({
                    'id': pubDate.id,
                    'name': pubDate.name,
                    'days': pubDate.days,
                    'codename': pubDate.codename,
                    'count': count
                })

        # Start: Industries
        industries = []
        industry_qs = all_vacancies.filter(pub_date__gte=vacancies_search_pub_date)
        if vacancies_search_text:
            industry_qs = industry_qs.filter(
                Q(employment__icontains=vacancies_search_text) |
                Q(description__icontains=vacancies_search_text)
            )
        if vacancies_search_state:
            industry_qs = industry_qs.filter(state_id=vacancies_search_state)
        if vacancies_search_employment_type:
            industry_qs = industry_qs.filter(employmentType_id=vacancies_search_employment_type)

        industry_annotated = industry_qs.values('industry').annotate(count=Count('industry')).order_by('industry')
        for entry in industry_annotated:
            if entry['industry']:
                industry = get_object_or_404(Industry, pk=entry['industry'])
                industries.append({
                    'id': industry.id,
                    'name': industry.name,
                    'count': entry['count']
                })

        # Start: States
        states = []
        state_qs = all_vacancies.filter(pub_date__gte=vacancies_search_pub_date)
        if vacancies_search_text:
            state_qs = state_qs.filter(
                Q(employment__icontains=vacancies_search_text) |
                Q(description__icontains=vacancies_search_text)
            )
        if vacancies_search_industry:
            state_qs = state_qs.filter(industry_id=vacancies_search_industry)
        if vacancies_search_employment_type:
            state_qs = state_qs.filter(employmentType_id=vacancies_search_employment_type)

        state_annotated = state_qs.values('state').annotate(count=Count('state')).order_by('state')
        for entry in state_annotated:
            if entry['state']:
                state = get_object_or_404(State, pk=entry['state'])
                states.append({
                    'id': state.id,
                    'name': state.name,
                    'count': entry['count']
                })
        employment_types = []
        etype_qs = all_vacancies.filter(pub_date__gte=vacancies_search_pub_date)
        if vacancies_search_text:
            etype_qs = etype_qs.filter(
                Q(employment__icontains=vacancies_search_text) |
                Q(description__icontains=vacancies_search_text)
            )
        if vacancies_search_industry:
            etype_qs = etype_qs.filter(industry_id=vacancies_search_industry)
        if vacancies_search_state:
            etype_qs = etype_qs.filter(state_id=vacancies_search_state)

        etype_annotated = etype_qs.values('employmentType').annotate(count=Count('employmentType')).order_by('employmentType')
        for entry in etype_annotated:
            if entry['employmentType']:
                etype = get_object_or_404(Employment_Type, pk=entry['employmentType'])
                employment_types.append({
                    'id': etype.id,
                    'name': etype.name,
                    'count': entry['count']
                })

        vacancy_data = VacancySerializer(vacancies, many=True).data
        return Response({
            "vacancies": vacancy_data,
            "filters": {
                "pub_dates": pub_dates,
                "industries": industries,
                "states": states,
                "employment_types": employment_types,
            }
        }, status=status.HTTP_200_OK)
    
def filter_vacancies_by_industry(request, industry_id=None):
    """
    Stores the selected industry filter in the session based on the provided industry_id.
    
    If industry_id is not zero, it fetches the corresponding Industry object and stores it in the session.
    If industry_id is zero, it clears the industry filter from the session.

    Args:
        request (HttpRequest): The incoming HTTP request.
        industry_id (int or None): ID of the industry to filter vacancies by.

    Returns:
        HttpResponseRedirect: Redirects to the vacancies search results page.
    """
    if industry_id:
        if int(industry_id) != 0:
            request.session['vacancies_search_industry'] = get_object_or_404(Industry, pk=int(industry_id))
        elif int(industry_id) == 0:
            request.session['vacancies_search_industry'] = None
    return redirect('vacancies_search_vacancies')

class FilterVacanciesByStateAPIView(APIView):
    """
    API view to store the selected state filter in the session.
    """

    def post(self, request, state_id=None):
        """
        Store the selected state filter in session based on provided state_id.
        
        - If state_id != 0, fetches State object and stores its id in session.
        - If state_id == 0, clears the filter from session.
        """
        try:
            state_id_int = int(state_id)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid state_id."}, status=status.HTTP_400_BAD_REQUEST)

        if state_id_int != 0:
            state = get_object_or_404(State, pk=state_id_int)
            request.session['vacancies_search_state'] = state.pk
        else:
            request.session['vacancies_search_state'] = None
        return Response({"vacancies_search_state": request.session.get('vacancies_search_state')}, status=status.HTTP_200_OK)


class EmploymentTypeFilterAPIView(APIView):
    """
    API view to set or clear the employment type filter in session.
    """

    def post(self, request, employmentType_id=None):
        """
        Store or clear employment type in session.

        Args:
            employmentType_id (int): The ID passed in the URL (or None to clear).

        Returns:
            JSON: Success status and filter details.
        """
        if employmentType_id is not None:
            if int(employmentType_id) != 0:
                employment_type = get_object_or_404(Employment_Type, pk=employmentType_id)
                request.session['vacancies_search_employment_type'] = employment_type.id  # Store only ID in session
                serializer = EmploymentTypeSerializer(employment_type)
                return Response({
                    "message": "Employment type filter set.",
                    "filter": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                request.session['vacancies_search_employment_type'] = None
                return Response({
                    "message": "Employment type filter cleared."
                }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "employmentType_id not provided."
        }, status=status.HTTP_400_BAD_REQUEST)

class FilterVacanciesByPubDateAPIView(APIView):
    """
    API to store publication date filter in session.
    """

    def post(self, request, days=None):
        try:
            days_int = int(days)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid 'days' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        if 1 <= days_int <= 30:
            pub_date_threshold = now() - timedelta(days=days_int)
            pub_date_obj = get_object_or_404(PubDate_Search, days=days_int)
        else:
            pub_date_threshold = now() - timedelta(days=days_default_search)
            pub_date_obj = get_object_or_404(PubDate_Search, days=days_default_search)

        request.session['vacancies_search_pub_date'] = pub_date_threshold.isoformat()
        request.session['vacancies_search_pub_date_days'] = PubDateSearchSerializer(pub_date_obj).data

        return Response({
            "vacancies_search_pub_date": request.session['vacancies_search_pub_date'],
            "vacancies_search_pub_date_days": request.session['vacancies_search_pub_date_days'],
        }, status=status.HTTP_200_OK)

class VacancySearchAPIView(APIView):
    """
    API for searching vacancies with filters, pagination, and metadata.
    """

    class VacancyPagination(PageNumberPagination):
        page_size = 10 
        page_size_query_param = 'page_size'
        max_page_size = 50

    def get(self, request):
        filters = {}
        session = request.session

        state_id = request.query_params.get('state') or session.get('vacancies_search_state')
        if state_id:
            filters['state_id'] = state_id if isinstance(state_id, int) else getattr(state_id, 'id', None)

        industry_id = request.query_params.get('industry') or session.get('vacancies_search_industry')
        if industry_id:
            filters['industry_id'] = industry_id if isinstance(industry_id, int) else getattr(industry_id, 'id', None)

        pub_date_iso = request.query_params.get('pub_date') or session.get('vacancies_search_pub_date')
        if pub_date_iso:
            try:
                pub_date = pub_date_iso if isinstance(pub_date_iso, str) else pub_date_iso.isoformat()
                filters['pub_date__gte'] = pub_date
            except Exception:
                pass

        search_text = request.query_params.get('search') or session.get('vacancies_search_text')

        vacancies = Vacancy.objects.all()
        if 'pub_date__gte' in filters:
            vacancies = vacancies.filter(pub_date__gte=filters['pub_date__gte'])
        if filters.get('state_id'):
            vacancies = vacancies.filter(state_id=filters['state_id'])
        if filters.get('industry_id'):
            vacancies = vacancies.filter(industry_id=filters['industry_id'])
        if search_text and len(search_text) > 4:
            vacancies = vacancies.filter(title__icontains=search_text)
        paginator = self.VacancyPagination()
        result_page = paginator.paginate_queryset(vacancies, request)

        serializer = VacancySerializer(result_page, many=True)

        total_vacancies = vacancies.count()
        current_filters = {
            "state": filters.get('state_id'),
            "industry": filters.get('industry_id'),
            "pub_date": filters.get('pub_date__gte'),
            "search_text": search_text,
        }

        return paginator.get_paginated_response({
            'vacancies': serializer.data,
            'total_vacancies': total_vacancies,
            'current_filters': current_filters,
        })

class VacancyDetailsAPIView(APIView):

    def get(self, request, vacancy_id, format=None):
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

        user = request.user
        recruiter = None
        if user.is_authenticated:
            recruiter = Recruiter.objects.filter(user=user, user__is_active=True).first()

        my_vacancy = False
        if recruiter and (user == vacancy.user or vacancy.company in recruiter.company.all()):
            my_vacancy = True

        user_profile = None
        if user.is_authenticated:
            user_profile = getattr(user, 'profile', None)
            user_profile_code = getattr(user_profile, 'codename', None)
        else:
            user_profile_code = None

        if not user.is_authenticated or user_profile_code == 'candidate':
            vacancy.seen += 1
            vacancy.save()

        files = Vacancy_Files.objects.filter(vacancy=vacancy)
        files_serialized = VacancyFilesSerializer(files, many=True).data

        questions = Question.objects.filter(vacancy=vacancy)
        questions_serialized = QuestionSerializer(questions, many=True).data

        postulate = None
        is_favorite = None
        if user.is_authenticated and user_profile_code == 'candidate':
            candidate = get_object_or_404(Candidate, user=user)
            postulate = Postulate.objects.filter(candidate=candidate, vacancy=vacancy).first()
            is_favorite = Candidate_Fav.objects.filter(candidate=candidate, vacancy=vacancy).first()

        postulate_serialized = PostulateSerializer(postulate).data if postulate else None
        is_favorite_serialized = CandidateFavSerializer(is_favorite).data if is_favorite else None

        stages = VacancyStage.objects.filter(vacancy=vacancy)
        all_stages = Stage.objects.filter(company=vacancy.company).exclude(id__in=[stage.stage.id for stage in stages])

        notice_period = get_notice_period()
        vacancy_notice_period = notice_period.get(int(vacancy.notice_period), '')

        data = {
            'vacancy': VacancySerializer(vacancy).data,
            'files': files_serialized,
            'questions': questions_serialized,
            'postulate': postulate_serialized,
            'is_favorite': is_favorite_serialized,
            'my_vacancy': my_vacancy,
            'stages': [s.stage.id for s in stages],
            'all_stages': [s.id for s in all_stages],
            'notice_period': vacancy_notice_period,
            'today': str(date.today()),
        }

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, vacancy_id, format=None):
        """
        Handle:
        - Candidate applying (postulate creation)
        - Posting social media shares (if relevant)
        - Uploading photo / CV (if social_code present)
        - Asking questions
        """
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        user = request.user
        data = request.data

        if user.is_authenticated:
            user_profile_code = getattr(getattr(user, 'profile', None), 'codename', None)

            if user_profile_code == 'candidate':
                candidate = get_object_or_404(Candidate, user=user)

                existing_postulate = Postulate.objects.filter(candidate=candidate, vacancy=vacancy).first()
                if existing_postulate:
                    return Response({"detail": _("You have already applied for this position.")}, status=status.HTTP_400_BAD_REQUEST)

                first_stage = VacancyStage.objects.filter(vacancy=vacancy).order_by('order').first()
                new_postulate = Postulate.objects.create(vacancy=vacancy, candidate=candidate, vacancy_stage=first_stage)

                return Response({"detail": _("Successfully applied."), "postulate": PostulateSerializer(new_postulate).data}, status=status.HTTP_201_CREATED)

        return Response({"detail": _("Not authorized or invalid action.")}, status=status.HTTP_403_FORBIDDEN)

class VacancyStageDetailsAPIView(APIView):

    def get_recruiter(self, user, active_subdomain):
        try:
            return Recruiter.objects.get(user=user, user__is_active=True, company__subdomain__slug=active_subdomain)
        except Recruiter.DoesNotExist:
            return None

    def get(self, request, vacancy_id=None, vacancy_stage=None, stage_section='0'):
        error_message = _('The job opening you are trying to find does not exist or has ended')
        today = date.today()

        subdomain_data = subdomain(request)
        if not subdomain_data['active_subdomain']:
            return Response({"detail": "Invalid subdomain"}, status=status.HTTP_404_NOT_FOUND)

        recruiter = self.get_recruiter(request.user, subdomain_data['active_subdomain'])
        if not recruiter:
            return Response({"detail": "Recruiter not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        if not vacancy_id:
            return Response({"detail": error_message}, status=status.HTTP_404_NOT_FOUND)

        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        user = request.user

        my_vacancy = False
        if user.recruiter.company.all()[0] == vacancy.company:
            my_vacancy = True

        if not my_vacancy and not vacancy in Vacancy.publishedjobs.all():
            return Response({"detail": error_message}, status=status.HTTP_404_NOT_FOUND)

        # Validate stage_section, default to '0' if invalid
        if stage_section not in ['0', '1', '2']:
            stage_section = '0'

        candidates = None
        section0_count = section1_count = section2_count = None
        finalize = False

        if vacancy_stage and vacancy_stage != '100':
            vacancystage = get_object_or_404(VacancyStage, vacancy=vacancy, order=int(vacancy_stage))
            if stage_section == '1':
                candidates = Postulate.objects.filter(Q(vacancy=vacancy), Q(finalize=True) | Q(vacancy_stage__order__gt=vacancy_stage))
            elif stage_section == '2':
                candidates = vacancystage.postulate_set.filter(vacancy=vacancy, discard=True)
            else:
                candidates = vacancystage.postulate_set.filter(vacancy=vacancy).exclude(discard=True)

            section0_count = vacancystage.postulate_set.filter(vacancy=vacancy).exclude(discard=True).count()
            section1_count = Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=vacancy_stage).count()
            section2_count = vacancystage.postulate_set.filter(vacancy=vacancy, discard=True).count()

        else:
            finalize = True
            candidates = Postulate.objects.filter(vacancy=vacancy, finalize=True, discard=False)

        stages = VacancyStage.objects.filter(vacancy=vacancy)
        for stage in stages:
            count0 = stage.postulate_set.filter(vacancy=vacancy).exclude(discard=True).count()
            count1 = Postulate.objects.filter(vacancy=vacancy, vacancy_stage__order__gt=stage.order).count()
            count2 = stage.postulate_set.filter(vacancy=vacancy, discard=True).count()
            count3 = Postulate.objects.filter(vacancy=vacancy, finalize=True).count()
            stage.total_count = count0 + count1 + count2

        finalized_count = Postulate.objects.filter(vacancy=vacancy, finalize=True).count()

        process = VacancyStage.objects.filter(vacancy=vacancy, order=vacancy_stage).first()

        for candidate in candidates:
            candidate.process, created = Postulate_Stage.objects.get_or_create(postulate=candidate, vacancy_stage=process)
            candidate.processes = candidate.postulate_stage_set.all()
            candidate.comments = candidate.comment_set.filter(comment_type__lt=2)
            candidate.timeline = candidate.comment_set.filter(comment_type__gte=2)
            rated = candidate.process.scores.filter(recruiter=recruiter)
            candidate.hasRated = rated.exists()
            candidate.comment = rated.first().get_comment if candidate.hasRated else None
            candidate.schedule = candidate.schedule_set.filter(user=request.user, status=0).first()

        isProcessMember = process and request.user.recruiter in process.recruiters.all()

        vacancy_data = VacancySerializer(vacancy).data
        stages_data = VacancyStageSerializer(stages, many=True).data
        candidates_data = PostulateSerializer(candidates, many=True).data

        return Response({
            'vacancy': vacancy_data,
            'is_favorite': None,
            'my_vacancy': my_vacancy,
            'isProcessMember': isProcessMember,
            'postulate': False,
            'allstages': [],
            'current_process': VacancyStageSerializer(process).data if process else None,
            'candidates': candidates_data,
            'finalize_count': finalized_count,
            'today': today,
            'finalize': finalize,
            'stages': stages_data,
            'section0_count': section0_count,
            'section1_count': section1_count,
            'section2_count': section2_count,
            'question_published': 'q' in request.GET,
            'form_question': None,
            'company': CompanySerializer(Company.objects.filter(user=request.user).first()).data if Company.objects.filter(user=request.user).exists() else None,
            'vacancy_stage': vacancy_stage,
            'stage_section': stage_section,
        })

    def post(self, request, vacancy_id=None, vacancy_stage=None, stage_section='0'):
        subdomain_data = subdomain(request)
        if not subdomain_data['active_subdomain']:
            return Response({"detail": "Invalid subdomain"}, status=status.HTTP_404_NOT_FOUND)

        recruiter = self.get_recruiter(request.user, subdomain_data['active_subdomain'])
        if not recruiter:
            return Response({"detail": "Recruiter not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

        form = Public_Files_OnlyForm(request.data or None)
        if form.is_valid():
            save_public_application(request, vacancy, recruiter)
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class VacancyToPDFAPIView(APIView):
    """
    API endpoint to generate a PDF version of a vacancy using WeasyPrint.
    """
    def get(self, request, vacancy_id):
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        user = request.user
        my_vacancy = user.is_authenticated and user == vacancy.user

        logo_pdf = 'logos_TRM/logo_pdf.png'
        pdf_name = f"{vacancy.employment[:30].replace(' ', '_')}_{vacancy.pk}.pdf"

        html_string = render_to_string('vacancy_details_pdf.html', {
            'vacancy': vacancy,
            'MEDIA_URL': MEDIA_URL,
            'logo_pdf': logo_pdf,
            'my_vacancy': my_vacancy,
            'LOGO_COMPANY_DEFAULT': LOGO_COMPANY_DEFAULT,
        })

        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as output:
            HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(output.name)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_name}"'
            return response

class VacanciesByCompanyAPIView(APIView):
    """
    API endpoint that returns paginated vacancies for a given company.

    - Returns only published, non-confidential vacancies.
    - Adds metadata for pagination control.
    """

    def get(self, request, company_id):
        num_pages_visible = settings.num_pages
        number_objects_page = settings.number_objects_page

        company = get_object_or_404(Company, pk=company_id)
        company_user = get_object_or_404(User, pk=company.user.pk)
        queryset = Vacancy.publishedjobs.filter(company=company, confidential=False).order_by('-id')
        total_vacancies = queryset.count()

        # DRF Pagination
        paginator = PageNumberPagination()
        paginator.page_size = number_objects_page
        paginated_vacancies = paginator.paginate_queryset(queryset, request)

        current_page = paginator.page.number
        total_pages = paginator.page.paginator.num_pages

        # Calculate pagination window
        if total_pages > num_pages_visible:
            half_window = num_pages_visible // 2
            if current_page <= half_window:
                minimo_paginas = 1
                maximo_paginas = num_pages_visible
            elif current_page > total_pages - half_window:
                minimo_paginas = total_pages - num_pages_visible + 1
                maximo_paginas = total_pages
            else:
                minimo_paginas = current_page - half_window
                maximo_paginas = current_page + half_window
        else:
            minimo_paginas = 1
            maximo_paginas = total_pages

        # Adjust extra navigation bounds
        paginas_finales = total_pages - num_pages_visible
        link_anterior = max(1, minimo_paginas - 4)
        link_siguiente = min(total_pages, maximo_paginas + 4)

        serialized = VacancySerializer(paginated_vacancies, many=True)

        return paginator.get_paginated_response({
            'company': {
                'id': company.id,
                'name': company.name,
            },
            'company_user': {
                'id': company_user.id,
                'username': company_user.username,
            },
            'vacancies': serialized.data,
            'total_vacancies': total_vacancies,
            'minimo_paginas': minimo_paginas,
            'maximo_paginas': maximo_paginas,
            'link_anterior': link_anterior,
            'link_siguiente': link_siguiente,
            'num_pages_visible': num_pages_visible,
            'paginas_finales': paginas_finales,
            'total_pages': total_pages,
            'current_page': current_page,
        })

class CreateVacanciesAPIView(APIView):
    """
    API endpoint that generates multiple random vacancies for Mexican states and industries.

    POST only. Generates dummy data across different companies and industries.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        industries = Industry.objects.all()
        country_mex = get_object_or_404(Country, iso2_code__exact='MX')
        states = State.objects.filter(country=country_mex)

        created_count = 0

        for state in states:
            for _ in range(2):
                municipal = Municipal.objects.filter(state_id=state).order_by('?').first()
                if not municipal:
                    continue

                for industry in industries:
                    area = Area.objects.filter(industry_id=industry).order_by('?').first()
                    company = Company.objects.all().order_by('?').first()

                    if not (area and company):
                        continue

                    pub_date = (date.today() - timedelta(days=1)) - timedelta(days=random.randint(0, 30))
                    hiring_date = pub_date - timedelta(days=random.randint(0, 30))
                    salary_type = Salary_Type.objects.get(pk=random.randint(1, 6))

                    if salary_type.codename == 'fixed':
                        min_salary = random.randint(8000, 14000)
                        max_salary = random.randint(16000, 50000)
                    else:
                        min_salary = None
                        max_salary = None

                    vacancy = Vacancy.objects.create(
                        company=company,
                        user=company.user,
                        status=get_vacancy_active_status(),
                        employment=f"{company.name} solicits personal",
                        description="This job opening was generated automatically " * 6,
                        state=state,
                        municipal=municipal,
                        industry=industry,
                        area=area,
                        gender=Gender.objects.get(pk=random.randint(1, 3)),
                        employmentType=Employment_Type.objects.get(pk=random.randint(2, 7)),
                        employmentExperience=Employment_Experience.objects.get(pk=random.randint(1, 7)),
                        degree=Degree.objects.get(pk=random.randint(1, 10)),
                        min_age=random.randint(18, 25),
                        max_age=random.randint(26, 64),
                        vacancies_number=random.randint(1, 10),
                        salaryType=salary_type,
                        min_salary=min_salary,
                        max_salary=max_salary,
                        seen=0,
                        postulate=random.choice([True, False]),
                        applications=0,
                        confidential=random.choice([True, False]),
                        questions=random.choice([True, False]),
                        pub_after=False,
                        pub_date=pub_date,
                        hiring_date=hiring_date,
                        editing_date=pub_date + timedelta(days=5),
                        end_date=pub_date + timedelta(days=30),
                        email='contact.travelder@gmail.com'
                    )

                    vacancy.employment = f"{vacancy.id} - {vacancy.employment}"
                    vacancy.data_contact = False if vacancy.confidential else random.choice([True, False])
                    vacancy.save()
                    created_count += 1

        return Response({"message": f"{created_count} vacancies created."}, status=status.HTTP_201_CREATED)

def save_public_application(request,vacancy, recruiter, referer = None, external_referer=None, array = False):
    """
    Saves a public job application submitted by a user without a candidate account.

    Creates a new `Candidate`, `Curriculum`, and `Postulate` instance based on uploaded files
    and form data. Attaches referer, external referer, or recruiter if present and logs a comment.

    Args:
        request (HttpRequest): The HTTP request containing form data and uploaded files.
        vacancy (Vacancy): The vacancy object to which the application is being submitted.
        recruiter (Recruiter): Optional recruiter submitting the application on behalf of the candidate.
        referer (Recruiter, optional): Referring recruiter (internal).
        external_referer (ExternalReferal, optional): External referral source.
        array (bool, optional): If True, returns a list containing form, saved flag, and postulate.

    Returns:
        Public_FilesForm or list: The submitted form or [form, saved (bool), new_cv_public (Postulate)]
    """
    saved = False
    new_cv_public = None
    try:
        public_form = Public_FilesForm(data=request.POST, files=request.FILES, v_id = vacancy.id)
        if public_form.is_valid():
            if request.FILES:
                email = request.POST.get('email')
                old_cv_files = Postulate.objects.filter(vacancy=vacancy, candidate__public_email=email)
                if not old_cv_files:
                    full_name = request.POST.get('full_name').strip().split(' ')
                    first_name = full_name[0]
                    last_name = ' '.join(full_name[1:])
                    description = request.POST.get('description')
                    file = public_form.clean_file()
                    first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
                    candidate = Candidate.objects.create(first_name = first_name, last_name = last_name, public_email = email)
                    curriculum = Curriculum.objects.create(candidate = candidate, file = file)
                    new_cv_public = Postulate.objects.create(vacancy=vacancy, candidate = candidate, description=description, vacancy_stage=first_stage)
                    if request.session.get('referral_source'):
                        medium, created = Medium.objects.get_or_create(name=request.session.pop('referral_source'))
                        new_cv_public.medium= medium
                        new_cv_public.save()
                    if recruiter:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.recruiter = recruiter
                        new_cv_public.is_recruiter = True
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Application Added by '+ str(recruiter.user.get_full_name()))
                    elif referer:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.recruiter = referer
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Refered by '+ str(referer.user.get_full_name()))                        
                    elif external_referer:
                        # new_cv_public.isRecruiter = True
                        new_cv_public.external_reference = external_referer
                        new_cv_public.save()
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Reference by '+ str(external_referer.name))                        
                    else:
                        Comment.objects.create(postulate = new_cv_public, comment_type=3, text='Application Received for the job opening')
                        # file_path = str(new_cv_public.file.path)
                        # Send Mail
                        # context_email = {
                        #     'vacancy': vacancy,
                        #     'full_name': new_cv_public.full_name,
                        #     'email': email,
                        #     'salary': new_cv_public.salary,
                        #     'age': new_cv_public.age,
                        #     'description': new_cv_public.description,
                        #     'file_path': file_path,
                        #     'public_postulate': True,
                        # }

                        # subject_template_name = 'mails/public_postulate_subject.html',
                        # email_template_name = 'mails/public_postulate_email.html',
                         # Mail to company
                        # send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=vacancy.email,file=file_path)

                        # Mail to candidate
                        # send_TRM_email(subject_template_name=subject_template_name, email_template_name=email_template_name, context_email=context_email, to_user=email,file=file_path)
                        # public_form = Public_FilesForm()
                    if recruiter:
                        messages.success(request,'Candidate Profile added to the job opening "%s"' % vacancy.employment)
                        # context['msg'] = u'Candidate Profile added to the job opening "%s"' % vacancy.employment
                    else:
                        messages.success(request,'We have successfully submitted your profile to the job opening "%s"' % vacancy.employment)
                        # context['msg'] = u'We have successfully submitted your profile to the job opening "%s"' % vacancy.employment
                    saved = True
                else:
                    messages.error(request, 'Already Applied')
                    # context['msg'] = u'Already Applied'
        else:
            # context['errors'] = public_form.errors
            pass
    except:
        tb = traceback.format_exc()
        print(tb)
        messages.error(request,  'Failed to apply to this job opening, please try again...')
        public_form = Public_FilesForm()
        new_cv_public = None
        saved = False
    if not array:
        return public_form
    else:
        return [public_form, saved, new_cv_public]

class PublicApplyAPIView(APIView):
    """
    Handles public job applications using DRF for a specific vacancy.
    """

    def get(self, request, vacancy_id=None):
        return self._handle_request(request, vacancy_id, method='GET')

    def post(self, request, vacancy_id=None):
        return self._handle_request(request, vacancy_id, method='POST')

    def _handle_request(self, request, vacancy_id, method):
        error_message = _('The job opening you are trying to find does not exist or has ended')
        today = now().date()
        postulate = False
        my_vacancy = False
        subdomain_data = subdomain(request)
        if not subdomain_data['active_host']:
            raise Http404

        company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])

        if not company.check_service('CSM_ONSITE_APPLY'):
            raise Http404

        recruiter = None
        if request.user.is_authenticated:
            recruiter = Recruiter.objects.filter(user=request.user, user__is_active=True).first()

        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        if not vacancy.public_cvs and not vacancy.postulate:
            raise Http404(error_message)

        if recruiter and (request.user == vacancy.user or vacancy.company in recruiter.company.all()):
            my_vacancy = True

        if not my_vacancy and vacancy not in Vacancy.publishedjobs.all():
            raise Http404(error_message)

        user_profile = None
        if request.user.is_authenticated:
            try:
                user_profile = request.user.profile.codename
            except:
                pass

        # Referer and external referer logic
        referer = request.query_params.get('referer')
        external_referer = request.query_params.get('external_referer')
        referer_obj = None
        external_referer_obj = None

        if not recruiter:
            if referer:
                referer_id = referer_hash.decode(referer)
                if referer_id:
                    referer_obj = Recruiter.objects.filter(id=referer_id[0], company=vacancy.company).first()
            elif external_referer:
                external_id = external_referer_hash.decode(external_referer)
                if external_id:
                    external_referer_obj = ExternalReferal.objects.filter(id=external_id[0], company=vacancy.company).first()

        if isinstance(request.user, AnonymousUser) or user_profile == 'candidate':
            vacancy.seen += 1
            vacancy.save()

        files = Vacancy_Files.objects.filter(vacancy=vacancy)

        if method == 'POST':
            form = save_public_application(request, vacancy, recruiter, referer_obj, external_referer_obj)
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            form = Public_Files_OnlyForm()
            return Response({
                'company': company.id,
                'vacancy': vacancy.id,
                'form_fields': form.fields.keys(),
                'referer': referer,
                'external_referer': external_referer,
            }, status=status.HTTP_200_OK)

def extract_public_form_content(public_form):
    """
    Parses uploaded resume content from the public form and generates a minimal candidate profile.

    Utilizes a resume parsing library to extract structured information such as name, email,
    phone, skills, and education history from the uploaded file. Creates corresponding
    Candidate, Curriculum, and Academic objects in the database.

    Args:
        public_form (Public_FilesForm): The validated form containing the uploaded resume.

    Returns:
        list: A list containing the created Candidate and Curriculum instances.
    """

    from resume_parser.resume_parser import extract_file_content
    file = public_form.clean_file()
    candidate = Candidate.objects.create()
    # first_stage=VacancyStage.objects.get(order=0, vacancy = vacancy)
    curriculum = Curriculum.objects.create(candidate = candidate, file = file)
    # new_cv_public = Postulate.objects.create(vacancy=vacancy, candidate = candidate, description=description, vacancy_stage=first_stage)
    # dat = read_file_content_directly(uploaded_file)
    dat = extract_file_content(curriculum.file.path, 'json')
    print(dat)
    if dat['name']:
        names = dat['name'][0].split(' ')
        candidate.first_name = names[0]
        try:
            candidate.save()
        except:
            pass
        if len(names) > 1:
            candidate.last_name = ' '.join(names[1:])
            try:
                candidate.save()
            except:
                pass
    if len(dat['phones']) > 0:
        candidate.phone = dat['phones'][0]
        try:
            candidate.save()
        except:
            pass
    if len(dat['emails']) > 0:
        candidate.public_email = dat['emails'][0]
        try:
            candidate.save()
        except:
            pass
    candidate.skills = ','.join(dat['skills'])
    try:
        candidate.save()
    except:
        pass
    max_i = max(len(dat['education']['education-degrees']), len(dat['education']['school-college']))
    i = 0
    while i < max_i:
        try:
            degree = dat['education']['education-degrees'][i]
        except:
            degree = ""
        try:
            school = dat['education']['school-college'][i]
        except:
            school = ""
        try:
            dates = dat['education']['education-dates'][i].split('-')
        except:
            dates = None
        start_date = None
        end_date=None
        status = 'complete'
        try:
            if len(dates) > 1 :
                start_date = date(int(dates[0]),1,1)
                if not dates[1] == 'Present':
                    end_date = date(int(dates[1]),1,1)
                else:
                    status = 'progress'
            else:
                end_date = date(int(dates[0]),1,1)
        except:
            pass
        new_academic = Academic.objects.create(
                candidate = candidate,
                course_name = degree,
                status = Academic_Status.objects.get(codename=status)
            )
        new_academic.school = school
        try:
            new_academic.save()
        except:
            pass
        if start_date:
            new_academic.start_date = start_date
        if end_date:
            new_academic.end_date = end_date
        try:
            new_academic.save()
        except:
            pass
        i = i+1
    # Add work parsing
    return [candidate, curriculum]

class NewApplicationAPIView(APIView):
    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        recruiter_upload = False
        fresh_application = False
        candidate = None
        sa_profile = None
        conflicts = None
        advanced_error = False

        referer_path = request.data.get('refering_page')
        if referer_path:
            request.session['referer'] = referer_path
            fresh_application = True
        else:
            referer_path = request.session.get('referer')

        user = request.user
        is_recruiter = user.is_authenticated and user.profile.codename == 'recruiter'
        is_candidate = user.is_authenticated and user.profile.codename == 'candidate'

        if is_recruiter and vacancy.company in user.recruiter.company.all():
            recruiter_upload = True

        if user.is_anonymous or recruiter_upload:
            if fresh_application:
                public_form = Public_Files_OnlyForm(data=request.data, files=request.FILES, v_id=vacancy.id)
                if public_form.is_valid():
                    candidate, curriculum = extract_public_form_content(public_form)
                    request.session['candidate'] = candidate.id
                    existing = Postulate.objects.filter(
                        Q(candidate__public_email=candidate.public_email) |
                        Q(candidate__user__email=candidate.public_email),
                        vacancy=vacancy
                    )
                    if existing.exists():
                        curriculum.delete()
                        candidate.delete()
                        return Response({"error": "Already applied."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "Invalid upload", "details": public_form.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                candidate_id = request.session.get('candidate')
                if not candidate_id:
                    return Response({"error": "Invalid upload."}, status=status.HTTP_400_BAD_REQUEST)
                candidate = get_object_or_404(Candidate, id=candidate_id)
                curriculum = get_object_or_404(Curriculum, candidate=candidate)
                if user.is_anonymous:
                    sa_profile = Candidate.objects.filter(~Q(user=None), user__email=candidate.public_email).first()
        elif is_candidate:
            candidate = user.candidate
            curriculum = get_object_or_404(Curriculum, candidate=candidate)
            existing = Postulate.objects.filter(
                Q(candidate=candidate) |
                Q(candidate__public_email=candidate.user.email),
                vacancy=vacancy
            )
            if existing.exists():
                return Response({"error": "Already applied."}, status=status.HTTP_400_BAD_REQUEST)
            old_candidate_id = request.session.pop('candidate', None)
            if old_candidate_id:
                old_candidate = Candidate.objects.filter(id=old_candidate_id).first()
                if old_candidate:
                    old_candidate.parent_profile = candidate
                    old_candidate.save()
        else:
            raise Http404

        if not fresh_application:
            candidate_form = CandidateMiniForm(instance=candidate, data=request.data)
            expertise_forms = ExpertiseFormset(prefix="expertise", queryset=candidate.expertise_set.all(), data=request.data)
            academic_forms = AcademicFormset(prefix="academic", queryset=candidate.academic_set.all(), data=request.data)

            if candidate_form.is_valid():
                candidate_form.save()
                candidate.refresh_from_db()
                existing = Postulate.objects.filter(
                    Q(candidate=candidate) |
                    Q(candidate__public_email=candidate.user.email),
                    vacancy=vacancy
                )
                if existing.exists():
                    return Response({"error": "Already applied."}, status=status.HTTP_400_BAD_REQUEST)
            if expertise_forms.is_valid():
                expertises = expertise_forms.save()
                for expertise in expertises:
                    expertise.candidate = candidate
                    expertise.save()
            else:
                advanced_error = True

            if academic_forms.is_valid():
                academics = academic_forms.save()
                for academic in academics:
                    academic.candidate = candidate
                    academic.save()
            else:
                advanced_error = True

        conflicts = candidate.find_conflicts()
        today = now().date()
        applicant = candidate

        return Response({
            "vacancy_id": vacancy.id,
            "applicant_id": applicant.id,
            "candidate_id": candidate.id if not recruiter_upload else None,
            "curriculum": curriculum.filename,
            "conflicts": conflicts,
            "today": str(today),
            "sa_profile": sa_profile.id if sa_profile else None,
            "advanced_error": advanced_error,
        }, status=status.HTTP_200_OK)

class ResolveApplicationConflictsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, vacancy_id, card_type):
        if not hasattr(request.user, 'profile') or request.user.profile.codename != 'candidate':
            raise Http404("Only candidates may resolve conflicts.")

        candidate = request.user.candidate
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)

        if str(card_type) == '1':  # Academic
            course_name = request.data.get('course_name', '').strip()
            school = request.data.get('school', '').strip()
            degree_name = request.data.get('degree', '').strip()
            area = request.data.get('area', '').strip()
            country_name = request.data.get('country', '').strip()
            state = request.data.get('state', '').strip()
            city = request.data.get('city', '').strip()
            status_name = request.data.get('status', 'Completed').strip()
            start_date = request.data.get('start_date', '').strip()
            end_date = request.data.get('end_date', '').strip()
            old_cards = request.data.get('old_cards', [])

            degree = Degree.objects.filter(name=degree_name).first() or None
            country = Country.objects.filter(name=country_name).first() or None
            status = Academic_Status.objects.filter(name=status_name).first() or Academic_Status.objects.get(name="Completed")

            new_academic = Academic.objects.create(
                candidate=candidate,
                course_name=course_name,
                school=school,
                degree=degree,
                area=area,
                country=country,
                state=state,
                city=city,
                status=status,
                start_date=start_date,
                end_date=end_date
            )

            if old_cards:
                Academic.objects.filter(id__in=old_cards).delete()

        elif str(card_type) == '2':  # Professional/Expertise
            employment = request.data.get('employment', '').strip()
            company = request.data.get('company', '').strip()
            tasks = request.data.get('tasks', '').strip()
            start_date = request.data.get('start_date', '').strip()
            end_date = request.data.get('end_date', '').strip()
            industry_ids = request.data.get('industry', [])
            old_cards = request.data.get('old_cards', [])

            industries = Company_Industry.objects.filter(id__in=industry_ids)

            new_expertise = Expertise.objects.create(
                candidate=candidate,
                employment=employment,
                company=company,
                tasks=tasks,
                start_date=start_date,
                end_date=end_date,
            )
            new_expertise.industry.set(industries)

            # Delete conflicting expertise entries
            if old_cards:
                Expertise.objects.filter(id__in=old_cards).delete()
        else:
            return Response({"detail": "Invalid card type."}, status=status.HTTP_400_BAD_REQUEST)

        candidate.refresh_from_db()
        conflicts = candidate.find_conflicts()
        today = datetime.now().date()

        return Response({
            "message": "Conflict resolved successfully.",
            "conflicts": conflicts,
            "today": today,
        }, status=status.HTTP_200_OK)

class CompleteApplicationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        vacancy_has_form_template = vacancy.form_template
        referer_path = request.META.get('HTTP_REFERER', None)
        recruiter_upload = False

        if request.user.profile.codename == 'recruiter' and vacancy.company in request.user.recruiter.company.all():
            recruiter_upload = True
            vacancy_has_form_template = False

        try:
            referer_name = resolve(urlparse(referer_path).path).url_name if referer_path else None
        except Exception:
            referer_name = None

        referer_session = request.session.get('referer', None)

        if not recruiter_upload:
            if request.user.profile.codename != 'candidate':
                raise Http404("User must be candidate to apply")
            candidate = request.user.candidate
        else:
            candidate_id = request.session.get('candidate')
            candidate = get_object_or_404(Candidate, id=candidate_id)
            if not candidate.public_email:
                return Response({"error": "Email is required and missing."}, status=status.HTTP_400_BAD_REQUEST)

        curriculum = Curriculum.objects.get(candidate=candidate)
        templated_form = None
        coverletter = None

        if request.method == 'POST' and request.path == reverse(referer_name, args=[vacancy.pk]):
            coverletter = request.data.get('coverletter', '')
            if vacancy_has_form_template:
                templated_form = TemplatedForm(request.data, template=vacancy_has_form_template, formClasses="form-control")

            if (vacancy_has_form_template and templated_form.is_valid()) or coverletter is not None:
                first_stage = VacancyStage.objects.get(order=0, vacancy=vacancy)
                application, created = Postulate.objects.get_or_create(
                    vacancy=vacancy,
                    candidate=candidate,
                    vacancy_stage=first_stage
                )

                cookie = request.COOKIES.get(f'referer-{vacancy.id}')
                referral_source = request.session.pop('referral_source', None)
                if referral_source:
                    medium, _ = Medium.objects.get_or_create(name=referral_source)
                    application.medium = medium
                    application.save()

                referer = None
                if cookie:
                    try:
                        referer = Recruiter.objects.get(id=int(cookie))
                    except Recruiter.DoesNotExist:
                        referer = None

                external_referer = None
                if not referer:
                    cookie_ext = request.COOKIES.get(f'exreferer-{vacancy.id}')
                    external_referer = None

                if referer:
                    application.recruiter = referer
                    application.save()
                    Comment.objects.create(postulate=application, comment_type=3,
                                           text=f'Referred by {referer.user.get_full_name()}')
                elif external_referer:
                    application.external_referer = external_referer
                    application.save()
                    Comment.objects.create(postulate=application, comment_type=3,
                                           text=f'Referenced by external referer')
                elif recruiter_upload:
                    application.is_recruiter = True
                    application.recruiter = request.user.recruiter
                    application.save()
                    Comment.objects.create(postulate=application, comment_type=3,
                                           text=f'Application added by {request.user.get_full_name()}')
                else:
                    Comment.objects.create(postulate=application, comment_type=3,
                                           text='Application received for the job opening')

                if vacancy_has_form_template and templated_form.is_valid():
                    fields = templated_form.save()
                    for field in fields:
                        if field.value:
                            application.has_filled_custom_form = True
                            application.custom_form_application.add(field)
                    application.save()

                if coverletter:
                    application.description = coverletter
                    application.save()

                request.session.pop('referer', None)
                request.session.pop('candidate', None)

                msg = 'New application has been added.' if recruiter_upload else 'Your application has been received.'
                return Response({"message": msg}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Invalid form or missing cover letter"}, status=status.HTTP_400_BAD_REQUEST)

        if vacancy_has_form_template and not templated_form:
            templated_form = TemplatedForm(template=vacancy_has_form_template, formClasses="form-control mt2")

        return Response({
            "candidate_id": candidate.id,
            "vacancy_id": vacancy.id,
            "templated_form": str(templated_form) if templated_form else None
        }, status=status.HTTP_200_OK)

class VacancyTalentSourcingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vacancy_id):
        subdomain_data = subdomain(request)
        if not subdomain_data.get('active_subdomain'):
            raise Http404("Inactive subdomain")

        recruiter = get_object_or_404(Recruiter, user=request.user, user__is_active=True)
        if not recruiter.is_manager():
            raise Http404("User is not a manager recruiter")

        company = get_object_or_404(Company, subdomain__slug=subdomain_data['active_subdomain'])
        if not company.check_service('JP_POST'):
            raise Http404("JP_POST service not active for company")

        vacancy = get_object_or_404(Vacancy, pk=vacancy_id, company__in=recruiter.company.all())

        external_referers = ExternalReferal.objects.filter(company=company, referal_type='ER')

        return Response({
            "vacancy": {
                "id": vacancy.id,
                "title": vacancy.title,
            },
            "isVacancy": True,
            "vacancy_id": vacancy_id,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
            },
            "company": {
                "id": company.id,
                "name": company.name,
            },
            "external_referers": [
                {
                    "id": er.id,
                    "name": er.name,
                }
                for er in external_referers
            ]
        }, status=status.HTTP_200_OK)