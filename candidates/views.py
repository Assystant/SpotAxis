# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import os
import random

from datetime import datetime
import traceback
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import Http404, JsonResponse
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from weasyprint import HTML
from companies.models import Company_Industry
from .forms import AcademicForm, CandidateForm, CvLanguageForm, ExpertiseForm, ObjectiveForm, \
    cv_FileForm, TrainingForm, CertificateForm, ProjectForm, InterestsForm, \
    HobbiesForm, ExtraCurricularsForm, OthersForm, CandidateContactForm
from .models import Candidate, Academic, Academic_Area, Academic_Status, Curriculum, CV_Language, \
     Expertise, Language, Language_Level, Training, Certificate, Project
from common import registration_settings as up_settings
from common.models import State, Profile, User, Gender, Marital_Status, Municipal, Degree, Country
from common.forms import UserDataForm, UserPhotoForm
from django.forms.models import modelformset_factory
from vacancies.models import Vacancy_Status, Postulate, Candidate_Fav
from TRM.context_processors import subdomain
from TRM.settings import SITE_URL
from django.db.models import Q
from six.moves import range
from utils import is_ajax

def resume_builder(request):
    """
    Render the resume builder page with all required candidate-related forms.

    Supports AJAX requests for partial form submissions.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered resume builder HTML page with forms.
    """
    subdomain_data = subdomain(request)
    if subdomain_data['active_subdomain']:
        url = SITE_URL + reverse('candidates_resume_builder'),
        redirect(url)
    if is_ajax(request):
        data = request.POST
        formno = request.POST['formno']
        if formno == 0:
            candidateForm = CandidateForm(data=data,files = request.FILES) 
    candidateForm = CandidateForm()
    candidateContactForm = CandidateContactForm()
    objectiveForm = ObjectiveForm()
    interestsForm = InterestsForm()
    hobbiesForm = HobbiesForm()
    extraCurricularsForm = ExtraCurricularsForm()
    othersForm = OthersForm()
    academicForm = AcademicForm()
    expertiseForm = ExpertiseForm()
    trainingForm = TrainingForm()
    certificateForm = CertificateForm()
    projectForm = ProjectForm()
    languageForm = CvLanguageForm()
    return render(request,'resume_builder.html',
                              {'user': request.user,
                               'ispublicCV': True,
                               'form_academic': academicForm,
                               'form_candidate': candidateForm,
                               'form_candidate_contact': candidateContactForm,
                               'form_interests': interestsForm,
                               'form_hobbies': hobbiesForm,
                               'form_extra_curriculars': extraCurricularsForm,
                               'form_others': othersForm,
                               'form_objective': objectiveForm,
                               'form_experience': expertiseForm,
                               'form_training': trainingForm,
                               'form_certificate': certificateForm,
                               'form_project': projectForm,
                               'form_language': languageForm})

                               
                              

def resume_builder_templates(request,candidate_id=None):
    """
    Render a resume template view for a given candidate by candidate_id.

    Args:
        request (HttpRequest): The HTTP request object.
        candidate_id (int, optional): The ID of the candidate whose resume template is requested.

    Raises:
        Http404: If the candidate with the given ID does not exist.

    Returns:
        HttpResponse: Rendered resume template page.
    """
    try: 
        candidate = Candidate.objects.get(id = candidate_id)  
        referer = request.META['HTTP_REFERER']
    except:
        referer = None
        raise Http404
    context={}
    context['candidate'] = candidate
    return render(request,'resume_template.html',{
    
                                                        'candidate':candidate,
                                                    }) 

    return JsonResponse(context)
def record_candidate(request):
    """
    Handle candidate registration by processing user data form submissions.

    On successful form validation, creates a new user, assigns candidate profile,
    sends verification email, and redirects to a registration success page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the candidate registration form on GET or invalid POST,
                      redirects after successful registration.
    """
    if request.method == 'POST':
        form_user = UserDataForm(data=request.POST,
                                 files=request.FILES,)
        if form_user.is_valid():
            new_user = form_user.save()
            candidate_profile = Profile.objects.get(codename='candidate')
            new_user.profile = candidate_profile
            new_user.logued_by = 'EL'
            new_user.save()
            # try:
            Candidate.objects.create(user=new_user, first_name=new_user.first_name, last_name=new_user.last_name)
            form_user.send_verification_mail(new_user)
            request.session['new_email'] = new_user.email
            # raise ValueError(request.session.keys())
            # raise ValueError(request.session['new_email'])

            return redirect(up_settings.REGISTRATION_REDIRECT)
            # except:
            #     new_user.delete()
            #     raise Http404


    else:
        form_user = UserDataForm()

    # raise ValueError(form_user.errors)
    return render(request,'candidate_registration.html',
                              {'form_user': form_user})
   


