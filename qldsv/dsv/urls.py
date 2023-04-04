from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(prefix='users', viewset=UserViewSet, basename='users')
router.register(prefix='courses', viewset=CourseViewSet, basename='courses')
router.register(prefix='forum', viewset=ForumViewSet, basename='forum')
router.register(prefix='comment', viewset=CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserList.as_view()),
    path('users/<pk>/', UserDetails.as_view()),
    path('register/', RegisterUserAPIView.as_view()),
    path('mark/', MarkAPIView.as_view()),
    path('groups/', GroupList.as_view()),
    path('upload/', UploadFileView.as_view()),
    path('course/', CourseListView.as_view()),
    path('chat/', ChatCreateView.as_view())
    # path('mark-detail/', MarkView.as_view())
    # re_path('^class/(?P<classname>.+)/$', StudentsViewSet.as_view()),
]


