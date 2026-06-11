from django.urls import path

from accounts import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('teachers/', admin_views.admin_teachers, name='admin_teachers'),
    path('teachers/create/', admin_views.admin_teacher_create, name='admin_teacher_create'),
    path('teachers/<int:teacher_id>/', admin_views.admin_teacher_detail, name='admin_teacher_detail'),
    path('teachers/<int:teacher_id>/edit/', admin_views.admin_teacher_edit, name='admin_teacher_edit'),
    path('teachers/<int:teacher_id>/toggle/', admin_views.admin_teacher_toggle, name='admin_teacher_toggle'),
    path('students/', admin_views.admin_students, name='admin_students'),
    path('students/create/', admin_views.admin_student_create, name='admin_student_create'),
    path('students/import/', admin_views.admin_student_import, name='admin_student_import'),
    path('students/import/template/', admin_views.admin_student_import_template, name='admin_student_import_template'),
    path('students/import/credentials/', admin_views.admin_student_import_credentials, name='admin_student_import_credentials'),
    path('students/<int:student_id>/', admin_views.admin_student_detail, name='admin_student_detail'),
    path('students/<int:student_id>/edit/', admin_views.admin_student_edit, name='admin_student_edit'),
    path('students/<int:student_id>/toggle/', admin_views.admin_student_toggle, name='admin_student_toggle'),
    path('classes/', admin_views.admin_classes, name='admin_classes'),
    path('classes/create/', admin_views.admin_class_create, name='admin_class_create'),
    path('classes/<int:class_id>/', admin_views.admin_class_detail, name='admin_class_detail'),
    path('classes/<int:class_id>/assign-teachers/', admin_views.admin_class_assign_teachers, name='admin_class_assign_teachers'),
    path('classes/<int:class_id>/remove-teacher/<int:teacher_id>/', admin_views.admin_class_remove_teacher, name='admin_class_remove_teacher'),
    path('classes/<int:class_id>/enroll-students/', admin_views.admin_class_enroll_students, name='admin_class_enroll_students'),
    path('classes/<int:class_id>/remove-student/<int:student_id>/', admin_views.admin_class_remove_student, name='admin_class_remove_student'),
    path('classes/<int:class_id>/reassign-teacher/<int:teacher_id>/', admin_views.admin_class_reassign_teacher, name='admin_class_reassign_teacher'),
    path('messages/', admin_views.admin_messages_compose, name='admin_messages_compose'),
    path('messages/history/', admin_views.admin_messages_history, name='admin_messages_history'),
]
