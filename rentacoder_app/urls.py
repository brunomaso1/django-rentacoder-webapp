from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'views/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/$', views.my_profile, name='my_profile'),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.user_profile, name='user_profile'),

    url(r'^(?P<token>[0-9a-f-]+)/$', views.validate_email, name='validate_email_token'),
    url(r'reset_password/$', views.reset_password, name='reset_password_post'),
    url(r'reset_password/(?P<token>[0-9a-f-]+)/$', views.reset_password, name='reset_password_get'),

    url(r'^$', views.portal, name='portal'),
    url(r'^projects/$', views.my_projects, name='my_projects'),
    url(r'^projects/new/$', views.new_project, name='new_project'),
    url(r'^projects/(?P<pk>[0-9]+)/$', views.project, name='project'),
    url(r'^projects/(?P<pk>[0-9]+)/apply/$', views.apply_to_project, name='apply'),
    url(r'^projects/(?P<pk>[0-9]+)/edit/$', views.edit_project, name='edit'),
    url(r'^projects/(?P<pk>[0-9]+)/questions/$', views.send_question, name='send_question'),
    url(r'^projects/(?P<pk>[0-9]+)/questions/(?P<question_id>[0-9]+)$', views.answer_question, name='answer_question'),
    url(r'^projects/(?P<pk>[0-9]+)/accept_job_offer/(?P<offer_id>[0-9]+)$', views.accept_job_offer, name='accept_job_offer'),

    url(r'^applications/$', views.applications, name='my_applications'),

    url(r'^scores/$', views.scores, name='scores'),

    url(r'^history/$', views.history, name='history'),
    url(r'^projects/(?P<pk>[0-9]+)/close/$', views.close_project, name='close_project'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)