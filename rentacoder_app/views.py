from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.template import loader

import logging

from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import ResetPasswordForm, RegisterForm, NewProjectForm, ApplyToProjectForm, UserProfileForm, \
    ProjectQuestionForm, AnswerQuestionForm
from .models import User, Project, Technology, ProjectQuestion
from .views_helper import verify_registration_token
import rentacoder_app.errors as err

log = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'


@login_required
def portal(request):
    projects_last_all = Project.objects.order_by('-id')
    projects_top = Project.objects.all()[:7]
    # projectsRecomended = Project.objects.filter(technologies__headline__conatins='Java')
    projects_recomended = Project.objects.all()[:14:2]
    page = request.GET.get('page', 1)

    paginator_last = Paginator(projects_last_all, 5)
    try:
        projects_last = paginator_last.page(page)
    except PageNotAnInteger:
        projects_last = paginator_last.page(1)
    except EmptyPage:
        projects_last = paginator_last.page(paginator_last.num_pages)

    context = {
        "projectsLast": projects_last,
        "projectsTop": projects_top,
        "projectsRecomended": projects_recomended
    }
    return render(request, 'views/portal.html', context)


@login_required
def my_projects(request):
    projects_last_all = Project.objects.filter(user=request.user).order_by('-id')
    projects_top = Project.objects.filter(user=request.user)
    page = request.GET.get('page', 1)

    paginator_last = Paginator(projects_last_all, 5)
    try:
        projects_last = paginator_last.page(page)
    except PageNotAnInteger:
        projects_last = paginator_last.page(1)
    except EmptyPage:
        projects_last = paginator_last.page(paginator_last.num_pages)

    context = {
        "projectsLast": projects_last,
        "projectsTop": projects_top,
    }
    return render(request, 'views/my_projects.html', context)


@login_required
def profile(request):
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == GET:
        return render(request, 'views/profile.html', {'form': form})
    elif request.method == POST:
        if form.is_valid():
            log.info("Updating user {}".format(request.user.username))
            form.save()
            return redirect(reverse('profile'))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

    return render(request, 'views/edit_project.html', {'form': form})


