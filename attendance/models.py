from django.db import models


class AttendanceRecord(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'

    STATUS_CHOICES = (
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
    )

    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_by = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendance',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'student__user__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'date'],
                name='unique_attendance_per_student_subject_date',
            ),
        ]
        indexes = [
            models.Index(fields=['subject', 'date']),
        ]

    def __str__(self):
        return f'{self.student} — {self.subject} — {self.date} — {self.status}'