@login_required
def edit_curriculum(request, candidate_id=None):
    profile ='candidate'
    """
    View to edit a candidate's curriculum vitae (CV).

    Allows uploading/removing CV files, updating candidate personal info, photo,
    and managing academic, expertise, training, certificates, projects, and languages.

    Calculates curriculum completion status and renders the edit CV page.

    Args:
        request (HttpRequest): The HTTP request object.
        candidate_id (int, optional): The candidate ID to edit. Defaults to logged-in user.

    Returns:
        HttpResponse: Rendered edit CV page with forms and candidate data.
    """
    if request.user.is_authenticated and not request.user.email:
        # iF THE USER IS LOGGED IN AND HAS NO EMAIL...
        redirect_page = 'common_register_blank_email'
        return redirect(redirect_page)

    if profile == 'candidate':
        candidate, created = Candidate.objects.get_or_create(user=request.user)
    else:
        raise Http404("Only candidates can access this page.")

    if candidate_id:
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        company = True
    else:
        candidate = get_object_or_404(Candidate, user=request.user)
        company = False

    curriculum, created = Curriculum.objects.get_or_create(candidate=candidate)

    # if created:
        # If the candidate is new default language english is added as native language
        # language_esp = get_object_or_404(Language, codename='en')
        # esp_level = get_object_or_404(Language_Level, codename='native')
        # CV_Language.objects.create(candidate=candidate, language=language_esp, level=esp_level)

    academics = Academic.objects.filter(candidate=candidate)
    expertises = Expertise.objects.filter(candidate=candidate)
    languages = CV_Language.objects.filter(candidate=candidate)
    trainings = Training.objects.filter(candidate=candidate)
    certificates = Certificate.objects.filter(candidate=candidate)
    projects = Project.objects.filter(candidate=candidate)
    # softwares = CV_Software.objects.filter(candidate=candidate)

    actual_cv_file = None
    if curriculum.file:
        actual_cv_file = curriculum.file
    fileForm = False
    photoForm = False
    if request.method == 'POST':

        del_actual_cv = request.POST.get('del-actual-cv')
        if del_actual_cv:
            # If the user clicked Delete to remove their CV
            if actual_cv_file:
                try:
                    remove_file = os.path.join(settings.MEDIA_ROOT, str(actual_cv_file))
                    os.remove(str(remove_file))
                    curriculum.file = None
                    curriculum.save()
                    messages.success(request, _('Your CV/Portafolio was successfully removed from the system'))
                except:
                    tb = traceback.format_exc()
                    print(tb)
                    pass
                return redirect('candidates_edit_curriculum')

        if not request.POST.get('isimage','0') =='1':
            fileForm = cv_FileForm(data=request.POST, files=request.FILES, instance=curriculum)

            if fileForm.is_valid():
                new_cv_file = request.FILES.get('file')
                if new_cv_file:
                    fileForm.save()
                    if actual_cv_file:
                        try:
                            remove_file = os.path.join(settings.MEDIA_ROOT, str(actual_cv_file))
                            print(('remove_file: %s' % remove_file))
                            os.remove(str(remove_file))
                        except:
                            tb = traceback.format_exc()
                            print(tb)
                            pass
                    messages.success(request, _('Successfuly uploaded your file %s') % curriculum.filename())
                return redirect('candidates_edit_curriculum')
        else:
            photoForm = UserPhotoForm(instance=candidate.user, data=request.POST, files=request.FILES)
            if photoForm.is_valid():
                photoForm.save()
                candidate.refresh_from_db()
                messages.success(request, "Successfully updated photo")
    if not fileForm:
        fileForm = cv_FileForm(instance=curriculum)
    candidateForm = CandidateForm(instance=candidate)
    candidateContactForm = CandidateContactForm(instance=candidate)
    objectiveForm = ObjectiveForm(instance=candidate)
    interestsForm = InterestsForm(instance=candidate)
    hobbiesForm = HobbiesForm(instance=candidate)
    extraCurricularsForm = ExtraCurricularsForm(instance=candidate)
    othersForm = OthersForm(instance=candidate)
    academicForm = AcademicForm()
    expertiseForm = ExpertiseForm()
    trainingForm = TrainingForm()
    certificateForm = CertificateForm()
    projectForm = ProjectForm()
    languageForm = CvLanguageForm()
    if not photoForm:
        photoForm = UserPhotoForm(instance=candidate.user)

    # The Progress or comletion percentage in curriculum
    if candidate.birthday and candidate.gender:
        curriculum.personal_info = True
    if candidate.objective:
        curriculum.objective = True
    if candidate.interests:
        curriculum.interests = True
    if expertises:
        curriculum.expertise = True
        for expertise in expertises:
            expertise.form = ExpertiseForm(instance=expertise)
    if academics:
        curriculum.academic = True
        for academic in academics:
            academic.form = AcademicForm(instance=academic)
    if languages:
        curriculum.language = True
        for language in languages:
            language.form = Language
    if trainings:
        curriculum.training = True
        for training in trainings:
            training.form = TrainingForm(instance=training)
    if certificates:
        curriculum.certificate = True
        for certificate in certificates:
            certificate.form = CertificateForm(instance=certificate)
    if projects:
        curriculum.project = True
        for project in projects:
            project.form = ProjectForm(instance=project)
    if languages:
        curriculum.language = True
        for language in languages:
            language.form = CvLanguageForm(instance=language)
    # if softwares:
    #     curriculum.software = True
    curriculum.set_advance()
    curriculum.save()

    today = datetime.now().date()
    return render(request,'edit_view_curriculum.html',
                              {'user': request.user,
                               'isCV': True,
                               'today': today,
                               'fileForm': fileForm,
                               'form_academic': academicForm,
                               'form_candidate': candidateForm,
                               'form_candidate_contact': candidateContactForm,
                               'form_objective': objectiveForm,
                               'form_interests': interestsForm,
                               'form_hobbies': hobbiesForm,
                               'form_extra_curriculars': extraCurricularsForm,
                               'form_others': othersForm,
                               'form_experience': expertiseForm,
                               'form_training': trainingForm,
                               'form_certificate': certificateForm,
                               'form_language': languageForm,
                               'form_project': projectForm,
                               'form_user_photo': photoForm,
                               'curriculum': curriculum,
                               'candidate': candidate,
                               'academics': academics,
                               'trainings': trainings,
                               'certificates': certificates,
                               'projects': projects,
                               'expertises': expertises,
                               'languages': languages,
                               # 'softwares': softwares,
                               'company': company})
                              

