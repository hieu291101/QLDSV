from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User, UserAdmin)
admin.site.register(Myclass)
admin.site.register(Course)
admin.site.register(Mark)
admin.site.register(Forum)
admin.site.register(Comment)
admin.site.register(MarkType)