from django import forms
from recognition.models import  QuestionPaper


class UploadQuestionBank(forms.Form):
    qb_class = forms.IntegerField(label="class1")
    qb_series = forms.CharField(label="qseries", max_length=2)
    qb_qno = forms.IntegerField(label="number")
    question_paper = forms.ImageField(label="question-paper")







