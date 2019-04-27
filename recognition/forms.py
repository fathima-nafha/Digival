from django import forms
from bootstrap_modal_forms.forms import BSModalForm
from .models import QuestionBank

class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    phone_number = forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=False)


class UploadQuestionBank(forms.Form):
    qb_class = forms.IntegerField(label="class1")
    qb_series = forms.CharField(label="qseries", max_length=2)
    qb_qno = forms.IntegerField(label="number")
    question_paper = forms.ImageField(label="question-paper")


class QuestionBankForm(BSModalForm):
    class Meta:
        model = QuestionBank
        exclude = ['qb']




