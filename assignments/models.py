import os
import uuid

from django.db import models


def study_material_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return f'notes/{instance.subject_id}/{safe_name}'


def assignment_submission_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return (
        f'assignments/{instance.student_id}/{instance.subject_id}/'
        f'v{instance.version}/{safe_name}'
    )


class StudyMaterial(models.Model):
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='study_materials',
    )
    uploaded_by = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.CASCADE,
        related_name='uploaded_materials',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to=study_material_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    @property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f'{size} B'
        if size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024 * 1024):.1f} MB'


class AssignmentSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_NEEDS_REWORK = 'needs_rework'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_NEEDS_REWORK, 'Needs Rework'),
    )

    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
    )
    version = models.PositiveSmallIntegerField(default=1)
    file = models.FileField(upload_to=assignment_submission_upload_to)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    feedback = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_submissions',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'version'],
                name='unique_submission_version',
            ),
        ]

    def __str__(self):
        return f'{self.student} — {self.subject} v{self.version}'

    @classmethod
    def latest_for(cls, student, subject):
        return cls.objects.filter(
            student=student,
            subject=subject,
        ).order_by('-version').first()

    @classmethod
    def can_resubmit(cls, student, subject):
        latest = cls.latest_for(student, subject)
        if latest is None:
            return True
        return latest.status in (cls.STATUS_REJECTED, cls.STATUS_NEEDS_REWORK)
