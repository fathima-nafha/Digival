import csv
import pandas
import re
import time

#gmail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from django.views.generic import *
from django.contrib.auth.models import User

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import UploadQuestionBank, RegisterForm , SetPasswordForm, PasswordResetRequestForm
from .models import AddQuestionBank
from .models import QuestionBank, StudentMarks, Student, Teacher, QuestionPaper
from .recognize import recognize, evaluate_paper


# Create your views here.
def validate_email_address(email):
    #This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.

        try:
            validate_email(email)
            return True
        except ValidationError:
            return False


def ResetPasswordRequestView(request, *args, **kwargs):
    template = 'recognition/forgot_password.html'
    success_url = 'recognition/Sign_in.html'

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
        if validate_email_address(data) is True:
            associated_users = User.objects.filter(Q(email=data) | Q(username=data))
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        'email': user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Digival',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_template_name = 'recognition/password_reset_email.html'
                    email = loader.render_to_string(email_template_name, c)
                    send_mail('Reset Password', email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                messages.success(request,'An email has been sent to ' + data + ". Please check its inbox to continue reseting password.")
                return render(request, 'recognition/forgot_password.html', {'form': form})
            messages.error(request, 'No user is associated with this email address')
            return render(request, 'recognition/forgot_password.html', {'form': form})
        else:
            associated_users = User.objects.filter(username=data)
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        'email': user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Digival',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_template_name = 'recognition/password_reset_email.html'
                    email = loader.render_to_string(email_template_name, c)
                    send_mail('Reset Password', email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                messages.success(request,'Email has been sent to ' + data + "'s email address. Please check its inbox to continue reseting password.")
                return render(request, 'recognition/forgot_password.html', {'form': form})
            else:
                messages.error(request, 'This username does not exist in the system.')
                return render(request, 'recognition/forgot_password.html', {'form': form})
        messages.error(request, 'Invalid Input')
        return render(request, 'recognition/forgot_password.html', {'form': form})
    else:
        form = PasswordResetRequestForm()
    return render(request, template, {'form': form})


def PasswordResetConfirmView(request, uid = None, token = None, *args, **kwargs):
    if request.method == 'POST':
        UserModel = get_user_model()
        form = SetPasswordForm(request.POST)
        assert uid is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uid)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return render(request, 'recognition/reset_password_confirm.html')
            else:
                messages.error(request, 'Password reset has not been successful.')
                return render(request, 'recognition/reset_password_confirm.html')
        else:
            messages.error(request, 'The reset password link is no longer valid.')
            return render(request, 'recognition/reset_password_confirm.html')
    else:
        form = SetPasswordForm()
    return render(request, 'recognition/reset_password_confirm.html', {'form': form})


def login(request):
    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Save session as cookie to login the user
            auth_login(request, user)
            user_email = User.objects.get(username=username)
            teacher_id = Teacher.objects.get(t_email=user_email.email)
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

                #Login the user
                auth_login(request, user)
                teacher = Teacher.objects.create(t_name=f_name +" "+ l_name, t_email=email)
                # redirect to accounts page:
                return render(request, 'recognition/Sign_in.html')
            # return HttpResponseRedirect('recognition/Sign_in.html')

    # No post data availabe, let's just show the page.
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})

    # return render(request, 'recognition/signup.html')