@login_required
def cv_personal_info(request):
    """
    View to display and update candidate's personal information.

    Supports AJAX requests to update and return JSON responses.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse or JsonResponse: Renders personal info form or returns JSON on AJAX POST.
    """
    candidate = get_object_or_404(Candidate, user=request.user)
    context={}
    context['success'] = False
    if request.method == 'POST':
        # try:
        #     state_selected = State.objects.get(pk=int(request.POST['state']))
        # except:
        #     state_selected = None

        form_candidate = CandidateForm(instance=candidate, data=request.POST, files=request.FILES)#, state_selected=state_selected)
        form_user_photo = UserPhotoForm(instance=candidate.user, data=request.POST, files=request.FILES)
        if form_candidate.is_valid():
            # raise ValueError()
            form_candidate.save()
            form_user_photo.save()
            context['msg'] = 'Profile Updated'
            context['success'] = True
            if is_ajax(request):
                return JsonResponse(context)
            else:
                return redirect('candidates_edit_curriculum')
        else:
            pass
    else:
        form_candidate = CandidateForm(instance=candidate)#, state_selected=candidate.state)
        form_user_photo = UserPhotoForm(instance=candidate.user)
    if not is_ajax(request):
        return render(request,'cv_personal_form.html',
                              {'isCV': True, 'form_candidate': form_candidate, 'form_user_photo': form_user_photo})

    else:
        return JsonResponse(context)


