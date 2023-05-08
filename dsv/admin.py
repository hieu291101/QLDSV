from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.translation import gettext_lazy as _

class UserCustomAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "student_number", "image")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
admin.site.register(User, UserCustomAdmin)
admin.site.register(Myclass)
admin.site.register(Course)
admin.site.register(Mark)
admin.site.register(Forum)
admin.site.register(Comment)
admin.site.register(MarkType)
admin.site.register(MyClassUser)