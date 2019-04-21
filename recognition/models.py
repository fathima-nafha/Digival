from django.db import models

# Create your models here.


def upload_location(instance,filename):
    return "%s/%s" %(instance.qp_series,filename)


def upload_location2(instance,filename):
    return "%s/%s" %(instance.student.s_id,filename)


class Teacher(models.Model):
    t_id = models.AutoField(primary_key=True)
    t_name = models.CharField(max_length=128, null=True)
    t_email = models.EmailField(null=True)
    t_password = models.CharField(max_length=30,null=True)
    t_school_name = models.CharField(max_length=128, null=True)
    security_question = models.CharField(max_length=128, null=True)
    security_answer = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.t_name


class Student(models.Model):
    s_id = models.AutoField(primary_key=True)
    s_rollno = models.IntegerField(null=True)
    s_name = models.CharField(max_length=128, null=True)
    s_class = models.IntegerField(null=True)
    s_school_name = models.CharField(max_length=128, null=True)
    s_marks = models.IntegerField(default=0)

    def __str__(self):
        return self.s_name


class QuestionPaper(models.Model):
    qp_series = models.CharField(primary_key=True, max_length=5)
    question_paper = models.ImageField(upload_to=upload_location,
                                       null=True,
                                       blank=True,
                                       width_field="width_field",
                                       height_field="height_field")
    qp_class = models.IntegerField(null=False)
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    def __str__(self):
        return self.qp_series


class QuestionBank(models.Model):
    q_id = models.AutoField(primary_key=True)
    qb_qno = models.CharField(max_length=5, null=False)
    qb = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    qb_class = models.IntegerField(null=False)
    qb_answers = models.CharField(max_length=30, null=False)


    class Meta:
        unique_together = (('qb_qno', 'qb', 'qb_class'),)

    def __str__(self):
        return self.qb_qno+" "+ self.qb.qp_series



class AddStudent(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer_paper = models.ImageField(upload_to=upload_location2,
                                       null=True,
                                       blank=True,
                                       width_field="width_field",
                                       height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    class Meta:
        unique_together = (('teacher', 'student'),)

    def __str__(self):
        return  str(self.teacher.t_id) +" " + self.student.s_name


class AddQuestionBank(models.Model):

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    questionpaper = models.ForeignKey(QuestionPaper,to_field='qp_series', on_delete=models.CASCADE)

    def __str__(self):
        return  self.teacher.t_name




