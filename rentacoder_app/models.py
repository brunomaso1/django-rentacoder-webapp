import logging
from random import randint
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction, IntegrityError
from django.utils import timezone

import rentacoder_app.constants as const
import rentacoder_app.errors as err
from rentacoder_app.common import default_expiration_delta
from rentacoder_app.email_manager import EmailManager

log = logging.getLogger(__name__)


class Technology(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "technology"

    def __str__(self):
        return self.name


# A User can publish Projects and create JobOffers in Projects
class User(AbstractUser):
    """
    Attributes of Base User:
        first_name
        last_name
        username
        password
    """
    technologies = models.ManyToManyField('Technology')
    avatar = models.ImageField(upload_to='avatars', default=const.DEFAULT_PROFILE_IMAGE_USER)
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Save user and if user is superuser, activate it.
        """
        if not self.id and self.is_superuser:
            self.is_active = True
        super(User, self).save(*args, **kwargs)

    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email
        :param str email: Email to lookup
        :return User: User instance
        """
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            log.debug('There is no user with email %s' % email)
        return user

    @staticmethod
    def get_user_by_username(username):
        """
        Get user by username
        :param str username: Username to lookup
        :return User: User instance
        """
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            log.debug('There is no user with username %s' % username)
        return user

    @staticmethod
    def free_account(username, email):
        """
        Given a username and email the method deletes account if they are not active
        :param str username: The username to lookup
        :param str email: The email to lookup
        :return: Account free or not and list of errors
        """
        # get users by email and user (could be the same or not)
        user_username = User.get_user_by_username(username)
        user_email = User.get_user_by_email(email)

        # initialize errors list and set username and email free as default
        errors = []
        free_username = True
        free_email = True

        # if the user with username exists and is active
        # append error
        if user_username and user_username.is_active:
            free_username = False
            errors.append(err.Error(err.ERROR_USERNAME_IN_USE))

        # if the user with email exists and is active
        # append error
        if user_email and user_email.is_active:
            free_email = False
            errors.append(err.Error(err.ERROR_EMAIL_IN_USE))

        # if the user with username exists but is not active delete it
        if free_username and user_username:
            user_username.delete()

        # if the user with email exists but is not active delete it
        if free_email and user_email:
            user_email.delete()

        return free_email and free_username, errors

    @staticmethod
    def register(username, first_name, last_name, email, password):
        """
        Method to register a new user into the system
        :param str username: Username
        :param str first_name: First name
        :param str last_name: Last name
        :param str email: Email
        :param str password: The password
        :return: User instance if created and errors if any
        """
        user = None
        errors = [err.Error(err.ERROR_UNKNOWN)]
        try:
            with transaction.atomic():
                # if user is not free then we return empty user

                # try to free the username and email
                user_free, errors = User.free_account(username, email)

                # if username and email are free then create the user
                if user_free:
                    user = User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                    )
                    # create account verification token and assign it to user
                    EmailToken.objects.create(user=user)
                    EmailManager.activate_account_email(user)
        except IntegrityError as e:
            # if this exception should be triggered if user was already in use in Token
            # or if some user param was not unique
            log.error('Error creating user: %s' % e)
        except Exception as e:
            # probably DB not found
            log.critical('Unknown error creating user: %s' % e)

        return user, errors

    def activate(self):
        """
        Activates user
        """
        self.is_active = True
        self.save()

    def recover_password(self):
        """
        Start recover password flow:
        Create token
        Send email with recover password link
        """
        try:
            # create new token used for validation
            token = ResetPasswordToken.objects.create(user=self)
        except IntegrityError:
            ResetPasswordToken.objects.get(user=self).delete()
            token = ResetPasswordToken.objects.create(user=self)

        # assign token here to avoid additional query in send email
        self.reset_password_token = token

        # send email with link to recover password to user
        EmailManager.send_reset_password_email(self)

    @staticmethod
    def update_password(token_value, password):
        """
        Check if token is valid and update password
        :param token_value: The reset password validation token
        :param password: The new password
        :return: Password updated or not
        """
        updated = False
        errors = []
        try:
            token = ResetPasswordToken.objects.select_related('user').get(value=token_value)
            if token.is_valid():
                with transaction.atomic():
                    # update user password if the password is valid
                    if token.user.check_password(password):
                        token.user.set_password(password)
                        token.user.save()
                        token.delete()
                        updated = True
                    else:
                        log.debug('Invalid new password for user %s' % token.user.username)
                        errors.append(err.Error(err.ERROR_INVALID_PASSWORD))
        except ResetPasswordToken.DoesNotExist:
            log.error('Trying to reset password with non existent token %s' % token_value)
            errors.append(err.Error(err.ERROR_TOKEN_NOT_VALID))
        return updated, errors


class Token(models.Model):
    """
    Used to validate account
    """
    value = models.UUIDField(default=uuid4, editable=False, unique=True, db_index=True)
    expiry_date = models.DateTimeField(default=default_expiration_delta, editable=False)
    user = models.OneToOneField(to='User', unique=True, editable=False)

    def is_valid(self):
        """
        Checks token expiration
        :return: Token expired or not
        """
        return self.expiry_date >= timezone.now()

    class Meta:
        abstract = True


# A Project is created by a User and can offer one or more job openings
class Project(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    technologies = models.ManyToManyField('Technology')
    openings = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    # duration: calculated in days, weeks, months?

    class Meta:
        db_table = "project"

    @staticmethod
    def generate(number=1):
        last_project = Project.objects.last()
        next_id = (last_project and last_project.pk + 1) or 1
        for n in range(number):
            date = timezone.now()
            Project.objects.create(title="Project %i" % next_id, description=uuid4(),
                                   user_id=1, openings=randint(1, 10),
                                   start_date=date, end_date=date)
            next_id += 1


# Users can post JobOffers for a Project
class JobOffer(models.Model):
    project = models.ForeignKey('Project')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.IntegerField()
    hours = models.IntegerField()
    message = models.TextField()

    class Meta:
        db_table = "job_offer"


class ProjectQuestion(models.Model):
    project = models.ForeignKey('Project')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()


class ResetPasswordToken(Token):
    """
    Used to reset password
    """
    user = models.OneToOneField(to='User', unique=True, editable=False, related_name='reset_password_token')


class EmailToken(Token):
    """
    Used to validate email and activate account
    """
    email = models.EmailField()
    user = models.OneToOneField(to='User', unique=True, editable=False, related_name='email_token')