@login_required
def new_project(request):
    log.info(request.user)
    if request.method == GET:
        return render(request, 'views/new_project.html', {'form': NewProjectForm()})
    elif request.method == POST:
        # create form from request POST params
        form = NewProjectForm(request.POST)

        # check if the form is valid
        if form.is_valid():
            # try to create the project
            log.info("Creating project by user {}".format(request.user))
            technologies = form.cleaned_data.pop('technologies')
            form.user_id = request.user.pk
            project = form.save(commit=False)
            project.user_id = request.user.pk
            project.save()

            for tech_name in technologies:
                technology = Technology.objects.get(name=tech_name)
                project.technologies.add(technology)

            return redirect(reverse('project', kwargs={"pk": project.pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors))
            messages.error(request, 'Invalid form data')

        return HttpResponse('')


@login_required
def project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    job_offers = project.joboffer_set.all()
    context = {
        "project": project,
        "job_offers": job_offers,
        "technologies": list(project.technologies.all().values_list("name", flat=True)),
        "own_project": request.user == project.user,
        "questions": project.projectquestion_set.all(),  # TODO: Private questions, private answers
        "question_form": ProjectQuestionForm(),
        "answer_form": AnswerQuestionForm(),
        "already_applied": job_offers.filter(user=request.user).exists(),
    }
    return render(request, 'views/project.html', context)


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.user != request.user:
        return HttpResponseForbidden()

    form = NewProjectForm(request.POST or None, instance=project)
    if request.method == GET:
        context = {
            "form": form,
            "project": Project.objects.get(pk=int(pk))
        }
        return render(request, 'views/edit_project.html', context)
    else:
        if form.is_valid():
            form.save()
            return redirect(reverse('project', kwargs={"pk": pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

    return render(request, 'views/edit_project.html', {'form': form})


@login_required
def apply_to_project(request, pk):
    if request.method == GET:
        form = ApplyToProjectForm()
        context = {
            "form": form,
            "project": Project.objects.get(pk=int(pk))
        }
        return render(request, 'views/apply_to_project.html', context)
    else:
        log.info("Attempting to create JobOffer for project {} by user {} - Request: {}".
                 format(pk, request.user, request.POST))
        form = ApplyToProjectForm(request.POST)
        if form.is_valid():
            form.user_id = request.user.pk
            form.project_id = pk
            job_offer = form.save(commit=False)
            job_offer.user_id = request.user.pk
            job_offer.project_id = pk
            job_offer.save()

            return redirect(reverse('project', kwargs={"pk": pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

            return redirect(reverse('apply'))


def send_question(request, pk):
    if request.method == POST:
        log.info("Attempting to send question for project {} by user {} - Request: {}".
                 format(pk, request.user, request.POST))
        form = ProjectQuestionForm(request.POST)
        if form.is_valid():
            form.user_id = request.user.pk
            form.project_id = pk
            question = form.save(commit=False)
            question.user_id = request.user.pk
            question.project_id = pk
            question.save()
            return redirect(reverse('project', kwargs={"pk": pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')
            return redirect(reverse('project'), kwargs={"pk": pk})


def answer_question(request, pk, question_id):
    if request.method == POST:
        log.info("Attempting to answer question {} for project {} by user {} - Request: {}".
                 format(question_id, pk, request.user, request.POST))
        form = AnswerQuestionForm(request.POST)
        if form.is_valid():
            question = ProjectQuestion.objects.get(pk=question_id)
            question.answer = form.cleaned_data.get('answer')
            question.save()
            return redirect(reverse('project', kwargs={"pk": pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')
            return redirect(reverse('project'), kwargs={"pk": pk})


def register(request):
    """
    View used to register a new user
    :param request:
    """
    if request.method == GET:
        # create form to render and return it
        form = RegisterForm()
        return render(request, 'views/register.html', {'form': form})
    elif request.method == POST:
        # create form from request POST params
        form = RegisterForm(request.POST)
        template = 'views/validation_template.html'
        context = {'title': 'Success', 'message': 'Great! Your account was created, now please check your email to '
                                                  'activate your account.'}
        # check if the form is valid
        if form.is_valid():
            # try to create an user
            form.cleaned_data.pop('password_confirmation')
            user, errors = User.register(**form.cleaned_data)
            if user:
                # render success
                return render(request, template, context)
            else:
                # show errors and redirect to register form
                for error in errors:
                    messages.error(request, error.text)
                return redirect(reverse('register'))
        else:
            # show errors and redirect to form
            messages.error(request, 'Invalid form data')
            response = redirect(reverse('register'))
        return response


def reset_password(request, token=None):
    """
    View used to reset password
    :param request: Django request object
    :param token: Token object used to validate password reset
    :return: HTML template
    """
    # GET requests
    if request.method == GET:
        # render page with reset password form
        form = ResetPasswordForm(initial={'token': token})
        return render(request, 'views/reset_password.html', {'form': form})
    # POST request
    elif request.method == POST:
        template = 'views/validation_template.html'
        context = {'title': 'Success', 'message': 'Your password was changed.'}
        # get data from form and reset password
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token_value = form.cleaned_data.get('token')
            updated, errors = User.update_password(token_value, form.cleaned_data.get('password1'))
            if updated:
                # password was updated
                response = render(request, template, context)
            else:
                # show errors and redirect to form
                for error in errors:
                    messages.error(request, error.text)
                response = redirect(reverse('reset_password_get', args=[request.POST.get('token', '')]))
        else:
            # show errors and redirect to form
            messages.error(request, err.Error(err.ERROR_RESET_PASSWORD_NOT_MATCH).text)
            response = redirect(reverse('reset_password_get', args=[request.POST.get('token', '')]))
        return response


def validate_email(request, token):
    verified, error = verify_registration_token(token)
    template = 'views/validation_template.html'

    if verified:
        msg = "This process was done correctly."
        return render(request, template, {'title': 'Success!', 'message': msg})
    else:
        return render(request, template, {'title': 'Ops!, error:', 'message': error.text})