def evaluate(request):
    show = 1
    messages = 0
    if not request.session.has_key('t_id'):
        return login(request)

    t_id = request.session['t_id']
    teacher = Teacher.objects.get(t_id=t_id)
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()

    rollno = Student.objects.values('s_rollno').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']
        qb_roll = request.POST['s_rollno']

        if len(request.FILES) == 0:
            messages = 2
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': rollno,
                           'messages': messages, 'show': show})
        elif not QuestionPaper.objects.filter(qp_subject = subject, qp_class = qb_class, qp_test_series = testseries).exists():
            messages = 4
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': rollno,
                           'messages': messages,'show': show})
        elif not Student.objects.filter(s_rollno=qb_roll, s_class=qb_class).exists():
            messages = 5
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': rollno,
                           'messages': messages, 'show': show})

        student = Student.objects.get(s_rollno=qb_roll, s_class=qb_class)
        answer_paper = request.FILES['answer']
        qp = QuestionPaper.objects.get(qp_subject=subject, qp_test_series=testseries, qp_class=qb_class)
        answer_model = StudentMarks.objects.create(question_paper=qp,
                                                teacher=teacher,
                                                student=student,
                                                answer_paper=answer_paper)

        url = 'media/' + str(qb_class)+"/"+str(qb_roll) + '/' + answer_paper.name
        results = recognize(url)


        if results != -1:
            db_answer = dict()
            answers = QuestionBank.objects.filter(qb__qp_class=qb_class, qb__qp_subject=subject,
                                                  qb__qp_test_series=testseries).distinct()
            for every in answers:
                db_answer[every.qb_qno] = every.qb_answers
            test_score = evaluate_paper(results, db_answer)
            answer_model = StudentMarks.objects.filter(question_paper=qp, teacher = teacher, student=student, answer_paper = answer_paper).update(marks=test_score)
            messages = 3

        else:

            messages = 1
            answer_model.answer_paper.delete()
            answer_model.delete()
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': rollno,
                           'messages': messages, 'show': show})

    return render(request, 'recognition/evaluate.html',
                  {'questionBank_subject': questionBank_subject, 'questionBank_testseries': questionBank_testseries,
                   'class': classes, 'r_no': rollno, 'messages': messages, 'show': show})


def question(request):
    if not request.session.has_key('t_id'):
        return login(request)

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
    if not request.session.has_key('t_id'):
        return login(request)
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

        return render(request,'recognition/homepage.html')
    else:
        return render(request, 'recognition/answerkeys.html')
    return render(request, 'recognition/answerkeys.html')


def results(request):

    if not request.session.has_key('t_id'):
        return login(request)
    isEmpty = 1
    t_id = request.session['t_id']
    teacher = Teacher.objects.get(t_id = t_id)
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']


        if not StudentMarks.objects.filter(question_paper__qp_subject=subject,
                                                   question_paper__qp_test_series=testseries,
                                                   question_paper__qp_class=qb_class, teacher = teacher).exists():
            args = {'questionBank_subject': questionBank_subject,
                    'questionBank_testseries': questionBank_testseries,
                    'class': classes, 'isEmpty': isEmpty}
            return render(request, 'recognition/results.html', args)
        isEmpty = 0
        studentmarks = StudentMarks.objects.filter(question_paper__qp_subject=subject,
                                                   question_paper__qp_test_series=testseries,
                                                   question_paper__qp_class=qb_class, teacher=teacher)

        args = {'questionBank_subject': questionBank_subject,
                'questionBank_testseries': questionBank_testseries,
                'class': classes, 'student': studentmarks, 'isEmpty': isEmpty}
        return render(request, 'recognition/results.html', args)

    args = {'questionBank_subject': questionBank_subject,
            'questionBank_testseries': questionBank_testseries,
            'class': classes, 'isEmpty': isEmpty}
    return render(request, 'recognition/results.html', args)


def homepage(request):

    if not request.session.has_key('t_id'):
        return login(request)


    t_id = request.session['t_id']
    return render(request, 'recognition/homepage.html', {"t_id": t_id})


def questionseries(request):
    message = 0
    if not request.session.has_key('t_id'):
        return login(request)

    isEmpty = 1
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()

    if request.method == 'POST' and 'qbAnswer' not in request.POST:
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']
        request.session['subject'] = subject
        request.session['testseries'] = testseries
        request.session['qb_class'] = qb_class
        if not QuestionPaper.objects.filter(qp_class = qb_class, qp_subject = subject, qp_test_series = testseries).exists():
            isEmpty = 1
        else:
            questionBank = QuestionBank.objects.filter(qb__qp_class=qb_class, qb__qp_subject=subject,
                                                   qb__qp_test_series=testseries)
            questionPaper = QuestionPaper.objects.filter(qp_class = qb_class, qp_subject = subject, qp_test_series = testseries).values('question_paper')

            isEmpty=0
            args = {'class': classes,
                'questionBank_subject': questionBank_subject,
                'questionBank_testseries': questionBank_testseries,
                'isEmpty': isEmpty,
                'questionBank': questionBank,
                'questionPaper': questionPaper,'message': message}

            return render(request, 'recognition/questionseries.html', args)
    if request.method == 'POST' and 'qbAnswer' in request.POST:

        qbAnswer = request.POST['qbAnswer']
        q_id = request.POST['q_id']
        message = 1
        QuestionBank.objects.filter(q_id=q_id).update(qb_answers=qbAnswer)
        if request.session.has_key('subject') and request.session.has_key('qb_class') and request.session.has_key('testseries') :
            subject = request.session['subject']
            qb_class = request.session['qb_class']
            testseries = request.session ['testseries']

            questionBank = QuestionBank.objects.filter(qb__qp_class=qb_class, qb__qp_subject=subject,
                                                       qb__qp_test_series=testseries)
            args = {'class': classes,
                    'questionBank_subject': questionBank_subject,
                    'questionBank_testseries': questionBank_testseries,
                    'questionBank': questionBank,
                    'message': message}

            return render(request, 'recognition/questionseries.html', args)

    args = {'class': classes, 'questionBank_subject': questionBank_subject,
            'questionBank_testseries': questionBank_testseries, 'isEmpty': isEmpty,'message': message}
    return render(request, 'recognition/questionseries.html', args)


