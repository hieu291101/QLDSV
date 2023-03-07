from django.contrib import admin
from django.urls import path

from .views import UserList, UserDetails, GroupList, RegisterUserAPIView

urlpatterns = [
    path('users/', UserList.as_view()),
    path('users/<pk>/', UserDetails.as_view()),
    path('register/', RegisterUserAPIView.as_view()),
    path('groups/', GroupList.as_view()),
]


