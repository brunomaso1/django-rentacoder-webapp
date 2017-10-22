from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'views/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^(?P<token>[0-9a-f-]+)/$', views.validate_email, name='validate_email_token'),
    url(r'reset_password/$', views.reset_password, name='reset_password_post'),
    url(r'reset_password/(?P<token>[0-9a-f-]+)/$', views.reset_password, name='reset_password_get'),

    url(r'^$', views.portal, name='portal'),
    url(r'^new_project/$', views.new_project, name='new_project'),
    url(r'^project/(?P<pk>[0-9]+)/$', views.project, name='project'),
]