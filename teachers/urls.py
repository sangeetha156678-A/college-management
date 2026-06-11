from django.urls import path
from .views import teacher_dashboard, teacher_students

urlpatterns = [
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('students/', teacher_students, name='teacher_students'),
]