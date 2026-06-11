from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from academics.validators import validate_student_placement


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        return full or self.username


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    year = models.ForeignKey(
        'academics.Year',
        on_delete=models.PROTECT,
        related_name='students',
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.PROTECT,
        related_name='students',
    )

    def __str__(self):
        return self.user.display_name

    @property
    def display_roll_number(self):
        return self.roll_number or self.user.username

    @property
    def department(self):
        if self.year_id:
            return self.year.department
        return None

    def clean(self):
        super().clean()
        validate_student_placement(self.year, self.semester)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.PROTECT,
        related_name='teachers',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.display_name


class TeacherSubjectAssignment(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='subject_assignments',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['teacher', 'subject']]

    def __str__(self):
        return f'{self.teacher} → {self.subject}'

    def clean(self):
        super().clean()
        if not self.teacher_id or not self.subject_id:
            return

        if self.teacher.department_id and self.subject.department_id:
            if self.teacher.department_id != self.subject.department_id:
                raise ValidationError(
                    "Teacher's home department must match the subject's department."
                )

        conflict = TeacherSubjectAssignment.objects.filter(
            teacher=self.teacher,
            subject__semester=self.subject.semester,
        ).exclude(pk=self.pk)
        if conflict.exists():
            raise ValidationError('Teacher already assigned to a subject in this semester.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CollegeClass(models.Model):
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    teachers = models.ManyToManyField(Teacher, through='ClassTeacher', related_name='classes')
    students = models.ManyToManyField(Student, through='ClassEnrollment', related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'classes'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()

    @property
    def teacher_count(self):
        return self.teachers.count()


class ClassTeacher(models.Model):
    college_class = models.ForeignKey(CollegeClass, on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['college_class', 'teacher']]

    def __str__(self):
        return f'{self.teacher} → {self.college_class}'


class ClassEnrollment(models.Model):
    college_class = models.ForeignKey(CollegeClass, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['college_class', 'student']]

    def __str__(self):
        return f'{self.student} in {self.college_class}'


class AdminMessage(models.Model):
    TARGET_INDIVIDUAL = 'individual'
    TARGET_ROLE_TEACHERS = 'role_teachers'
    TARGET_ROLE_STUDENTS = 'role_students'
    TARGET_ROLE_ALL = 'role_all'
    TARGET_CLASS = 'class'
    TARGET_CUSTOM = 'custom'

    TARGET_CHOICES = (
        (TARGET_INDIVIDUAL, 'Individual'),
        (TARGET_ROLE_TEACHERS, 'All Teachers'),
        (TARGET_ROLE_STUDENTS, 'All Students'),
        (TARGET_ROLE_ALL, 'All Users'),
        (TARGET_CLASS, 'By Class'),
        (TARGET_CUSTOM, 'Custom Selection'),
    )

    sent_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_admin_messages',
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_class = models.ForeignKey(
        CollegeClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
    )
    recipient_count = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return self.subject


class AdminMessageRecipient(models.Model):
    message = models.ForeignKey(AdminMessage, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_admin_messages')
    email = models.EmailField()

    def __str__(self):
        return f'{self.email} — {self.message.subject}'


class ActivityLog(models.Model):
    ACTION_USER_CREATED = 'user_created'
    ACTION_USER_ACTIVATED = 'user_activated'
    ACTION_USER_DEACTIVATED = 'user_deactivated'
    ACTION_TEACHER_UPDATED = 'teacher_updated'
    ACTION_STUDENT_UPDATED = 'student_updated'
    ACTION_CLASS_CREATED = 'class_created'
    ACTION_TEACHER_ASSIGNED = 'teacher_assigned'
    ACTION_STUDENT_ENROLLED = 'student_enrolled'
    ACTION_MESSAGE_SENT = 'message_sent'

    ACTION_CHOICES = (
        (ACTION_USER_CREATED, 'User created'),
        (ACTION_USER_ACTIVATED, 'User activated'),
        (ACTION_USER_DEACTIVATED, 'User deactivated'),
        (ACTION_TEACHER_UPDATED, 'Teacher updated'),
        (ACTION_STUDENT_UPDATED, 'Student updated'),
        (ACTION_CLASS_CREATED, 'Class created'),
        (ACTION_TEACHER_ASSIGNED, 'Teacher assigned'),
        (ACTION_STUDENT_ENROLLED, 'Student enrolled'),
        (ACTION_MESSAGE_SENT, 'Message sent'),
    )

    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs',
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description
