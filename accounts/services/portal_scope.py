from django.contrib.auth import get_user_model

from academics.models import Subject
from accounts.models import Student, TeacherSubjectAssignment

User = get_user_model()


def get_subjects_for_teacher(teacher):
    subject_ids = TeacherSubjectAssignment.objects.filter(
        teacher=teacher,
    ).values_list('subject_id', flat=True)
    return Subject.objects.filter(
        pk__in=subject_ids,
    ).select_related('department', 'semester', 'semester__year')


def get_subjects_for_student(student):
    return Subject.objects.filter(
        semester_id=student.semester_id,
        department_id=student.year.department_id,
    ).select_related('department', 'semester', 'semester__year').order_by('name')


def teacher_has_subject(teacher, subject_id):
    return TeacherSubjectAssignment.objects.filter(
        teacher=teacher,
        subject_id=subject_id,
    ).exists()


def student_has_subject(student, subject_id):
    return Subject.objects.filter(
        pk=subject_id,
        semester_id=student.semester_id,
        department_id=student.year.department_id,
    ).exists()


def get_students_for_teacher(teacher, subject=None):
    from accounts.services.student_service import get_students_for_teacher as _base

    queryset = _base(teacher)
    if subject is not None:
        queryset = queryset.filter(semester_id=subject.semester_id)
        if teacher.department_id:
            queryset = queryset.filter(year__department_id=teacher.department_id)
    return queryset


def resolve_student_by_identifier(identifier, *, semester_id=None, department_id=None):
    if not identifier:
        return None

    value = str(identifier).strip()
    if not value:
        return None

    queryset = Student.objects.filter(user__role='student').select_related('user', 'year', 'semester')
    if semester_id:
        queryset = queryset.filter(semester_id=semester_id)
    if department_id:
        queryset = queryset.filter(year__department_id=department_id)

    student = queryset.filter(roll_number__iexact=value).first()
    if student:
        return student

    student = queryset.filter(user__email__iexact=value).first()
    if student:
        return student

    return queryset.filter(user__username__iexact=value).first()
