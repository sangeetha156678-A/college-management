from datetime import date
from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from openpyxl import Workbook

from academics.models import Department, Semester, Subject, Year
from accounts.models import Student, Teacher, TeacherSubjectAssignment
from attendance.models import AttendanceRecord
from attendance.services.attendance_service import parse_attendance_workbook

User = get_user_model()


class AttendanceServiceTests(TestCase):
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

        student_user = User.objects.create_user(
            username='student1', email='student@test.com', password='pass', role='student',
            first_name='S', last_name='One',
        )
        self.student = Student.objects.create(
            user=student_user,
            roll_number='ROLL001',
            year=self.year,
            semester=self.semester,
        )

    def _build_workbook(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['Roll Number', 'Date', 'Status', 'Subject'])
        for row in rows:
            sheet.append(row)
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return buffer

    def test_parse_accepts_roll_number(self):
        uploaded = self._build_workbook([
            ['ROLL001', '2026-06-01', 'Present', 'BCA101'],
        ])
        result = parse_attendance_workbook(uploaded, self.teacher)
        self.assertEqual(result['summary']['valid'], 1)
        self.assertEqual(result['errors'], [])

    def test_parse_accepts_email_fallback(self):
        uploaded = self._build_workbook([
            ['student@test.com', '2026-06-01', 'Absent', 'BCA101'],
        ])
        result = parse_attendance_workbook(uploaded, self.teacher)
        self.assertEqual(result['summary']['valid'], 1)

    def test_parse_rejects_out_of_roster(self):
        other_year = Year.objects.create(department=self.department, number=2)
        other_semester = Semester.objects.create(year=other_year, number=1)
        other_user = User.objects.create_user(
            username='other', email='other@test.com', password='pass', role='student',
            first_name='O', last_name='Ne',
        )
        Student.objects.create(user=other_user, roll_number='OTHER', year=other_year, semester=other_semester)

        uploaded = self._build_workbook([
            ['OTHER', '2026-06-01', 'Present', 'BCA101'],
        ])
        result = parse_attendance_workbook(uploaded, self.teacher)
        self.assertEqual(result['summary']['valid'], 0)
        self.assertTrue(result['errors'])
