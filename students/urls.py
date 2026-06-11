from django.urls import path

from accounts.views import student_dashboard
from attendance.views import student_attendance
from assignments.views import (
    student_assignment_download,
    student_assignment_upload,
    student_assignments,
    student_material_download,
    student_materials,
)

urlpatterns = [
    path('', student_dashboard, name='student_dashboard'),
    path('dashboard/', student_dashboard),
    path('attendance/', student_attendance, name='student_attendance'),
    path('materials/', student_materials, name='student_materials'),
    path('materials/<int:material_id>/download/', student_material_download, name='student_material_download'),
    path('assignments/', student_assignments, name='student_assignments'),
    path('assignments/upload/', student_assignment_upload, name='student_assignment_upload'),
    path('assignments/<int:submission_id>/download/', student_assignment_download, name='student_assignment_download'),
]
