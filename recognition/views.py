from django.shortcuts import render

# Create your views here.


def forgot(request):
    return render(request, 'recognition/forgotpassword.html')



def login(request):
    return render(request, 'recognition/Sign_in.html')


def signup(request):
    return render(request, 'recognition/signup.html')


def evaluate(request):
    return render(request, 'recognition/evaluate.html')


def question(request):
    return render(request, 'recognition/question.html')


def homepage(request):
    return render(request, 'recognition/homepage.html')


def add_student(request):
    return render(request, 'recognition/add_student.html')


def questionseries(request):
    return render(request, 'recognition/questionseries.html')


def userprofile(request):
    return render(request, 'recognition/userprofile.html')