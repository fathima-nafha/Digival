from django.shortcuts import render, render_to_response
from django.template import RequestContext
from .forms import UploadQuestionBank, RegisterForm, QuestionBankForm
from .models import QuestionBank,AddStudent, Student,Teacher,QuestionPaper, AddQuestionBank
from .recognize import recognize, evaluate_paper
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
#from settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
#from utils.forms.reset_password_form import PasswordResetRequestForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q


# Create your views here.

class ResetPasswordRequestView(FormView):
    template_name = "recognition/test_template.html"    #code for template is given below the view's code
    success_url = '/recognition/login'
    form_class = PasswordResetForm

    @staticmethod
    def validate_email_address(email):
    #This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.

        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
    #A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm).

        form = self.form_class(request.POST)
        if form.is_valid():
            data= form.cleaned_data["email_or_username"]
        if self.validate_email_address(data) is True:                 #uses the method written above
            '''
            If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
            '''
            associated_users= User.objects.filter(Q(email=data)|Q(username=data))
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
                        subject_template_name='registration/password_reset_subject.txt'
                        # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                        email_template_name='registration/password_reset_email.html'
                        # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                        subject = loader.render_to_string(subject_template_name, c)
                        # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL , [user.email], fail_silently=False)
                result = self.form_valid(form)
                messages.success(request, 'An email has been sent to ' + data +". Please check its inbox to continue reseting password.")
                return result
            result = self.form_invalid(form)
            messages.error(request, 'No user is associated with this email address')
            return result
        else:
            '''
            If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
            '''
            associated_users= User.objects.filter(username=data)
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        'email': user.email,
                        'domain': '', #or your domain
                        'site_name': '',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                        }
                    subject_template_name='registration/password_reset_subject.txt'
                    email_template_name='registration/password_reset_email.html'
                    subject = loader.render_to_string(subject_template_name, c)
                    # Email subject *must not* contain newlines
                    subject = ''.join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL , [user.email], fail_silently=False)
                result = self.form_valid(form)
                messages.success(request, 'Email has been sent to ' + data +"'s email address. Please check its inbox to continue reseting password.")
                return result
            result = self.form_invalid(form)
            messages.error(request, 'This username does not exist in the system.')
            return result
        messages.error(request, 'Invalid Input')
        return self.form_invalid(form)


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
            answers = QuestionBank.objects.filter(qb_class = qb_class, qb__qp_series = qp_series).distinct()
            for every in answers:
                db_answer[every.qb_qno] = every.qb_answers
            test_score = evaluate_paper(results, db_answer)
            student.s_marks = test_score
            student.save()
            args = {'1': qp_series, '2': qb_class, '3': qb_roll, 'url': url, 'results': results, 'score' : test_score, 'a':db_answer}
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


