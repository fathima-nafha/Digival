from django.shortcuts import render, render_to_response
from django.template import RequestContext
from .forms import UploadQuestionBank
from .models import QuestionBank,AddStudent, Student,Teacher,QuestionPaper, AddQuestionBank
from django.http import HttpResponse
from .recognize import recognize, evaluate_paper
# Create your views here.


def forgot(request):
    return render(request, 'recognition/forgotpassword.html')



def login(request):
    return render(request, 'recognition/Sign_in.html')


def signup(request):
    return render(request, 'recognition/signup.html')


def evaluate(request):
    qp_series_fromdb = QuestionPaper.objects.filter()
    teacher = Teacher.objects.get(pk=1)
    all_records = Student.objects.all()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        qp_series = request.POST['qseries']
        qb_class = request.POST['class']
        qb_roll = request.POST['s_rollno']
        student = Student.objects.get(s_rollno=qb_roll)
        answer_paper = request.FILES['answer']
        answer_model = AddStudent.objects.create(teacher=teacher, student=student, answer_paper = answer_paper)
        url = 'media/' + str(qb_roll) + '/' + answer_paper.name
        results = recognize(url)
        if results != -1:
            db_answer = dict()
            answers = QuestionBank.objects.filter(qb_class = qb_class, qb__qp_series = qp_series).distinct()
            for every in answers:
                db_answer[every.qb_qno] = every.qb_answers
            test_score = evaluate_paper(results, db_answer)
            args = {'1': qp_series, '2': qb_class, '3': qb_roll, 'url': url, 'results': results, 'score' : test_score, 'a':db_answer}
            return render(request, 'recognition/success.html', args)

        else:
            answer_model.answer_paper.delete()
            answer_model.delete()
            return render(request, 'recognition/evaluate.html',
                          {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records,
                           'messages': 'Unable to identify characters in the image! Please try again'})

    return render(request, 'recognition/evaluate.html',
                  {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records, 'messages': ''})


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