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
    pass

class Class(BaseModel):
    name = models.CharField(maxlength=50)
    students = models.ManyToManyField('User', related_name='students')

class Course(BaseModel):
    subject = models.CharField(max_length=255)
    description = RichTextField()
    tutor = models.ForeignKey(User, on_delete=models.RESTRICT)

class Mark(BaseModel):
    grade1 = models.FLoatField()
    grade2 = models.FloatField()
    grade3 = models.FloatField()
    midterm_grade = models.FloatField()
    final_grade = models.FloatField()
    clock = models.BooleanField(default=False)
    course = models.OneToOneField(Course, on_delete=models.RETRICT)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

class Forum(BaseModel):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(BaseModel):
    comment = RichTextField()
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

