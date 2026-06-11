from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def _student_login_url():
    path = reverse('login')
    base = getattr(settings, 'PORTAL_BASE_URL', '').rstrip('/')
    return f'{base}{path}?role=student' if base else f'{path}?role=student'


def _teacher_login_url():
    path = reverse('login')
    base = getattr(settings, 'PORTAL_BASE_URL', '').rstrip('/')
    return f'{base}{path}?role=lecturer' if base else path


def send_teacher_welcome_email(user, temporary_password):
    login_url = _teacher_login_url()
    subject = 'Welcome to Goodwill College'
    body = (
        'Welcome to Goodwill College.\n\n'
        'Your teacher account has been created.\n\n'
        f'Login Username:\n{user.username}\n\n'
        f'Temporary Password:\n{temporary_password}\n\n'
        f'Login URL:\n{login_url}\n\n'
        'Please login and update your password.'
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_welcome_email(user, temporary_password):
    login_url = _student_login_url()
    subject = 'Welcome to GCCW Portal — Your Account Details'
    body = (
        f'Dear {user.display_name},\n\n'
        f'Your account has been created on the Goodwill Christian College For Women portal.\n\n'
        f'Username: {user.username}\n'
        f'Temporary password: {temporary_password}\n\n'
        f'Login URL: {login_url}\n\n'
        f'Please log in and change your password on first login.\n\n'
        f'Regards,\nGCCW Administration'
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def _should_send_portal_notifications():
    return getattr(settings, 'SEND_PORTAL_NOTIFICATIONS', True)


def notify_students_new_material(material):
    if not _should_send_portal_notifications():
        return

    from accounts.models import Student

    students = Student.objects.filter(
        semester_id=material.subject.semester_id,
        year__department_id=material.subject.department_id,
        user__is_active=True,
    ).select_related('user')

    login_url = _student_login_url()
    for student in students:
        try:
            send_mail(
                f'[GCCW] New study material: {material.title}',
                (
                    f'Dear {student.user.display_name},\n\n'
                    f'New study material has been uploaded for {material.subject.code} — {material.subject.name}.\n\n'
                    f'Title: {material.title}\n'
                    f'Uploaded by: {material.uploaded_by.user.display_name}\n\n'
                    f'View materials: {login_url}\n\n'
                    f'Regards,\nGCCW Portal'
                ),
                settings.DEFAULT_FROM_EMAIL,
                [student.user.email],
                fail_silently=True,
            )
        except Exception:
            pass


def notify_student_assignment_reviewed(submission):
    if not _should_send_portal_notifications():
        return

    student = submission.student
    user = student.user
    status_label = submission.get_status_display()

    try:
        send_mail(
            f'[GCCW] Assignment reviewed: {submission.subject.code}',
            (
                f'Dear {user.display_name},\n\n'
                f'Your assignment for {submission.subject.code} — {submission.subject.name} '
                f'(version {submission.version}) has been reviewed.\n\n'
                f'Status: {status_label}\n'
                f'{f"Feedback: {submission.feedback}" if submission.feedback else ""}\n\n'
                f'Login to view details: {_student_login_url()}\n\n'
                f'Regards,\nGCCW Portal'
            ),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_admin_message_email(recipient_email, subject, body, sender_name):
    email_subject = f'[GCCW] {subject}'
    email_body = (
        f'{body}\n\n'
        f'---\n'
        f'Sent by {sender_name} via GCCW Admin Portal'
    )
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )
