from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Class, Course, Mark, Forum, Comment

admin.site.register(User, UserAdmin)
admin.site.register(Class)
admin.site.register(Course)
admin.site.register(Mark)
admin.site.register(Forum)
admin.site.register(Comment)