def userprofile(request):
    if not request.session.has_key('t_id'):
        return login(request)

    t_id = request.session['t_id']
    t = Teacher.objects.get(t_id = t_id)
    args = {'teacher' : t}
    if request.method == 'POST':
        t_name = request.POST['t_name']
        t_school_name = request.POST['t_school_name']
        Teacher.objects.filter(t_id = t_id).update(t_name = t_name, t_school_name = t_school_name)
        return render(request, 'recognition/userprofile.html', args)

    return render(request, 'recognition/userprofile.html', args)


def view_student(request):
    if not request.session.has_key('t_id'):
        return login(request)

    classes = Student.objects.order_by('s_class').values('s_class').distinct()
    error = 5

    if request.method == 'POST':
        if 'class' in request.POST:
            class1 = request.POST['class']
            request.session['class'] = class1
            students = Student.objects.filter(s_class = class1).order_by('s_rollno')

            args = {'class': classes, 'students': students, 'message': error}
            return render(request, 'recognition/editstudent.html', args)

        if request.FILES:
            if len(request.FILES) == 0:
                error = 4
                args = {'class': classes, 'message': error}
                return render(request, 'recognition/editstudent.html', args)

            student_list = request.FILES['fileUpload']
            filename = student_list.name

            if not filename.endswith('.csv'):
                filename1 = re.split('\.', filename)[0]
                data_xls = pandas.read_excel(student_list, 'Sheet1', index_col=None)
                data_xls.to_csv(filename1+'.csv', encoding='utf-8')
                filename = filename1+'.csv'
            with open(filename, 'r') as csvFile:
                try:
                    read = csv.reader(csvFile)
                    next(read)
                    for line in read:
                        rollno = int(line[1])
                        name = str(line[2])
                        class1 = int(line[3])
                        school = str(line[4])
                        if Student.objects.filter(s_rollno=rollno, s_class=class1, s_school_name=school).exists():
                            error = 3
                            pass
                        else:
                            Student.objects.create(s_rollno=rollno, s_name=name, s_class=class1,
                                                   s_school_name=school)
                            error = 2


                finally:
                    csvFile.close()
            args = {'class': classes, 'message': error}
            return render(request, 'recognition/editstudent.html', args)

        if 'rollno' in request.POST and 'name' in request.POST:
            s_rollno = request.POST['rollno']
            s_name = request.POST['name']
            s_class = request.POST['s_class']
            s_school = request.POST['school']
            if Student.objects.filter(s_rollno=s_rollno, s_class=s_class, s_school_name=s_school).exists():
                error = 1
                args = {'class': classes,'message': error}
                return render(request, 'recognition/editstudent.html', args)
            else:
                Student.objects.create(s_rollno=s_rollno, s_name=s_name, s_class=s_class, s_school_name=s_school)
                class1 = request.session['class']
                students = Student.objects.filter(s_class=class1).order_by('s_rollno')
                error = 2
                args = {'class': classes,'students':students,'message': error}
                return render(request, 'recognition/editstudent.html', args)

    args = {'class': classes,'message': error}
    return  render(request, 'recognition/editstudent.html',args)


def logout(request):
    try:
        del request.session['t_id']
    except KeyError:
        pass
    return redirect('recognition:login')
