from django.conf.urls import url
from . import views

app_name='recognition';

urlpatterns = [
    url(r'^forgotpassword/$', views.forgot, name='forgotpassword'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^evaluate/$', views.evaluate, name='evaluate'),
    url(r'^questionbank/$', views.question, name='question'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^questionseries/$', views.questionseries, name='qs'),
    url(r'^student/$', views.view_student, name='view_student'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
    url(r'^results/$', views.results, name='results'),
    url('^$', views.login, name='login'),
]

