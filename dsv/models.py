from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField

# Create your models here.
class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    student_number = models.CharField(max_length=10, blank=True )

    def __str__(self):
        return self.username

class Myclass(BaseModel):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User, through='MyClassUser')
    
    def __str__(self):
        return self.name

class Course(BaseModel):
    subject = models.CharField(max_length=255)
    description = RichTextField()
    tutor = models.ForeignKey(User, on_delete=models.RESTRICT)

    def __str__(self):
        return self.subject

class MyClassUser(models.Model):
    myclass = models.ForeignKey(Myclass, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.myclass.name + " - " + self.user.username

class MarkType(BaseModel):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type

class Mark(BaseModel):
    grade = models.FloatField(default=0)
    gpa = models.FloatField(default=0)
    rank = models.CharField(max_length=1)
    is_clock = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark_type = models.ForeignKey(MarkType, on_delete=models.RESTRICT)

    class Meta:
        unique_together=('student', 'mark_type')

    def __str__(self):
        return self.course.subject + "#" + self.mark_type.type + "#" + self.student.username

class Forum(BaseModel):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Comment(BaseModel):
    comment = RichTextField()
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment

class Chat(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    firebase_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('timestamp',)
