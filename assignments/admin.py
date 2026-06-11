from django.contrib import admin

from assignments.models import AssignmentSubmission, StudyMaterial


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_by', 'uploaded_at', 'is_active')
    list_filter = ('subject', 'is_active')
    search_fields = ('title', 'topic')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'version', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('status', 'subject')
    search_fields = ('student__user__first_name', 'student__roll_number')
