from django.shortcuts import render, render_to_response
from django.template import RequestContext
from .forms import UploadQuestionBank, RegisterForm
from .models import QuestionBank,AddStudent, Student,Teacher,QuestionPaper, AddQuestionBank
from .recognize import recognize, evaluate_paper
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login

# Create your views here.



def forgot(request):
    return render(request, 'recognition/forgotpassword.html')


def login(request):
    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Save session as cookie to login the user
            auth_login(request,user)

            # Success, now let's login the user.
            return render(request, 'recognition/homepage.html')
        else:
            # Incorrect credentials, let's throw an error to the screen.
            return render(request, 'recognition/Sign_in.html',
                          {'error_message': 'Incorrect username and / or password.'})
    else:
        # No post data availabe, let's just show the page to the user.
        return render(request, 'recognition/Sign_in.html')


def signup(request):
    template = 'recognition/signup.html'

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Username already exists.'
                })
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Email already exists.'
                })
            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Passwords do not match.'
                })
            else:
                # Create the user:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.phone_number = form.cleaned_data['phone_number']
                user.save()

                f_name = form.cleaned_data['first_name']
                l_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']


                # Login the user
                auth_login(request, user)
                teacher = Teacher.objects.create(t_name=f_name + l_name, t_email=email)
                # redirect to accounts page:
                return render(request, 'recognition/Sign_in.html')
               # return HttpResponseRedirect('recognition/Sign_in.html')

    # No post data availabe, let's just show the page.
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})

    #return render(request, 'recognition/signup.html')


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
        if len(request.FILES) == 0:
            return render(request, 'recognition/evaluate.html',
                          {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records,
                           'messages': 2})

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
                           'messages': 1 })

    return render(request, 'recognition/evaluate.html',
                  {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records, 'messages': 0 })


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

def results(request):
    return render(request, 'recognition/results.html')

def homepage(request):
    return render(request, 'recognition/homepage.html')


def add_student(request):
    return render(request, 'recognition/add_student.html')


def questionseries(request):
    return render(request, 'recognition/questionseries.html')


def userprofile(request):
    return render(request, 'recognition/userprofile.html')


