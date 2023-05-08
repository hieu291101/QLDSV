import os
import pathlib
import string

import pyrebase
import firebase_admin
from django.db.models import Q
from rest_framework import generics, permissions, serializers, views, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope, OAuth2Authentication
from .models import *
from django.contrib.auth.models import Group
from .serializers import *
import io, csv, pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import filters
import requests
from rest_framework.decorators import api_view
import uuid

def is_valid(data):
    if data.is_valid_format.value and data.is_mx_found and data.is_smtp_valid:
        if not data.is_catchall_email and not data.is_role_email and not data.is_free_email:
            return True
    return False


def validate_email(email):
    response = requests.get(settings.API_URL_EMAIL + "&email=" + email)
    valid = is_valid(response.content)
    return valid


def send(subject, message, recipient):
    is_a_valid_email = validate_email(recipient)
    if is_a_valid_email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient])
    else:
        print("Not a valid recipient email, cannot send")

# Create your views here.
class UserList(generics.ListCreateAPIView):
    # permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['student_number', 'first_name', 'last_name']


class UserDetails(generics.RetrieveAPIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserDetails(views.APIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        user = request.user
        if user:
            return Response(UserSerializer(user, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class CheckGroupTeacher(views.APIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        user = request.user
        admin_group = Group.objects.get(name='Teacher')
        if user and admin_group in user.groups.all():
            return Response({"status": "success"}, status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class CheckGroupStudent(views.APIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        user = request.user
        admin_group = Group.objects.get(name='Student')
        if user and admin_group in user.groups.all():
            return Response({"status": "success"}, status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

# Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class GroupList(generics.ListCreateAPIView):
    permission_class = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class UserViewSet(viewsets.ViewSet):
    # permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]

    # get student list
    @action(methods=['POST'], detail=True, url_path='students')
    def students(self, request, pk):
        classname = request.data.get('classname')
        myclass = Myclass.objects.get(name=classname)

        students = myclass.users.all()
        teacher = User.objects.filter(myclass=myclass, id=pk)

        if teacher:
            return Response(StudentsSerializer(students, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


    # get mark for student
    @action(methods=['GET'], detail=True, url_path='mark')
    def mark(self, request, pk):
        mark = Mark.objects.filter(student_id=pk)

        if mark:
            return Response(MarkSerializer(mark, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='course')
    def get_course_by_teacher(self, request, pk):
        course = Course.objects.filter(tutor_id=pk)

        if course:
            return Response(CourseSerializer(course, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SaveMarkAPIView(generics.CreateAPIView, views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SaveMarkSerializer

    def get_object(self, pk):
        return Mark.objects.get(pk=pk)

    # lock grade for students
    def patch(self, request, pk):
        mark = self.get_object(pk)
        serializer = MarkSerializer(mark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if mark.is_clock:
                send("Thông báo về việc có điểm môn " + mark.queryset.values('course'),
                     "Hãy vào trang để xem điểm",
                     mark.queryset.values('student'))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class MarkViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST'], detail=True, url_path='students-by-teacher')
    def mark_details(self, request, pk):
        course = Course.objects.filter(tutor_id=request.data.get('teacher_id'))
        mark = Mark.objects.filter(course=course)

        if mark:
            return Response(MarkSerializer(mark, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='student')
    def mark_details(self, request, pk):
        mark = Mark.objects.filter(course_id=pk)

        if mark:
            return Response(MarkSerializer(mark, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='mark-detail')
    def mark_details(self, request, pk):
        mark = Mark.objects.filter(course_id=pk).filter(student_id=request.data.get('student_id'))

        if mark:
            return Response(MarkSerializer(mark, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='mark')
    def get_mark_list(self, request, pk):
        mark = Mark.objects.filter(course_id=pk)

        if mark:
            return Response(MarkSerializer(mark, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class CourseListView(views.APIView):

    def post(self, request):
        course = Mark.objects.filter(student_id=request.data.get('student_id')).values('course__id',
                                                                                                   'course__subject').distinct()
        if course:
            return Response(course, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UploadFileView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        list_review = []
        for _, row in reader.iterrows():
            student = User.objects.filter(student_number=row['Student Number'])
            marktype = MarkType.objects.filter(type=row['Mark Type'])
            course = Course.objects.filter(subject=row['Course Name'])
            grade = row['Grade']
            if not str(grade).isnumeric():
                return Response({'message': f'Điểm : \"{grade}\" (không đúng định dạng)'},
                                status=status.HTTP_200_OK)

            if not student:
                student_number = row['Student Number']
                return Response({'message': f'Mã số sinh viên : \"{student_number}\" (không tồn tại)' }, status=status.HTTP_200_OK)

            if not marktype:
                mark_type = row['Mark Type']
                return Response({'message': f'Loại điểm : \"{mark_type}\" (không tồn tại)' }, status=status.HTTP_200_OK)

            if not course:
                course_name = row['Course Name']
                print(course)
                print("course")
                return Response({'message': f'Tên môn học : \"{course_name}\" không tồn tại' }, status=status.HTTP_200_OK)

            new_file = Mark(
                grade=float(grade),
                course=course.first(),
                # course_id=course.first().id,
                student=student.first(),
                # student_id=student.first().id,
                mark_type=marktype.first(),
                # mark_type_id=student.first().id,
                gpa=0
            )
            list_review.append(new_file)
            new_file.save()

        if list_review.__len__().__gt__(0):
            return Response(MarkSerializer(list_review, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class ExportFileView(generics.CreateAPIView):
    serializer_class = None
    def post(self, request, *args, **kwargs):
        data = request.data.get('students')
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # file = serializer.validated_data['file']
        df = pd.DataFrame(data)
        df.to_csv(pathlib.Path.home() / 'Downloads/export_dataframe.csv', index=False, header=True, encoding='utf-8')
        print(df)
        return Response({"status": "success", "csv_url": f'{pathlib.Path.home()}\\Downloads\\export_dataframe.csv'},
                        status.HTTP_201_CREATED)

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_queryset(self):
        course = self.queryset
        subject = self.request.query_params.get('subject')

        if subject:
            course = course.filter(subject__icontains=subject)

        return course

class ForumViewSet(viewsets.ModelViewSet):
    serializer_class = ForumSerializer
    queryset = Forum.objects.all()

    def get_queryset(self):
        forum = self.queryset
        title = self.request.query_params.get('title')

        if title:
            forum = forum.filter(title__icontains=title)

        return forum

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        comment = self.queryset
        forum_title = self.request.query_params.get('forum_title')

        if forum_title:
            comment = comment.filter(forum_title__icontains=forum_title)

        return comment

FIREBASE_CONFIG  = {
    "apiKey": "AIzaSyBvkhkCqtyng4czwP__szqhYcpzxDzZzkY",
    "authDomain": "qldsv-64efc.firebaseapp.com",
    "databaseURL": "https://qldsv-64efc-default-rtdb.firebaseio.com",
    "projectId": "qldsv-64efc",
    "storageBucket": "qldsv-64efc.appspot.com",
    "messagingSenderId": "762995328688",
    "appId": "1:762995328688:web:8d7a0423469c1884451d75",
}

# Initialize Firebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
database = firebase.database()

class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        sender = self.request.query_params.get('sender')
        receiver = self.request.query_params.get('receiver')
        queryset = Chat.objects.filter(
            Q(sender=sender, receiver=receiver) |
            Q(sender=receiver, receiver=sender)
        )
        return queryset

class ChatViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def create(self, request):
        data = request.data
        serializer = ChatSerializer(data=data)
        if serializer.is_valid():
            # Lưu tin nhắn vào Firebase Realtime Database
            database.child("chat").push(data)
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class MyClassViewSet(viewsets.ModelViewSet):
    queryset = Myclass.objects.all()
    serializer_class = ClassSerializer