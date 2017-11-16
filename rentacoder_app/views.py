from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader

import logging

from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import ResetPasswordForm, RegisterForm, NewProjectForm, ApplyToProjectForm, UserProfileForm, \
    ProjectQuestionForm, AnswerQuestionForm, ScoreForm
from .models import User, Project, Technology, ProjectQuestion, JobOffer, ProjectScore
from .views_helper import verify_registration_token
import rentacoder_app.errors as err

log = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'


@login_required
def portal(request):
    projects_last_all = Project.objects.filter(closed=False).order_by('-id')
    page = request.GET.get('page', 1)

    paginator_last = Paginator(projects_last_all, 5)
    try:
        projects_last = paginator_last.page(page)
    except PageNotAnInteger:
        projects_last = paginator_last.page(1)
    except EmptyPage:
        projects_last = paginator_last.page(paginator_last.num_pages)

    context = {
        "projectsLast": projects_last
    }
    return render(request, 'views/portal.html', context)


@login_required
def my_projects(request):
    projects = Project.objects.filter(user=request.user)
    active_projects = projects.filter(closed=False).order_by('-id')
    closed_projects = projects.filter(closed=True).order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(active_projects, 5)
    try:
        active_projects = paginator.page(page)
    except PageNotAnInteger:
        active_projects = paginator.page(1)
    except EmptyPage:
        active_projects = paginator.page(paginator.num_pages)

    context = {
        "active_projects": active_projects,
        "closed_projects": closed_projects
    }
    return render(request, 'views/my_projects.html', context)


@login_required
def my_profile(request):
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    user = request.user
    context = {
        "form": form,
        "userTechnologies": user.technologies.all()
    }
    if request.method == GET:
        return render(request, 'views/my_profile.html', context)
    elif request.method == POST:
        if form.is_valid():
            log.info("Updating user {}".format(request.user.username))
            form.save()
            messages.success(request, 'User updated successfully')
            return redirect(reverse('my_profile'))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

    return render(request, 'views/my_profile.html', context)


@login_required
def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    context = {
        "profile": user,
        "profileTechnologies": user.technologies.all()
    }
    return render(request, 'views/user_profile.html', context)


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
        "openings_available": project.openings - len(job_offers.filter(accepted=True)),
        "technologies": list(project.technologies.all().values_list("name", flat=True)),
        "questions": project.projectquestion_set.all(),  # TODO: Private questions, private answers
        "question_form": ProjectQuestionForm(),
        "answer_form": AnswerQuestionForm(),
        "already_applied": job_offers.filter(user=request.user).exists(),
        "accepted": job_offers.filter(user=request.user, accepted=True).exists(),
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
    project = get_object_or_404(Project, pk=pk)
    job_offers = project.joboffer_set.all()
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
            if job_offers.filter(user=request.user).exists():
                log.error("Invalid form data: {}".format(form.errors.as_json()))
                messages.error(request, 'Already applied to this project.')
                return redirect(reverse('apply', kwargs={"pk": pk}))
            else:
                job_offer = form.save(commit=False)
                job_offer.user_id = request.user.pk
                job_offer.project_id = pk
                job_offer.save()
                log.info("User {} is now an applicant for Proyect {}".format(request.user, pk))

                # Send mail to user
                project = Project.objects.get(pk=pk)
                html_message = loader.render_to_string(
                    'email/you_applied_to_project.html',
                    {
                        'user_name': request.user.username,
                        'project': project,
                        'project_url': project.get_url()
                    }
                )
                try:
                    send_mail(
                        subject="Applied to Project {}!".format(project.title),
                        message='',
                        from_email='',
                        recipient_list=(request.user.email,),
                        fail_silently=False,
                        html_message=html_message
                    )
                except Exception as e:
                    log.exception("Problem sending email: {}".format(e))

                # Send mail to owner
                html_message = loader.render_to_string(
                    'email/coder_applied_to_project.html',
                    {
                        'user_name': project.user.username,
                        'coder_name': request.user.username,
                        'project': project,
                        'project_url': project.get_url()
                    }
                )
                try:
                    send_mail(
                        subject="Coder Applied to Project {}!".format(project.title),
                        message='',
                        from_email='',
                        recipient_list=(project.user.email,),
                        fail_silently=False,
                        html_message=html_message
                    )
                except Exception as e:
                    log.exception("Problem sending email: {}".format(e))


                return redirect(reverse('project', kwargs={"pk": pk}))
        else:
            log.error("Invalid form data: {}".format(form.errors.as_json()))
            messages.error(request, 'Invalid form data')

            return redirect(reverse('apply', kwargs={"pk": pk}))


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

            # Send mail to owner
            project = Project.objects.get(pk=pk)
            html_message = loader.render_to_string(
                'email/question_asked.html',
                {
                    'user_name': project.user.username,
                    'project': project,
                    'project_url': project.get_url()
                }
            )
            try:
                send_mail(
                    subject="Someone asked something in Project {}!".format(project.title),
                    message='',
                    from_email='',
                    recipient_list=(project.user.email,),
                    fail_silently=False,
                    html_message=html_message
                )
            except Exception as e:
                log.exception("Problem sending email: {}".format(e))


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

            # Send mail to whoever asked the question
            project = Project.objects.get(pk=pk)
            html_message = loader.render_to_string(
                'email/question_answered.html',
                {
                    'user_name': question.user,
                    'project': project,
                    'project_url': project.get_url()
                }
            )
            try:
                send_mail(
                    subject="Question answered for Project {}!".format(project.title),
                    message='',
                    from_email='',
                    recipient_list=(question.user.email,),
                    fail_silently=False,
                    html_message=html_message
                )
            except Exception as e:
                log.exception("Problem sending email: {}".format(e))

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

