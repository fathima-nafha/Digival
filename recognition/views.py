from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from .forms import RegisterForm,  UploadQuestionBank
from .models import QuestionBank,AddStudent, Student,Teacher,QuestionPaper, AddQuestionBank
from .recognize import recognize, evaluate_paper
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from .import forms

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
            user_email = User.objects.get(username = username)
            #print(user_email)
            teacher_id = Teacher.objects.get(t_email = user_email.email)
            request.session['t_id'] = teacher_id.t_id
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
    messages = 0
    if request.session.has_key('t_id'):
        t_id = request.session['t_id']
        teacher = Teacher.objects.get(t_id = t_id)
    all_records = Student.objects.all()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        qp_series = request.POST['qseries']
        qb_class = request.POST['class']
        qb_roll = request.POST['s_rollno']
        student = Student.objects.get(s_rollno = qb_roll)
        if len(request.FILES) == 0:
            messages = 2
            return render(request, 'recognition/evaluate.html',
                          {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records,
                           'messages': messages})

        answer_paper = request.FILES['answer']
        answer_model = AddStudent.objects.create(teacher=teacher, student=student, answer_paper = answer_paper)
        url = 'media/' + str(qb_roll) + '/' + answer_paper.name
        print(url)
        results = recognize(url)
        if results != -1:
            db_answer = dict()
            answers = QuestionBank.objects.filter( qb__qp_series = qp_series).distinct()
            for every in answers:
                db_answer[every.qb_qno] = every.qb_answers
            test_score = evaluate_paper(results, db_answer)
            student.s_marks = test_score
            student.save()
            args = {'1': qp_series,  '2': qb_roll, 'url': url, 'results': results, 'score' : test_score, 'a':db_answer}
            print(args)
            messages = 3

        else:
            answer_model.answer_paper.delete()
            answer_model.delete()
            messages = 1
            return render(request, 'recognition/evaluate.html',
                          {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records,
                           'messages': messages })

    return render(request, 'recognition/evaluate.html',
                  {'qp_series': qp_series_fromdb, 'class': classes, 'r_no': all_records, 'messages': messages })
    return render(request, 'recognition/evaluate.html')


def question(request):
    if request.method == 'POST':
       form=UploadQuestionBank(request.POST,request.FILES)
       if form.is_valid():
           qp_subject = request.POST['qp_subject']
           qp_test_series = request.POST['qp_test_series']
           qp_class = request.POST['qp_class']
           question_paper = request.FILES['question_paper']
           if QuestionPaper.objects.filter(qp_subject=qp_subject, qp_class=qp_class, qp_test_series=qp_test_series).exists():
               return render(request, 'recognition/question.html' , {
                   'form': form,
                   'error_message': 'Question Paper Already Exists!!'
                })
           else:
                paper = QuestionPaper(qp_subject = qp_subject, qp_test_series= qp_test_series, qp_class=qp_class, question_paper= question_paper)
                paper.save()

                qp_id=QuestionPaper.objects.filter(qp_subject = qp_subject, qp_test_series= qp_test_series, qp_class=qp_class).values('qp_id')
                qp= qp_id[0]['qp_id']
                request.session['q_id'] = qp

                if request.session.has_key('t_id'):
                    t_id = request.session['t_id']

                addques = AddQuestionBank()
                addques.teacher_id=t_id
                addques.qp_id=qp
                addques.save()
                #request.session.save()
                return render(request, 'recognition/answerkeys.html')
    else:
        form=UploadQuestionBank()
    return render(request,'recognition/question.html',{ 'form':form })

def answerkeys(request):
    if request.method == 'POST':
        ques = request.POST.getlist('ques[]')
        ans = request.POST.getlist('ans[]')
        num = request.POST['num']
        if request.session.has_key('q_id'):
            q_id = request.session['q_id']

        for i in range(len(ques)):
            qb_qno = ques[i]
            qb_answers = ans[i]
            q_bank = QuestionBank(qb_qno=qb_qno, qb_answers=qb_answers)
            q_bank.qb_id = q_id
            q_bank.save()
        #print(num)
        return render(request,'recognition/homepage.html')
    else:
        return render(request, 'recognition/answerkeys.html')
    #return render(request, 'recognition/answerkeys.html')

def results(request):
    students = Student.objects.all()
    args = {'students':students}
    return render(request, 'recognition/results.html',args)

def homepage(request):
    if request.session.has_key('t_id'):
        t_id = request.session['t_id']
        return render(request, 'recognition/homepage.html', {"t_id": t_id})
    else:
        return render(request, 'recognition/results.html')



def add_student(request):
    return render(request, 'recognition/add_student.html')


def questionseries(request):
    return render(request, 'recognition/questionseries.html')


def userprofile(request):
    return render(request, 'recognition/userprofile.html')




