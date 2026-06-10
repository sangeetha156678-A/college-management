"""
Demo user definitions and auto-provisioning for local development.
"""

from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError

from accounts.models import Student, Teacher

DEMO_USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'email': 'admin@goodwillcollege.edu',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'lecturer',
        'password': 'lecturer123',
        'role': 'teacher',
        'email': 'lecturer@goodwillcollege.edu',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'student',
        'password': 'student123',
        'role': 'student',
        'email': 'student@goodwillcollege.edu',
        'is_staff': False,
        'is_superuser': False,
    },
]


def ensure_demo_users():
    """Create or update demo users. Safe to call multiple times."""
    User = get_user_model()

    try:
        User.objects.exists()
    except (OperationalError, ProgrammingError):
        return

    for data in DEMO_USERS:
        username = data['username']
        user, _created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': data['email'],
                'role': data['role'],
                'is_staff': data['is_staff'],
                'is_superuser': data['is_superuser'],
                'is_active': True,
            },
        )

        user.email = data['email']
        user.role = data['role']
        user.is_staff = data['is_staff']
        user.is_superuser = data['is_superuser']
        user.is_active = True
        user.set_password(data['password'])
        user.save()

        if data['role'] == 'teacher':
            Teacher.objects.get_or_create(
                user=user,
                defaults={'subject': 'Computer Science', 'department': 'BCA'},
            )
        elif data['role'] == 'student':
            Student.objects.get_or_create(
                user=user,
                defaults={'course': 'BCA (AI & ML)', 'semester': 'Sem II'},
            )


_demo_users_ensured = False


def ensure_demo_users_if_needed():
    """Lazy provisioning on first login page load (e.g. after runserver)."""
    global _demo_users_ensured
    if _demo_users_ensured:
        return
    ensure_demo_users()
    _demo_users_ensured = True


def ensure_demo_users_on_migrate(sender, **kwargs):
    from django.conf import settings

    if not getattr(settings, 'AUTO_CREATE_DEMO_USERS', True):
        return
    ensure_demo_users()
