# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Course, CourseContent, Enrollment
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'email_otp', 'otp_created_at',)}),
    )
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(CourseContent)
admin.site.register(Enrollment)