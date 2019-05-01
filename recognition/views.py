from django.shortcuts import render,redirect
from django.urls import reverse
from .forms import UploadQuestionBank, RegisterForm, QuestionBankForm
from .models import QuestionBank, AddStudent, StudentMarks, Student, Teacher, QuestionPaper
from .recognize import recognize, evaluate_paper
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login


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

    # return render(request, 'recognition/signup.html')


def evaluate(request):
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    messages = 0
    if request.session.has_key('t_id'):
        t_id = request.session['t_id']
        teacher = Teacher.objects.get(t_id=t_id)
    all_records = Student.objects.all()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']
        qb_roll = request.POST['s_rollno']
        student = Student.objects.get(s_rollno=qb_roll)
        if len(request.FILES) == 0:
            messages = 2
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': all_records,
                           'messages': messages})

        answer_paper = request.FILES['answer']
        answer_model = AddStudent.objects.create(teacher=teacher, student=student, answer_paper=answer_paper)
        url = 'media/' + str(qb_roll) + '/' + answer_paper.name
        print(url)
        results = recognize(url)
        if results != -1:
            db_answer = dict()
            answers = QuestionBank.objects.filter(qb__qp_class=qb_class, qb__qp_subject=subject,
                                                  qb__qp_test_series=testseries).distinct()
            for every in answers:
                db_answer[every.qb_qno] = every.qb_answers
            test_score = evaluate_paper(results, db_answer)
            qp = QuestionPaper.objects.get(qp_subject=subject, qp_test_series=testseries, qp_class=qb_class)
            studentMarks = StudentMarks.objects.create(question_paper=qp, student=student, marks=test_score)
            args = {'1': testseries, '9': subject, '2': qb_class, '3': qb_roll, 'url': url, 'results': results,
                    'score': test_score, 'a': db_answer}
            print(args)
            messages = 3

        else:
            answer_model.answer_paper.delete()
            answer_model.delete()
            messages = 1
            return render(request, 'recognition/evaluate.html',
                          {'questionBank_subject': questionBank_subject,
                           'questionBank_testseries': questionBank_testseries, 'class': classes, 'r_no': all_records,
                           'messages': messages})

    return render(request, 'recognition/evaluate.html',
                  {'questionBank_subject': questionBank_subject, 'questionBank_testseries': questionBank_testseries,
                   'class': classes, 'r_no': all_records, 'messages': messages})


def question(request):
    if request.method == 'POST':
        form = UploadQuestionBank(request.POST, request.FILES)
        if form.is_valid():
            class1 = form.cleaned_data['class1']
            qseries = form.cleaned_data['qseries']
            number = form.cleaned_data['number']
            question_paper = form.cleaned_data['question_paper']
            args = {'class1': class1, 'qseries': qseries, 'number': number, 'qp': question_paper}

            return render(request, "recognition/success.html", args)

        else:
            form = UploadQuestionBank()
            return render(request, "recognition/homepage.html", {'form': form})
    else:
        form = UploadQuestionBank()
        return render(request, "recognition/question.html", {'form': form})
    # return render(request, 'recognition/question.html')


def results(request):
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()
    if request.method == 'POST':
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']
        studentmarks = StudentMarks.objects.filter(question_paper__qp_subject=subject,
                                                   question_paper__qp_test_series=testseries,
                                                   question_paper__qp_class=qb_class).count()

        if studentmarks == 0:
            args = {'questionBank_subject': questionBank_subject,
                    'questionBank_testseries': questionBank_testseries,
                    'class': classes, 'isEmpty': 1}
            return render(request, 'recognition/results.html', args)

        studentmarks = StudentMarks.objects.filter(question_paper__qp_subject=subject,
                                                   question_paper__qp_test_series=testseries,
                                                   question_paper__qp_class=qb_class)

        args = {'questionBank_subject': questionBank_subject,
                'questionBank_testseries': questionBank_testseries,
                'class': classes, 'student': studentmarks}
        return render(request, 'recognition/results.html', args)

    args = {'questionBank_subject': questionBank_subject,
            'questionBank_testseries': questionBank_testseries,
            'class': classes}
    return render(request, 'recognition/results.html', args)


def homepage(request):
    if request.session.has_key('t_id'):
        t_id = request.session['t_id']
        return render(request, 'recognition/homepage.html', {"t_id": t_id})
    else:
        return render(request, 'recognition/results.html')


def add_student(request):
    return render(request, 'recognition/add_student.html')


def questionseries(request):
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()

    if request.method == 'POST' and 'qbAnswer' not in request.POST:
        subject = request.POST['subject']
        testseries = request.POST['testseries']
        qb_class = request.POST['class']
        request.session['subject'] =subject
        request.session['testseries'] = testseries
        request.session['qb_class'] = qb_class
        questionBank = QuestionBank.objects.filter(qb__qp_class=qb_class, qb__qp_subject=subject,
                                                   qb__qp_test_series=testseries)
        args = {'class': classes,
                'questionBank_subject': questionBank_subject,
                'questionBank_testseries': questionBank_testseries,
                'questionBank': questionBank}

        return render(request, 'recognition/questionseries.html', args)
    if request.method == 'POST' and 'qbAnswer' in request.POST:

        qbAnswer = request.POST['qbAnswer']
        q_id = request.POST['q_id']
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
                    'questionBank': questionBank}

            return render(request, 'recognition/questionseries.html', args)

    args = {'class': classes, 'questionBank_subject': questionBank_subject,
            'questionBank_testseries': questionBank_testseries}
    return render(request, 'recognition/questionseries.html', args)


def save(request):
    questionBank_subject = QuestionPaper.objects.values('qp_subject').distinct()
    questionBank_testseries = QuestionPaper.objects.values('qp_test_series').distinct()
    classes = QuestionPaper.objects.order_by('qp_class').values('qp_class').distinct()

    if request.method == 'POST':
        # qbClass = request.POST['qbClass']
        qbAnswer = request.POST['qbAnswer']
        # qbSubject = request.POST['qbSubject']
        # qbTest_series = request.POST['qbTest_series']
        # qb_qno = request.POST['qb_qno']
        q_id = request.POST['q_id']
        QuestionBank.objects.filter(q_id = q_id).update(qb_answers = qbAnswer)
        # args = {'class': classes, 'questionBank_subject': questionBank_subject,
        #         'questionBank_testseries': questionBank_testseries, 'message': 1}
        # return redirect(reverse('questionseries'), args)
    #
    # args = {'class': classes, 'questionBank_subject': questionBank_subject,
    #         'questionBank_testseries': questionBank_testseries}
    # return render(request, 'recognition/questionseries.html', args)



def edit_qp(request):
    pass


def userprofile(request):
    return render(request, 'recognition/userprofile.html')


def sample(request):
    return render(request, 'recognition/sample.html')
