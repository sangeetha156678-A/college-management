from django.db import transaction
from django.utils import timezone

from assignments.models import AssignmentSubmission


def create_submission(*, student, subject, uploaded_file):
    latest = AssignmentSubmission.latest_for(student, subject)
    if latest and not AssignmentSubmission.can_resubmit(student, subject):
        raise ValueError('You cannot submit a new version until your current submission is reviewed.')

    version = 1 if latest is None else latest.version + 1

    with transaction.atomic():
        submission = AssignmentSubmission.objects.create(
            student=student,
            subject=subject,
            version=version,
            file=uploaded_file,
            status=AssignmentSubmission.STATUS_PENDING,
        )

    return submission


def review_submission(*, submission, teacher, status, feedback=''):
    with transaction.atomic():
        submission.status = status
        submission.feedback = feedback.strip()
        submission.reviewed_by = teacher
        submission.reviewed_at = timezone.now()
        submission.save(update_fields=['status', 'feedback', 'reviewed_by', 'reviewed_at'])

    return submission
