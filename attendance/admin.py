from django.contrib import admin

from attendance.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'recorded_by', 'created_at')
    list_filter = ('status', 'subject', 'date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__roll_number')
    readonly_fields = ('created_at',)
