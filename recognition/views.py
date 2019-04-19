from django.shortcuts import render, render_to_response
from django.template import RequestContext
from .forms import UploadQuestionBank
from .models import QuestionBank
from django.http import HttpResponse
# Create your views here.


def forgot(request):
    return render(request, 'recognition/forgotpassword.html')



def login(request):
    return render(request, 'recognition/Sign_in.html')


def signup(request):
    return render(request, 'recognition/signup.html')


def evaluate(request):
    values = QuestionBank.objects.filter()
    form = request.POST
    if request.method == 'POST':
        return render(request, "recognition/success.html")
    return render_to_response('recognition/evaluate.html', {'items': values} )



def question(request):
    if request.method == 'POST':
        form = UploadQuestionBank(request.POST, request.FILES)
        if form.is_valid():
            class1 = form.cleaned_data['class1']
            qseries = form.cleaned_data['qseries']
            number = form.cleaned_data['number']
            question_paper = form.cleaned_data['question_paper']
            args = {'class1':class1, 'qseries':qseries, 'number':number,'qp':question_paper}

            return render(request, "recognition/success.html", args)

        else:
            form = UploadQuestionBank()
            return render(request, "recognition/homepage.html", {'form': form})
    else:
        form = UploadQuestionBank()
        return render(request, "recognition/question.html", {'form':form})
    #return render(request, 'recognition/question.html')


def homepage(request):
    return render(request, 'recognition/homepage.html')


def add_student(request):
    return render(request, 'recognition/add_student.html')


def questionseries(request):
    return render(request, 'recognition/questionseries.html')


def userprofile(request):
    return render(request, 'recognition/userprofile.html')