@login_required
def cv_objective(request):
    """
    View to display and update candidate's career objective statement.

    Handles POST submissions to save the objective and redirects to CV edit page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the objective form template.
    """
    candidate = get_object_or_404(Candidate, user=request.user)
    if request.method == 'POST':
        form_objective = ObjectiveForm(instance=candidate, data=request.POST, files=request.FILES)
        if form_objective.is_valid():
            form_objective.save()
            return redirect('candidates_edit_curriculum')
    else:
        form_objective = ObjectiveForm(instance=candidate)
        return render(request,'cv_objective_form.html',
                              {'isCV': True, 'form_objective': form_objective, 'objective': candidate.objective})
   


# @login_required
# def cv_courses(request):
#     candidate = get_object_or_404(Candidate, user=request.user)
#     if request.method == 'POST':
#         form_courses = CoursesForm(instance=candidate, data=request.POST, files=request.FILES)
#         if form_courses.is_valid():
#             form_courses.save()
#             return redirect('candidates_edit_curriculum')
#     else:
#         form_courses = CoursesForm(instance=candidate)
#     # print candidate.courses
#     return render_to_response('cv_courses_form.html',
#                               {'isCV': True, 'form_courses': form_courses, 'courses': candidate.courses},
#                               context_instance=RequestContext(request))


@login_required
def cv_expertise(request, expertise_id=None):
    """
    Handle adding or updating a candidate's expertise (work experience) entry.

    Args:
        request (HttpRequest): The HTTP request object.
        expertise_id (int, optional): ID of the expertise to update. If None, a new expertise is created.

    Returns:
        HttpResponse or JsonResponse: Returns a rendered form page for GET requests,
        redirects after successful POST, or returns JSON for AJAX calls.
    """
    candidate = get_object_or_404(Candidate, user = request.user)
    context={}
    context['success'] = False
    if expertise_id:
        expertise = get_object_or_404(Expertise, id=expertise_id, candidate=candidate)
        industry_selected = expertise.industry
        update = True
    else:
        expertise = None
        industry_selected = None
        update = False
    if request.method == 'POST':
        try:
            present = request.POST['present']
            present = True
        except:
            present = False
        try:
            industry_selected = Company_Industry.objects.get(id=request.POST['industry'])
        except Company_Industry.DoesNotExist:
            industry_selected = None
        form_expertise = ExpertiseForm(instance=expertise,
                                       data=request.POST,
                                       files=request.FILES,
                                       industry_selected=industry_selected,
                                       present=present,
                                       )
        if form_expertise.is_valid():
            expertise = form_expertise.save()
            expertise.candidate = candidate
            expertise.save()
            context['msg'] = 'Experience Updated'
            context['success'] = True
            context['id'] = expertise.id
            context['del_url'] = reverse('candidates_cv_delete_expertise', kwargs={'expertise_id':expertise.id})
            if is_ajax(request):
                return JsonResponse(context)
            else:
                return redirect('candidates_edit_curriculum')
        else:
            context['errors'] = form_expertise.errors
            return JsonResponse(context)
    else:
        form_expertise = ExpertiseForm(instance=expertise,
                                       industry_selected=industry_selected,
                                       update=update)
    if not is_ajax(request):
        return render(request,'cv_expertise_form.html',
                              {'isCV': True, 'form_expertise': form_expertise, 'update': update})
        
    else:
        return JsonResponse(context)

@login_required
def cv_academic(request, academic_id=None):
    """
    Handle adding or updating a candidate's academic entry.

    Args:
        request (HttpRequest): The HTTP request object.
        academic_id (int, optional): ID of the academic record to update. If None, a new record is created.

    Returns:
        HttpResponse or JsonResponse: Returns a rendered form page for GET requests,
        redirects after successful POST, or returns JSON for AJAX calls.
    """
    candidate = get_object_or_404(Candidate, user=request.user)
    context={}
    context['success'] = False
    if academic_id:
        academic = get_object_or_404(Academic, id=academic_id, candidate=candidate)
        area_selected = academic.area
        update = True
    else:
        academic = None
        area_selected = None
        update = False
    if request.method == 'POST':
        try:
            area_selected = Academic_Area.objects.get(pk=int(request.POST['area']))
        except:
            area_selected = None
        form_academic = AcademicForm(instance=academic,
                                      data=request.POST,
                                      files=request.FILES,
                                      area_selected=area_selected,
                                      )
        if form_academic.is_valid():
            academic = form_academic.save()
            academic.candidate = candidate
            # if academic.status.codename == 'progress':
            #     academic.present = True
            # else:
            #     academic.present = False
            academic.save()
            context['msg'] = 'Education Updated'
            context['success'] = True
            context['id'] = academic.id
            context['del_url'] = reverse('candidates_cv_delete_academic', kwargs={'academic_id':academic.id})
            if is_ajax(request):
                return JsonResponse(context)
            else:
                return redirect('candidates_edit_curriculum')
        else:
            context['errors'] = form_academic.errors
            return JsonResponse(context)
    else:
        form_academic = AcademicForm(instance=academic,
                                       area_selected=area_selected,
                                       update=update)
    if not is_ajax(request):
        return render(request,'cv_academic_form.html',
                              {'isCV': True, 'form_academic': form_academic, 'update': update})
        
    else:
        return JsonResponse(context)

