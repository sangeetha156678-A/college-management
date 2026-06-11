from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import Department, Semester, Subject, Year
from accounts.models import CustomUser, Student, Teacher, TeacherSubjectAssignment


class AcademicHierarchyTests(TestCase):
    def setUp(self):
        self.bca, _ = Department.objects.get_or_create(
            code='TEST_BCA',
            defaults={'name': 'Test BCA'},
        )
        self.bcom, _ = Department.objects.get_or_create(
            code='TEST_BCOM',
            defaults={'name': 'Test B.Com'},
        )
        self.year1, _ = Year.objects.get_or_create(department=self.bca, number=1)
        self.year2, _ = Year.objects.get_or_create(department=self.bca, number=2)
        self.sem1, _ = Semester.objects.get_or_create(year=self.year1, number=1)
        self.sem2, _ = Semester.objects.get_or_create(year=self.year1, number=2)
        self.other_year, _ = Year.objects.get_or_create(department=self.bcom, number=1)
        self.other_sem, _ = Semester.objects.get_or_create(year=self.other_year, number=1)
        self.subject1, _ = Subject.objects.get_or_create(
            department=self.bca,
            code='TBCA101',
            defaults={'semester': self.sem1, 'name': 'Programming'},
        )
        self.subject2, _ = Subject.objects.get_or_create(
            department=self.bca,
            code='TBCA102',
            defaults={'semester': self.sem2, 'name': 'Data Structures'},
        )

    def test_subject_rejects_mismatched_department(self):
        subject = Subject(
            department=self.bcom,
            semester=self.sem1,
            code='BAD101',
            name='Invalid Subject',
        )
        with self.assertRaises(ValidationError):
            subject.full_clean()

    def test_student_rejects_semester_from_different_year(self):
        user = CustomUser.objects.create_user(
            username='student1',
            email='student1@test.edu',
            password='pass',
            role='student',
        )
        student = Student(user=user, year=self.year1, semester=self.other_sem)
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_student_accepts_valid_year_semester_chain(self):
        user = CustomUser.objects.create_user(
            username='student2',
            email='student2@test.edu',
            password='pass',
            role='student',
        )
        student = Student(user=user, year=self.year1, semester=self.sem1)
        student.full_clean()
        student.save()
        self.assertEqual(student.department, self.bca)

    def test_teacher_rejects_second_subject_in_same_semester(self):
        user = CustomUser.objects.create_user(
            username='teacher1',
            email='teacher1@test.edu',
            password='pass',
            role='teacher',
        )
        teacher = Teacher.objects.create(user=user, department=self.bca)
        subject_a, _ = Subject.objects.get_or_create(
            department=self.bca,
            code='TBCA103',
            defaults={'semester': self.sem1, 'name': 'Maths'},
        )
        subject_b, _ = Subject.objects.get_or_create(
            department=self.bca,
            code='TBCA104',
            defaults={'semester': self.sem1, 'name': 'English'},
        )
        TeacherSubjectAssignment.objects.create(teacher=teacher, subject=subject_a)
        assignment = TeacherSubjectAssignment(teacher=teacher, subject=subject_b)
        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_teacher_accepts_subjects_from_different_semesters(self):
        user = CustomUser.objects.create_user(
            username='teacher2',
            email='teacher2@test.edu',
            password='pass',
            role='teacher',
        )
        teacher = Teacher.objects.create(user=user, department=self.bca)
        TeacherSubjectAssignment.objects.create(teacher=teacher, subject=self.subject1)
        assignment = TeacherSubjectAssignment(teacher=teacher, subject=self.subject2)
        assignment.full_clean()
        assignment.save()
