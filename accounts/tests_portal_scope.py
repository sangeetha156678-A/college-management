from django.contrib.auth import get_user_model
from django.test import TestCase

from academics.models import Department, Semester, Subject, Year
from accounts.models import Student, Teacher, TeacherSubjectAssignment
from accounts.services.portal_scope import student_has_subject, teacher_has_subject

User = get_user_model()


class PortalScopeTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(code='TBCA', name='Test BCA', duration_years=3)
        self.year = Year.objects.create(department=self.department, number=1)
        self.semester = Semester.objects.create(year=self.year, number=1)
        self.subject = Subject.objects.create(
            department=self.department,
            semester=self.semester,
            code='BCA101',
            name='Programming',
        )

        teacher_user = User.objects.create_user(
            username='teacher1', email='teacher@test.com', password='pass', role='teacher',
            first_name='T', last_name='One',
        )
        self.teacher = Teacher.objects.create(user=teacher_user, department=self.department)
        TeacherSubjectAssignment.objects.create(teacher=self.teacher, subject=self.subject)

        other_teacher_user = User.objects.create_user(
            username='teacher2', email='teacher2@test.com', password='pass', role='teacher',
            first_name='T', last_name='Two',
        )
        self.other_teacher = Teacher.objects.create(user=other_teacher_user, department=self.department)

        student_user = User.objects.create_user(
            username='student1', email='student@test.com', password='pass', role='student',
            first_name='S', last_name='One',
        )
        self.student = Student.objects.create(
            user=student_user,
            year=self.year,
            semester=self.semester,
        )

    def test_teacher_has_subject(self):
        self.assertTrue(teacher_has_subject(self.teacher, self.subject.pk))
        self.assertFalse(teacher_has_subject(self.other_teacher, self.subject.pk))

    def test_student_has_subject(self):
        self.assertTrue(student_has_subject(self.student, self.subject.pk))
