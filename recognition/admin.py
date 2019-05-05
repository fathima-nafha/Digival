from django.contrib import admin
from .models import Student, Teacher, QuestionBank, QuestionPaper, AddStudent,StudentMark, AddQuestionBank
# Register your models here.
admin.site.register(Teacher)

admin.site.register(Student)

admin.site.register(QuestionBank)

admin.site.register(QuestionPaper)

admin.site.register(AddStudent)

admin.site.register(AddQuestionBank)

admin.site.register(StudentMark)