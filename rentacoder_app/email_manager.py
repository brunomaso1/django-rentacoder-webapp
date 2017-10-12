import logging
import urllib.parse
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.urls import reverse

logger = logging.getLogger(__name__)


class EmailManager:

    @staticmethod
    def activate_account_email(user):
        """
        Sends an email to the user with a link to activate account
        :param user: The user to activate
        """
        try:

            html_message = loader.render_to_string(
                'email/register_email.html',
                {
                    'user_name': user.first_name,
                    'url_token': urllib.parse.urljoin(settings.DOMAIN,
                                                      reverse('validate_email_token', args=(user.email_token.value,))),
                }
            )

            send_mail(
                subject='Welcome!',
                message='',
                from_email='',
                recipient_list=(user.email,),
                fail_silently=False,
                html_message=html_message
            )
        except SMTPException as e:
            logger.error('Error sending registration email to %s-%s. %s' % (user.id, user.username, e))
        except AttributeError as e:
            logger.error('Error obtaining token of %s-%s. %s' % (user.id, user.username, e))

    @staticmethod
    def send_reset_password_email(user):
        """
        Sends an email to the given user, with a link to recover password
        :param user: The user to recover the password
        """
        try:
            url = urllib.parse.urljoin(settings.DOMAIN,
                                       reverse('recover_password_get', args=[str(user.reset_password_token.value)]))

            # render template
            html_message = loader.render_to_string(
                'email/reset_password.html',
                {
                    'user_first_name': user.first_name.capitalize(),
                    'url_token': url,
                }
            )

            logger.debug('Email template rendered')

            send_mail(
                subject='Reset password',
                message='',
                from_email='',
                recipient_list=(user.email,),
                fail_silently=False,
                html_message=html_message
            )
            logger.debug('Email sent to %s' % user.email)
        except SMTPException as e:
            logger.error('Error sending recover password email to %s-%s. %s' % (user.id, user.username, e))
        except AttributeError as e:
            logger.error('Error obtaining token of %s-%s. %s' % (user.id, user.username, e))
