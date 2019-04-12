from django.conf.urls import url
from . import views

app_name='recognition';

urlpatterns = [
    url('forgotpassword/', views.forgot, name='forgotpassword'),
    url('signup/', views.signup, name='signup'),
    url('evaluate/', views.evaluate, name='evaluate'),
    url('questionbank/', views.question, name='question'),
    url('homepage/', views.homepage, name='homepage'),
    url('questionseries/', views.questionseries, name='qs'),
    url('result/', views.result, name='result'),
    url('userprofile/', views.userprofile, name='userprofile'),
    url('^$', views.login, name='login'),
]

