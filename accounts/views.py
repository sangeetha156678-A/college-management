from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from django.contrib.auth import get_user_model

from accounts.demo_users import DEMO_USERS, ensure_demo_users_if_needed

User = get_user_model()

# Maps login tab -> database role -> redirect URL name
LOGIN_ROLE_MAP = {
    'admin': {
        'db_role': 'admin',
        'label': 'Admin',
        'redirect': 'admin_dashboard',
    },
    'lecturer': {
        'db_role': 'teacher',
        'label': 'Lecturer',
        'redirect': 'lecturer_dashboard',
    },
    'student': {
        'db_role': 'student',
        'label': 'Student',
        'redirect': 'student_dashboard',
    },
}


def _active_role_from_request(request):
    role = request.GET.get('role') or request.POST.get('login_role', 'student')
    if role not in LOGIN_ROLE_MAP:
        role = 'student'
    return role


def _login_context(active_role, error=None, username=''):
    info = LOGIN_ROLE_MAP[active_role]
    context = {
        'active_role': active_role,
        'role_label': info['label'],
        'error': error,
        'username': username,
    }
    if settings.DEBUG:
        context['demo_credentials'] = DEMO_USERS
    return context


def user_login(request):
    if getattr(settings, 'AUTO_CREATE_DEMO_USERS', True):
        ensure_demo_users_if_needed()

    active_role = _active_role_from_request(request)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        posted_role = request.POST.get('login_role', active_role)
        if posted_role in LOGIN_ROLE_MAP:
            active_role = posted_role

        role_info = LOGIN_ROLE_MAP[active_role]

        if not username or not password:
            return render(
                request,
                'login.html',
                _login_context(
                    active_role,
                    error='Please enter your username and password.',
                    username=username,
                ),
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            inactive_user = User.objects.filter(username=username).first()
            if (
                inactive_user
                and not inactive_user.is_active
                and inactive_user.check_password(password)
            ):
                return render(
                    request,
                    'login.html',
                    _login_context(
                        active_role,
                        error=(
                            'Your account has been deactivated.\n'
                            'Please contact administration.'
                        ),
                        username=username,
                    ),
                )
            return render(
                request,
                'login.html',
                _login_context(
                    active_role,
                    error='Invalid credentials',
                    username=username,
                ),
            )

        if user.role != role_info['db_role']:
            return render(
                request,
                'login.html',
                _login_context(
                    active_role,
                    error='Invalid credentials',
                    username=username,
                ),
            )

        login(request, user)
        request.session['login_role'] = active_role
        return redirect(role_info['redirect'])

    return render(request, 'login.html', _login_context(active_role))


@require_POST
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/accounts/login/')
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')

    display_name = request.user.get_full_name().strip() or request.user.username
    if display_name == request.user.username:
        display_name = display_name.upper()

    return render(request, 'student_dashboard.html', {
        'student_display_name': display_name,
        'registration_no': getattr(request.user, 'registration_no', '25BBCAI008'),
        'semester': 'Sem II',
        'course': 'BCA (AI & ML)',
        'section': 'A',
        'current_datetime': timezone.localtime(timezone.now()).strftime('%b %d, %Y %I:%M:%S %p').upper(),
        'metrics': {
            'announcements': 0,
            'attendance': '-',
            'assessment': 0,
            'tasks': 4,
            'placement': 0,
        },
    })


def _teacher_portal_context(request):
    full_name = request.user.get_full_name().strip()
    if full_name:
        teacher_name = full_name
        if not full_name.lower().startswith(('mr.', 'ms.', 'mrs.', 'dr.')):
            teacher_name = f'Ms. {full_name}'
    else:
        teacher_name = request.user.username

    hour = timezone.localtime(timezone.now()).hour
    if hour < 12:
        greeting = 'Good Morning'
    elif hour < 17:
        greeting = 'Good Afternoon'
    else:
        greeting = 'Good Evening'

    return {
        'greeting': greeting,
        'teacher_name': teacher_name,
        'teacher_short_name': teacher_name.replace('Ms. ', '').replace('Mr. ', '').split()[0],
    }


@login_required(login_url='/accounts/login/')
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')

    from accounts.services.student_service import get_students_for_teacher

    teacher = getattr(request.user, 'teacher_profile', None)
    if teacher is None:
        return redirect('login')

    students_qs = get_students_for_teacher(teacher).filter(user__is_active=True)
    semester_count = teacher.subject_assignments.values('subject__semester_id').distinct().count()

    ctx = _teacher_portal_context(request)
    ctx.update({
        'stats': {
            'classes': semester_count,
            'students': students_qs.count(),
            'attendance_pct': 87,
            'assignments': 12,
            'notes': 24,
        },
    })
    return render(request, 'teacher_dashboard.html', ctx)


@login_required(login_url='/accounts/login/')
def teacher_students(request):
    if request.user.role != 'teacher':
        return redirect('login')

    from accounts.services.student_service import get_students_for_teacher

    teacher = getattr(request.user, 'teacher_profile', None)
    if teacher is None:
        return redirect('login')

    students = get_students_for_teacher(teacher).filter(user__is_active=True)

    ctx = _teacher_portal_context(request)
    ctx.update({
        'students': students,
        'active_nav': 'students',
    })
    return render(request, 'teacher_students.html', ctx)


@login_required(login_url='/accounts/login/')
def lecturer_dashboard(request):
    return teacher_dashboard(request)