@login_required
def cv_language(request):
    """
    Handle adding or updating multiple language proficiencies for the candidate via a formset.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the language formset page or redirects after successful POST.
    """
    candidate = get_object_or_404(Candidate, user = request.user)
    LanguageFormSet = modelformset_factory(CV_Language, max_num=5, extra=5, form=CvLanguageForm, can_delete=True)
    if request.method == 'POST':
        formset_languages = LanguageFormSet(request.POST, request.FILES, queryset=CV_Language.objects.filter(candidate=candidate))
        if formset_languages.is_valid():
            languages = formset_languages.save(commit=False)
            for language in languages:
                language.candidate = candidate
                language.save()
            return redirect('candidates_edit_curriculum')
    else:
        formset_languages = LanguageFormSet(queryset=CV_Language.objects.filter(candidate=candidate))
    return render(request,'cv_language_form.html',
                              {'isCV': True, 'formset_languages': formset_languages, })
    
@login_required
def cv_delete_item(request, expertise_id=None, academic_id=None, software_id=None):
    """
    Delete a candidate's expertise, academic, or software record.

    Args:
        request (HttpRequest): The HTTP request object.
        expertise_id (int, optional): ID of the expertise record to delete.
        academic_id (int, optional): ID of the academic record to delete.
        software_id (int, optional): ID of the software record to delete.

    Returns:
        HttpResponseRedirect: Redirects to the curriculum edit page after deletion.
    """
    candidate = get_object_or_404(Candidate, user = request.user)
    if expertise_id:
        expertise = get_object_or_404(Expertise, id=expertise_id, candidate=candidate)
        expertise.delete()
    if academic_id:
        academic= get_object_or_404(Academic, id=academic_id, candidate=candidate)
        academic.delete()
    if software_id:
        software = get_object_or_404(CV_Software, id=software_id, candidate=candidate)
        software.delete()
    return redirect(edit_curriculum)


def curriculum_to_pdf(request, candidate_id, template=None):
    """
    Generate and return a PDF of a candidate's full curriculum vitae.

    Args:
        request (HttpRequest): The HTTP request object.
        candidate_id (int): ID of the candidate whose CV will be generated.
        template (str, optional): Template to use for PDF rendering. Defaults to None.

    Returns:
        HttpResponse: PDF file response with the candidate's CV.
    """
    from django.template.loader import render_to_string
    from TRM.settings import MEDIA_URL

    candidate = get_object_or_404(Candidate, pk=candidate_id)
    academics = Academic.objects.filter(candidate=candidate)
    expertises = Expertise.objects.filter(candidate=candidate)
    languages = CV_Language.objects.filter(candidate=candidate)
    trainings = Training.objects.filter(candidate=candidate)
    certificates = Certificate.objects.filter(candidate=candidate)
    projects = Project.objects.filter(candidate=candidate)
    # softwares = CV_Software.objects.filter(candidate=candidate)
    today = datetime.now().date()
    logo_pdf = 'logos_TRM/logo_pdf.png'
    pdf_name = '%s_%s_%s.pdf' % (candidate.first_name, candidate.last_name, candidate.pk)
    html_string = render_to_string('curriculum_to_pdf.html',
                                    context={'user': request.user,
                                             'today': today,
                                             'candidate': candidate,
                                             'academics': academics,
                                             'expertises': expertises,
                                             'languages': languages,
                                             'trainings': trainings,
                                             'certificates': certificates,
                                             'projects': projects,
                                             # 'softwares': softwares,
                                             'MEDIA_URL': MEDIA_URL,
                                             'logo_pdf': logo_pdf,
                                    })
    
    # Generate PDF using WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % pdf_name
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
    return response

