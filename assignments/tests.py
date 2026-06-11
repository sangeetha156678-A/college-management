from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from academics.models import Department, Semester, Subject, Year
from accounts.models import Student, Teacher, TeacherSubjectAssignment
from assignments.models import AssignmentSubmission
from assignments.services.assignment_service import create_submission, review_submission

User = get_user_model()


class AssignmentSubmissionTests(TestCase):
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
        self.pdf = SimpleUploadedFile('test.pdf', b'%PDF-1.4 test', content_type='application/pdf')

    def test_submission_versioning(self):
        first = create_submission(student=self.student, subject=self.subject, uploaded_file=self.pdf)
        self.assertEqual(first.version, 1)

        review_submission(
            submission=first,
            teacher=self.teacher,
            status=AssignmentSubmission.STATUS_REJECTED,
            feedback='Please revise',
        )

        second = create_submission(
            student=self.student,
            subject=self.subject,
            uploaded_file=SimpleUploadedFile('v2.pdf', b'%PDF-1.4 v2', content_type='application/pdf'),
        )
        self.assertEqual(second.version, 2)
        self.assertEqual(AssignmentSubmission.objects.filter(student=self.student, subject=self.subject).count(), 2)

    def test_cannot_resubmit_while_pending(self):
        create_submission(student=self.student, subject=self.subject, uploaded_file=self.pdf)
        with self.assertRaises(ValueError):
            create_submission(
                student=self.student,
                subject=self.subject,
                uploaded_file=SimpleUploadedFile('dup.pdf', b'%PDF-1.4 dup', content_type='application/pdf'),
            )
