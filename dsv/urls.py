from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(prefix='users', viewset=UserViewSet, basename='users')
router.register(prefix='courses', viewset=CourseViewSet, basename='courses')
router.register(prefix='forum', viewset=ForumViewSet, basename='forum')
router.register(prefix='comment', viewset=CommentViewSet, basename='comment')
router.register(prefix='chat', viewset=ChatViewSet, basename='chat')
router.register(prefix='courses', viewset=MarkViewSet, basename='courses')
router.register(prefix='classes', viewset=MyClassViewSet, basename='classes')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserList.as_view()),
    path('users/<pk>/', UserDetails.as_view()),
    path('user/current-user/', CurrentUserDetails.as_view()),
    path('check-teacher/', CheckGroupTeacher.as_view()),
    path('check-student/', CheckGroupStudent.as_view()),
    path('register/', RegisterUserAPIView.as_view()),
    path('mark/', SaveMarkAPIView.as_view()),
    path('groups/', GroupList.as_view()),
    path('upload/', UploadFileView.as_view()),
    path('course/', CourseListView.as_view()),
    path('chat/', ChatListView.as_view()),
    path('export/', ExportFileView.as_view())
    # path('mark-detail/', MarkView.as_view())
    # re_path('^class/(?P<classname>.+)/$', StudentsViewSet.as_view()),
]


