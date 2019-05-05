from django.db import models

# Create your models here.


def upload_location(instance,filename):
    return "%s/%s" %(instance.qp_test_series+instance.qp_subject,filename)


def upload_location2(instance,filename):
    return "%s/%s" %(instance.student.s_rollno,filename)


class Teacher(models.Model):
    t_id = models.AutoField(primary_key=True)
    t_name = models.CharField(max_length=128, null=True)
    t_email = models.EmailField(null=True)
    t_school_name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.t_name


class Student(models.Model):
    s_id = models.AutoField(primary_key=True)
    s_rollno = models.IntegerField(null=True)
    s_name = models.CharField(max_length=128, null=True)
    s_class = models.IntegerField(null=True)
    s_school_name = models.CharField(max_length=128, null=True)


    def __str__(self):
        return self.s_name


class QuestionPaper(models.Model):
    qp_id=models.AutoField(primary_key=True)
    qp_subject = models.CharField(max_length=15, null=False, default='eng')
    qp_test_series = models.CharField(max_length=15, null=False, default=1)
    question_paper = models.ImageField(upload_to=upload_location,
                                       null=True,
                                       blank=False,
                                       width_field="width_field",
                                       height_field="height_field")
    qp_class = models.IntegerField(null=False, default=1)
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    class Meta:
        unique_together = (('qp_subject', 'qp_test_series', 'qp_class'),)

    def __str__(self):
        return self.qp_subject +" "+ self.qp_test_series


class QuestionBank(models.Model):
    q_id = models.AutoField(primary_key=True)
    qb_qno = models.CharField(max_length=5, null=False)
    qb = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    qb_answers = models.CharField(max_length=30, null=False)

    class Meta:
        unique_together = (('qb_qno', 'qb'),)

    def __str__(self):
        return self.qb.qp_subject +" "+self.qb.qp_test_series+' '+self.qb_qno+" "+ self.qb_answers



class AddStudent(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer_paper = models.ImageField(upload_to=upload_location2,
                                       null=True,
                                       blank=True,
                                       width_field="width_field",
                                       height_field="height_field")
    height_field = models.IntegerField(default=0, null=True)
    width_field = models.IntegerField(default=0, null=True)

    def __str__(self):
        return  str(self.teacher.t_id) +" " + self.student.s_name + " " + str(self.student.s_rollno)


class AddQuestionBank(models.Model):

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    qp = models.ForeignKey(QuestionPaper,on_delete=models.CASCADE)

    def __str__(self):
        return  self.teacher.t_name


class StudentMark(models.Model):
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks = models.IntegerField(default=0, null=True)

    class Meta:
        unique_together = (('question_paper','student'),)


