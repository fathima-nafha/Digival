from django.db import models

# Create your models here.

def upload_location(instance,filename):
    return "%s/%s" %(instance.id,filename)


class Teacher(models.Model):
    t_id = models.AutoField(primary_key=True)
    t_name = models.CharField(max_length=128)
    t_email = models.EmailField()
    t_password = models.CharField(max_length=30)
    t_school_name = models.CharField(max_length=128)
    security_question = models.CharField(max_length=128)
    security_answer = models.CharField(max_length=50)


class Student(models.Model):
    s_id = models.AutoField(primary_key=True)
    s_rollno = models.IntegerField()
    s_name = models.CharField(max_length=128)
    s_class = models.IntegerField()
    s_school_name = models.CharField(max_length=128)
    s_marks = models.IntegerField(default=0)


class QuestionBank(models.Model):
    qb_id = models.AutoField(primary_key=True)
    qb_class = models.IntegerField()
    qb_qno = models.IntegerField()
    qb_series = models.CharField(max_length=5)
    qb_answers = models.CharField(max_length=30)


class QuestionPaper(models.Model):
    qp_series = models.CharField(max_length=5)
    question_paper = models.ImageField(upload_to=upload_location,
                                       null=True,
                                       blank=True,
                                       width_field="width_field",
                                       height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)


