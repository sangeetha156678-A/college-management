from django.contrib.auth import get_user_model
from django.test import TestCase

from academics.models import Department, Semester, Year
from accounts.models import Student
from accounts.services.user_service import create_user_account

User = get_user_model()


class UserServiceTests(TestCase):
    def setUp(self):
        self.department, _ = Department.objects.get_or_create(
            code='TEST_SVC_BCA',
            defaults={'name': 'Service Test BCA'},
        )
        self.year, _ = Year.objects.get_or_create(department=self.department, number=1)
        self.semester, _ = Semester.objects.get_or_create(year=self.year, number=2)

    def test_create_student_account_with_academic_fks(self):
        user, _password = create_user_account(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@test.edu',
            role='student',
            year=self.year,
            semester=self.semester,
        )
        student = Student.objects.get(user=user)
        self.assertEqual(student.year, self.year)
        self.assertEqual(student.semester, self.semester)
        self.assertEqual(student.department, self.department)
