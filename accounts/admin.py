from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    ActivityLog,
    AdminMessage,
    AdminMessageRecipient,
    ClassEnrollment,
    ClassTeacher,
    CollegeClass,
    CustomUser,
    Student,
    Teacher,
    TeacherSubjectAssignment,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


class TeacherSubjectAssignmentInline(admin.TabularInline):
    model = TeacherSubjectAssignment
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'semester')
    list_filter = ('year__department', 'year')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'department')
    list_filter = ('department',)
    inlines = [TeacherSubjectAssignmentInline]


admin.site.register(TeacherSubjectAssignment)
admin.site.register(CollegeClass)
admin.site.register(ClassTeacher)
admin.site.register(ClassEnrollment)
admin.site.register(AdminMessage)
admin.site.register(AdminMessageRecipient)
admin.site.register(ActivityLog)