def create_candidates(request):
    """
    Automatically generate and create multiple candidate users with random profile data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to a test or confirmation page after bulk creation.
    """
    mex = Country.objects.get(iso2_code__iexact='IN')
    last_user_id = User.objects.last()
    start_range = last_user_id.pk + 1
    end_range = start_range + 500
    # print(start_range)
    # print(end_range)

    for x in range(start_range, end_range, 1):
        # User
        first_name = 'Auto Candidato %s' % str(x)
        last_name = 'Apellido %s' % str(x)
        email = 'autoemail%s@mail.com' % str(x)
        username = 'autocandidate%s' % str(x)
        password = 'pbkdf2_sha256$12000$O3GiWwQV0znu$1eUYIjXairxvkLJHUvHtn+cRlztA9D6m7nfawt/735w='
        logued_by = 'EL'
        candidate_profile = Profile.objects.get(codename='candidate')
        
        try:
            user = User.objects.create(username=username, password=password, first_name=first_name, last_name=last_name,
                                   email=email.lower(), is_active=True, logued_by=logued_by, profile=candidate_profile)
        except:
            user = User.objects.create(username=username+'3', password=password, first_name=first_name, last_name=last_name,
                                   email=email.lower(), is_active=True, logued_by=logued_by, profile=candidate_profile)
        # Candidate
        year = random.choice(list(range(1950, 2000)))
        month = random.choice(list(range(1, 12)))
        day = random.choice(list(range(1, 28)))
        birthday = datetime(year, month, day)
        gender = Gender.objects.get(id=random.randint(2, 3))
        maritalStatus = Marital_Status.objects.all().order_by('?')[0]
        state = 'State %s' % str(x)
        city = 'City %s' % str(x)
        travel = random.choice([True, False])
        residence = random.choice([True, False])
        min_salary = random.choice(list(range(5000, 10000)))
        max_salary = random.choice(list(range(10000, 80000)))
        objective = "Auto Objetivo Profesional %s Objetivo Profesional %s Objetivo Profesional %s" % (str(x), str(x), str(x))
        # courses = "Diplomado en procesos automaticos %s" % str(x)
        candidate = Candidate.objects.create(user=user, first_name=first_name, last_name=last_name,
                                             birthday=birthday, gender=gender, maritalStatus=maritalStatus,
                                             nationality=mex, state=state, city=city,
                                             min_salary=min_salary, max_salary=max_salary,
                                             travel=travel, residence=residence, objective=objective)

        for i in range(1, 3, 1):
            # Expertise
            company = 'Auto Empresa Numero %s - %s' % (str(x), str(i))
            industry = Company_Industry.objects.all().order_by('?')[0]
            # area =  Company_Area.objects.filter(company_industry=industry).order_by('?')[0]
            employment = 'Auto Puesto numero %s - %s' % (str(x), str(i))
            tasks = 'Auto Estas son las tareas del puesto numero %s - %s' % (str(x), str(i))
            start_date_year = random.choice(list(range(1964, 1980)))
            start_date_month = random.choice(list(range(1, 12)))
            start_date_day = random.choice(list(range(1, 28)))
            start_date = datetime(start_date_year, start_date_month, start_date_day)
            present = random.choice([True, False])
            end_date = None
            if not present:
                end_date_year = random.choice(list(range(1981, 2015)))
                end_date_month = random.choice(list(range(1, 12)))
                end_date_day = random.choice(list(range(1, 28)))
                end_date = datetime(end_date_year, end_date_month, end_date_day)
            Expertise.objects.create(candidate=candidate, company=company, industry=industry,
                                     country=mex, employment=employment, start_date=start_date,
                                     end_date=end_date, present=present, tasks=tasks)

            # Academic
            degree = Degree.objects.exclude(codename__iexact='indistinct').order_by('?')[0]
            # area = Academic_Area.objects.all().order_by('?')[0]
            # career = Academic_Career.objects.filter(area=area).order_by('?')[0]
            # if career.codename == 'other':
            #     other = 'Auto Otra Carrera %s' % str(x)
            # else:
            #     other = None
            status = Academic_Status.objects.all().order_by('?')[0]
            school = 'Auto Escuela %s - %s' % (str(x), str(i))
            # school_type = School_Type.objects.all().order_by('?')[0]
            start_date_year = random.choice(list(range(1964, 1996)))
            start_date_month = random.choice(list(range(1, 12)))
            start_date_day = random.choice(list(range(1, 28)))
            start_date = datetime(start_date_year, start_date_month, start_date_day)
            country = Country.objects.all().order_by('?')[0]
            present = random.choice([True, False])
            end_date = None
            if not present:
                end_date_year = random.choice(list(range(1981, 2014)))
                end_date_month = random.choice(list(range(1, 12)))
                end_date_day = random.choice(list(range(1, 28)))
                end_date = datetime(end_date_year, end_date_month, end_date_day)
            Academic.objects.create(candidate=candidate, degree=degree, status=status,
                                    school=school, country=country,
                                    start_date=start_date, end_date=end_date)

            # Language
            # language = Language.objects.all().order_by('?')[0]
            # level = Language_Level.objects.all().order_by('?')[0]
            # CV_Language.objects.create(candidate=candidate, language=language, level = level)

            # Software
            # software = Software.objects.all().order_by('?')[0]
            # level = Software_Level.objects.all().order_by('?')[0]
            # description = 'Auto Manejo de programa %s - %s' % (str(x), str(i))
            # CV_Software.objects.create(candidate=candidate, software=software, level=level, description=description)

        # Curriculum Advance
        academics = Academic.objects.filter(candidate=candidate)
        expertises = Expertise.objects.filter(candidate=candidate)
        languages = CV_Language.objects.filter(candidate=candidate)
        # softwares = CV_Software.objects.filter(candidate=candidate)
        curriculum, created = Curriculum.objects.get_or_create(candidate=candidate)
        if candidate.birthday and candidate.gender:
            curriculum.personal_info = True
        if candidate.objective:
            curriculum.objective = True
        if expertises:
            curriculum.expertise = True
        if academics:
            curriculum.academic = True
        if languages:
            curriculum.language = True
        """# if softwares:
        #     curriculum.software = True
        # Setting percentage completion of Curriculum"""
        curriculum.set_advance()
        curriculum.save()

    return redirect('test')


