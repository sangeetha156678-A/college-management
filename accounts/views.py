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
        'redirect': 'teacher_dashboard',
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

    student = getattr(request.user, 'student_profile', None)
    registration_no = request.user.username
    semester = '—'
    course = '—'
    section = '—'
    year_label = '—'
    attendance_metric = '-'
    pending_assignments = 0

    if student:
        registration_no = student.display_roll_number
        semester = f'Semester {student.semester.number}'
        course = student.year.department.name
        year_label = f'Year {student.year.number}'

        from attendance.services.attendance_service import get_attendance_summary_for_student
        from assignments.models import AssignmentSubmission

        summary = get_attendance_summary_for_student(student)
        if summary['overall_total']:
            attendance_metric = f"{summary['overall_percentage']}%"
        pending_assignments = AssignmentSubmission.objects.filter(
            student=student,
            status=AssignmentSubmission.STATUS_PENDING,
        ).count()

    return render(request, 'student_dashboard.html', {
        'student_display_name': display_name,
        'registration_no': registration_no,
        'semester': semester,
        'course': course,
        'year_label': year_label,
        'section': section,
        'active_nav': 'dashboard',
        'current_datetime': timezone.localtime(timezone.now()).strftime('%b %d, %Y %I:%M:%S %p').upper(),
        'metrics': {
            'announcements': 0,
            'attendance': attendance_metric,
            'assessment': pending_assignments,
            'tasks': pending_assignments,
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

    from accounts.services.portal_scope import get_students_for_teacher

    teacher = getattr(request.user, 'teacher_profile', None)
    if teacher is None:
        return redirect('login')
    from assignments.models import AssignmentSubmission, StudyMaterial
    from attendance.models import AttendanceRecord

    students_qs = get_students_for_teacher(teacher).filter(user__is_active=True)
    semester_count = teacher.subject_assignments.values('subject__semester_id').distinct().count()
    subject_ids = teacher.subject_assignments.values_list('subject_id', flat=True)

    attendance_records = AttendanceRecord.objects.filter(subject_id__in=subject_ids)
    attendance_total = attendance_records.count()
    attendance_present = attendance_records.filter(status=AttendanceRecord.STATUS_PRESENT).count()
    attendance_pct = round((attendance_present / attendance_total) * 100) if attendance_total else 0

    pending_submissions = AssignmentSubmission.objects.filter(
        subject_id__in=subject_ids,
        status=AssignmentSubmission.STATUS_PENDING,
    ).count()
    notes_count = StudyMaterial.objects.filter(uploaded_by=teacher, is_active=True).count()

    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'dashboard',
        'stats': {
            'classes': semester_count,
            'students': students_qs.count(),
            'attendance_pct': attendance_pct,
            'assignments': pending_submissions,
            'notes': notes_count,
        },
    })
    return render(request, 'teacher_dashboard.html', ctx)


@login_required(login_url='/accounts/login/')
def teacher_students(request):
    if request.user.role != 'teacher':
        return redirect('login')

    from accounts.services.portal_scope import get_students_for_teacher, get_subjects_for_teacher

    teacher = getattr(request.user, 'teacher_profile', None)
    if teacher is None:
        return redirect('login')

    subjects = get_subjects_for_teacher(teacher)
    subject_id = request.GET.get('subject')
    selected_subject = None

    students = get_students_for_teacher(teacher).filter(user__is_active=True)
    if subject_id:
        selected_subject = subjects.filter(pk=subject_id).first()
        if selected_subject:
            students = get_students_for_teacher(teacher, subject=selected_subject).filter(user__is_active=True)

    ctx = _teacher_portal_context(request)
    ctx.update({
        'students': students,
        'subjects': subjects,
        'selected_subject_id': str(selected_subject.pk) if selected_subject else '',
        'active_nav': 'students',
    })
    return render(request, 'teacher_students.html', ctx)


@login_required(login_url='/accounts/login/')
def lecturer_dashboard(request):
    return teacher_dashboard(request)
