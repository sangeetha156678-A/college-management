import secrets

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from accounts.models import ActivityLog, Student, Teacher, TeacherSubjectAssignment
from accounts.services.email_service import send_teacher_welcome_email, send_welcome_email

User = get_user_model()


def _slug_part(name):
    return slugify(name).replace('-', '')


def _generate_username(first_name, last_name, email):
    first = _slug_part(first_name)
    last = _slug_part(last_name)
    if first and last:
        base = f'{first}.{last}'
    elif first:
        base = first
    else:
        base = _slug_part(email.split('@')[0]) or 'user'
    base = base.lower()[:30]
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f'{base}{suffix}'
        suffix += 1
    return candidate


def _generate_temp_password(first_name, last_name):
    first_initial = (first_name.strip()[:1] or 'U').upper()
    last_initial = (last_name.strip()[:1] or 'S').upper()
    digits = ''.join(secrets.choice('0123456789') for _ in range(5))
    return f'{first_initial}{last_initial}@{digits}'


def create_teacher_account(
    *,
    first_name,
    last_name,
    email,
    phone='',
    department=None,
    subjects=None,
    performed_by=None,
):
    email = email.strip().lower()
    if User.objects.filter(email=email).exists():
        raise ValueError('A teacher with this email already exists.')

    username = _generate_username(first_name, last_name, email)
    temp_password = _generate_temp_password(first_name, last_name)

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role='teacher',
            is_active=True,
        )

        teacher = Teacher.objects.create(
            user=user,
            phone=phone.strip(),
            department=department,
        )
        for subject in subjects or []:
            TeacherSubjectAssignment.objects.create(teacher=teacher, subject=subject)

        ActivityLog.objects.create(
            performed_by=performed_by,
            action=ActivityLog.ACTION_USER_CREATED,
            description=f'Created teacher account for {user.display_name} ({email})',
        )

    send_teacher_welcome_email(user, temp_password)
    return user, temp_password


def update_teacher_profile(
    teacher,
    *,
    first_name,
    last_name,
    email,
    phone='',
    department=None,
    subjects=None,
    performed_by=None,
):
    email = email.strip().lower()
    user = teacher.user
    if User.objects.filter(email=email).exclude(pk=user.pk).exists():
        raise ValueError('A teacher with this email already exists.')

    with transaction.atomic():
        user.first_name = first_name.strip()
        user.last_name = last_name.strip()
        user.email = email
        user.save(update_fields=['first_name', 'last_name', 'email'])

        teacher.phone = phone.strip()
        teacher.department = department
        teacher.save(update_fields=['phone', 'department'])

        if subjects is not None:
            teacher.subject_assignments.all().delete()
            for subject in subjects:
                TeacherSubjectAssignment.objects.create(teacher=teacher, subject=subject)

        ActivityLog.objects.create(
            performed_by=performed_by,
            action=ActivityLog.ACTION_TEACHER_UPDATED,
            description=f'Updated teacher profile for {user.display_name}',
        )

    return teacher


def create_user_account(
    *,
    first_name,
    last_name,
    email,
    role,
    department=None,
    subjects=None,
    year=None,
    semester=None,
    performed_by=None,
):
    if role == 'teacher':
        return create_teacher_account(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            subjects=subjects,
            performed_by=performed_by,
        )

    email = email.strip().lower()
    if User.objects.filter(email=email).exists():
        raise ValueError('A user with this email already exists.')

    username = _generate_username(first_name, last_name, email)
    temp_password = _generate_temp_password(first_name, last_name)

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            is_active=True,
        )

        if role == 'student':
            Student.objects.create(
                user=user,
                year=year,
                semester=semester,
            )

        ActivityLog.objects.create(
            performed_by=performed_by,
            action=ActivityLog.ACTION_USER_CREATED,
            description=f'Created {role} account for {user.display_name} ({email})',
        )

    send_welcome_email(user, temp_password)
    return user, temp_password


def log_user_status_change(user, is_active, performed_by):
    action = (
        ActivityLog.ACTION_USER_ACTIVATED
        if is_active
        else ActivityLog.ACTION_USER_DEACTIVATED
    )
    status = 'activated' if is_active else 'deactivated'
    ActivityLog.objects.create(
        performed_by=performed_by,
        action=action,
        description=f'{status.title()} account for {user.display_name}',
    )
