from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


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
    login_url = _teacher_login_url()
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
