from django.urls import path

from accounts import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('users/', admin_views.admin_users, name='admin_users'),
    path('users/create/', admin_views.admin_user_create, name='admin_user_create'),
    path('users/<int:user_id>/toggle/', admin_views.admin_user_toggle, name='admin_user_toggle'),
    path('users/bulk/', admin_views.admin_users_bulk, name='admin_users_bulk'),
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
