from django.conf import settings
from django.core.mail import send_mail


def send_welcome_email(user, temporary_password):
    subject = 'Welcome to GCCW Portal — Your Account Details'
    body = (
        f'Dear {user.display_name},\n\n'
        f'Your account has been created on the Goodwill Christian College For Women portal.\n\n'
        f'Username: {user.username}\n'
        f'Temporary password: {temporary_password}\n\n'
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