@login_required
def vacancies_postulated(request):
    """
    Display a candidate's postulated vacancies categorized by active, finalized, and rejected.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the vacancies_postulated page with categorized vacancies.
    """
    candidate = get_object_or_404(Candidate, user=request.user)
    active = False
    finalized = False
    vacancies_status = Vacancy_Status.objects.all()
    active_status = vacancies_status.get(codename='open')
    finalized_status = vacancies_status.get(codename='closed')
    postulates = Postulate.objects.filter(candidate=candidate)
    finalize_postulates = Postulate.objects.filter(candidate = candidate, discard = False, finalize = True, vacancy__status = finalized_status)
    active_postulates = Postulate.objects.filter(candidate = candidate, vacancy__status = active_status, discard = False)
    rejected_postulates = Postulate.objects.filter(Q(candidate = candidate, discard = True) | Q(candidate = candidate, vacancy__status = finalized_status, finalize = False))
    return render(request,
        'vacancies_postulated.html', {
            'isApplication': True,
            'active_postulates': active_postulates,
            'finalized_postulates': finalize_postulates,
            'rejected_postulates': rejected_postulates,
            'active_status':active_status,
            'finalized_status':finalized_status,
        }
      
    )


@login_required
def vacancies_favorites(request):
    """
    Display a candidate's favorite vacancies, removing any that have been applied to.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the vacancies_favorites page with updated favorite vacancies.
    """
    candidate = get_object_or_404(Candidate, user=request.user)
    candidate_favs = Candidate_Fav.objects.filter(candidate=candidate)
    applications = Postulate.objects.filter(candidate = candidate)
    for application in applications:
        for fav in candidate_favs:
            if fav.vacancy == application.vacancy:
                fav.delete()
    candidate_favs = Candidate_Fav.objects.filter(candidate=candidate)
    return render(request,'vacancies_favorites.html',
                              {'candidate_favs': candidate_favs,
                              'isFav': True})
                            
