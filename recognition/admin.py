from django.contrib import admin
from .models import Student, Teacher, QuestionBank, QuestionPaper,StudentMarks, AddQuestionBank
# Register your models here.
admin.site.register(Teacher)

admin.site.register(Student)

admin.site.register(QuestionBank)

admin.site.register(QuestionPaper)

admin.site.register(AddQuestionBank)

admin.site.register(StudentMarks)