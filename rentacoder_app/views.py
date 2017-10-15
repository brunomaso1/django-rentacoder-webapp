from django.http import HttpResponse
from django.template import loader

import logging

from django.contrib import messages

from django.shortcuts import render, redirect
from django.urls import reverse

from rentacoder_app.forms.register import RegisterForm
from .forms.reset_password import ResetPasswordForm
from .models import User
from .views_helper import verify_registration_token
import rentacoder_app.errors as err

log = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'


def portal(request):
    template = loader.get_template('views/portal.html')
    return HttpResponse(template.render())


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
