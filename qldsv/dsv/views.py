from django.shortcuts import render
from rest_framework import generics, permissions, serializers, views, viewsets
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from .models import User, Class
from django.contrib.auth.models import Group
from .serializers import UserSerializer, GroupSerializer, RegisterSerializer


# Create your views here.
class UserList(generics.ListCreateAPIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetails(generics.RetrieveAPIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


#Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class GroupList(generics.ListCreateAPIView):
    permission_class = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ShowStudentsAPIView(views.APIView):
    permission_class = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    def get(self, request, user_id):
        classroom = Class.objects.filter(teacher_id=user_id)
        students = User.objects.filter()


