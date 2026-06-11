from django.urls import path

from accounts.views import teacher_dashboard, teacher_students
from attendance.views import (
    teacher_attendance,
    teacher_attendance_commit,
    teacher_attendance_preview,
    teacher_attendance_template,
    teacher_attendance_upload,
)
from assignments.views import (
    teacher_assignment_download,
    teacher_assignment_review,
    teacher_assignments,
    teacher_material_delete,
    teacher_material_upload,
    teacher_materials,
)

urlpatterns = [
    path('', teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/', teacher_dashboard),
    path('students/', teacher_students, name='teacher_students'),
    path('attendance/', teacher_attendance, name='teacher_attendance'),
    path('attendance/upload/', teacher_attendance_upload, name='teacher_attendance_upload'),
    path('attendance/preview/', teacher_attendance_preview, name='teacher_attendance_preview'),
    path('attendance/commit/', teacher_attendance_commit, name='teacher_attendance_commit'),
    path('attendance/template/', teacher_attendance_template, name='teacher_attendance_template'),
    path('materials/', teacher_materials, name='teacher_materials'),
    path('materials/upload/', teacher_material_upload, name='teacher_material_upload'),
    path('materials/<int:material_id>/delete/', teacher_material_delete, name='teacher_material_delete'),
    path('assignments/', teacher_assignments, name='teacher_assignments'),
    path('assignments/<int:submission_id>/review/', teacher_assignment_review, name='teacher_assignment_review'),
    path('assignments/<int:submission_id>/download/', teacher_assignment_download, name='teacher_assignment_download'),
]
