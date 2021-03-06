from django.conf.urls import url
from . import views

app_name='recognition';

urlpatterns = [
    url(r'^reset-password/$', views.ResetPasswordRequestView, name='reset_password'),
    url(r'^reset_password_confirm/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$', views.PasswordResetConfirmView,name='reset_password_confirm'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^evaluate/$', views.evaluate, name='evaluate'),
    url(r'^questionbank/$', views.question, name='question'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^questionseries/$', views.questionseries, name='qs'),
    url(r'^student/$', views.view_student, name='view_student'),
    url(r'^userprofile/$', views.userprofile, name='userprofile'),
    url(r'^results/$', views.results, name='results'),
    url(r'^answerkeys/$',views.answerkeys, name='answerkeys'),
    url(r'^logout/$', views.logout, name="logout"),
    url('^$', views.login, name='login'),
]