@login_required
def accept_job_offer(request, pk, offer_id):
    if request.method == POST:
        log.info("Attempting to accept offer  {} for project {} by user {} - Request: {}".
                 format(offer_id, pk, request.user, request.POST))
        offer = JobOffer.objects.get(pk=offer_id)
        offer.accepted = True
        offer.save()

        # Send mail to user
        project = Project.objects.get(pk=pk)
        html_message = loader.render_to_string(
            'email/application_accepted.html',
            {
                'user_name': offer.user.username,
                'project': project,
                'project_url': project.get_url()
            }
        )
        try:
            send_mail(
                subject="Accepted in Project {}!".format(project.title),
                message='',
                from_email='',
                recipient_list=(offer.user.email,),
                fail_silently=False,
                html_message=html_message
            )
        except Exception as e:
            log.exception("Problem sending email: {}".format(e))

        return redirect(reverse('project', kwargs={"pk": pk}))

@login_required
def scores(request):
    context = {
        "pending_scores": ProjectScore.get_pending_scores_for_user(request.user),
        "coder_scores": ProjectScore.objects.filter(coder=request.user),
        "owner_scores": ProjectScore.objects.filter(project__user=request.user),
        "score_form": ScoreForm()
    }
    return render(request, 'views/scores.html', context)

@login_required
def applications(request):
    context = {
        "applications": JobOffer.objects.filter(user=request.user)
    }
    return render(request, 'views/my_applications.html', context)

@login_required
def history(request):
    context = {
        "projects": Project.objects.filter(user=request.user, closed=True).order_by("-id")
    }
    return render(request, 'views/history.html', context)

@login_required
def close_project(request, pk):
    if request.method == POST:
        log.info("Attempting to close project  {} by user {} - Request: {}".
                 format(pk, request.user, request.POST))
        project = Project.objects.get(pk=pk)
        project.closed = True
        project.save()

        # Create pending score instances for each accepted coder and send mail to everyone
        project = Project.objects.get(pk=pk)
        for offer in project.joboffer_set.filter():
            if offer.accepted:
                ProjectScore.objects.create(project_id=pk, coder=offer.user)

            # Send mail to coder
            html_message = loader.render_to_string(
                'email/project_closed.html',
                {
                    'user_name': offer.user.username,
                    'project': project,
                    'scores_url': ProjectScore.get_url(),
                    'accepted': offer.accepted
                }
            )
            try:
                send_mail(
                    subject="Project {} closed!".format(project.title),
                    message='',
                    from_email='',
                    recipient_list=(offer.user.email,),
                    fail_silently=False,
                    html_message=html_message
                )
            except Exception as e:
                log.exception("Problem sending email: {}".format(e))

        return render(request, 'views/my_projects.html')


def score_coder(request, pk):
    score_object = ProjectScore.objects.get(pk=pk)
    score_object.coder_score = request.POST.get('score')
    score_object.save()
    log.info("Owner {} rated Coder {}: {}".format(request.user, score_object.coder, score_object.coder_score))
    return redirect(reverse('scores'))


def score_owner(request, pk):
    score_object = ProjectScore.objects.get(pk=pk)
    score_object.owner_score = request.POST.get('score')
    score_object.save()
    log.info("Coder {} rated Owner {}: {}".format(request.user, score_object.project.user, score_object.owner_score))
    return redirect(reverse('scores'))
