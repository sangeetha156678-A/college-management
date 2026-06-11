from io import BytesIO

from django.contrib import messages

from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.db.models import Count, Q

from django.http import HttpResponse

from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone

from django.views.decorators.http import require_POST

from openpyxl import Workbook



from accounts.decorators import admin_required

from accounts.forms import (
    CollegeClassForm,
    ComposeMessageForm,
    CreateStudentForm,
    CreateTeacherForm,
    EditStudentForm,
    EditTeacherForm,
    StudentFilterForm,
    StudentImportForm,
    TeacherFilterForm,
)

from accounts.models import (

    ActivityLog,

    AdminMessage,

    AdminMessageRecipient,

    ClassEnrollment,

    ClassTeacher,

    CollegeClass,

    Student,

    Teacher,

)

from accounts.services.email_service import send_admin_message_email

from accounts.services.student_service import (
    create_student_account,
    import_students_from_excel,
    update_student_profile,
)
from accounts.services.user_service import (
    create_teacher_account,
    log_user_status_change,
    update_teacher_profile,
)



User = get_user_model()





def _admin_context(request, active_nav='dashboard'):

    full_name = request.user.get_full_name().strip() or request.user.username

    hour = timezone.localtime(timezone.now()).hour

    if hour < 12:

        greeting = 'Good Morning'

    elif hour < 17:

        greeting = 'Good Afternoon'

    else:

        greeting = 'Good Evening'



    return {

        'greeting': greeting,

        'admin_name': full_name,

        'admin_short_name': full_name.split()[0] if full_name else request.user.username,

        'active_nav': active_nav,

    }





def _resolve_message_recipients(target_type, individual_user=None, target_class=None, custom_recipients=None):

    if target_type == AdminMessage.TARGET_INDIVIDUAL:

        return [individual_user]

    if target_type == AdminMessage.TARGET_ROLE_TEACHERS:

        return list(User.objects.filter(role='teacher', is_active=True))

    if target_type == AdminMessage.TARGET_ROLE_STUDENTS:

        return list(User.objects.filter(role='student', is_active=True))

    if target_type == AdminMessage.TARGET_ROLE_ALL:

        return list(User.objects.filter(role__in=['teacher', 'student'], is_active=True))

    if target_type == AdminMessage.TARGET_CLASS:

        users = set()

        for teacher in target_class.teachers.select_related('user'):

            if teacher.user.is_active:

                users.add(teacher.user)

        for student in target_class.students.select_related('user'):

            if student.user.is_active:

                users.add(student.user)

        return list(users)

    if target_type == AdminMessage.TARGET_CUSTOM:

        return list(custom_recipients)

    return []





@login_required(login_url='/accounts/login/')

@admin_required

def admin_dashboard(request):

    ctx = _admin_context(request, 'dashboard')



    teachers = User.objects.filter(role='teacher')

    students = User.objects.filter(role='student')

    classes = CollegeClass.objects.annotate(

        enrolled_count=Count('students', distinct=True),

        assigned_teachers=Count('teachers', distinct=True),

    )



    ctx.update({

        'stats': {

            'teachers': teachers.count(),

            'students': students.count(),

            'classes': classes.count(),

            'active_accounts': User.objects.filter(

                role__in=['teacher', 'student'],

                is_active=True,

            ).count(),

            'inactive_accounts': User.objects.filter(

                role__in=['teacher', 'student'],

                is_active=False,

            ).count(),

        },

        'recent_activity': ActivityLog.objects.select_related('performed_by')[:10],

        'class_stats': classes[:8],

        'recent_messages': AdminMessage.objects.select_related('sent_by')[:5],

    })

    return render(request, 'admin/dashboard.html', ctx)





@login_required(login_url='/accounts/login/')
@admin_required
def admin_teachers(request):
    ctx = _admin_context(request, 'teachers')
    filter_form = TeacherFilterForm(request.GET or None)

    teachers = Teacher.objects.select_related(
        'user',
        'department',
    ).order_by('-user__date_joined')

    if filter_form.is_valid():
        q = filter_form.cleaned_data.get('q', '').strip()
        status = filter_form.cleaned_data.get('status')

        if q:
            teachers = teachers.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
                | Q(phone__icontains=q)
            )
        if status == 'active':
            teachers = teachers.filter(user__is_active=True)
        elif status == 'inactive':
            teachers = teachers.filter(user__is_active=False)

    paginator = Paginator(teachers, 15)
    page = paginator.get_page(request.GET.get('page'))

    new_teacher_credentials = request.session.pop('new_teacher_credentials', None)

    ctx.update({
        'filter_form': filter_form,
        'teachers_page': page,
        'new_teacher_credentials': new_teacher_credentials,
    })
    return render(request, 'admin/teachers.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_teacher_create(request):
    ctx = _admin_context(request, 'teachers')

    if request.method == 'POST':
        form = CreateTeacherForm(request.POST)
        if form.is_valid():
            try:
                user, temp_password = create_teacher_account(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    department=form.cleaned_data['department'],
                    subjects=list(form.cleaned_data.get('subjects') or []),
                    performed_by=request.user,
                )
                request.session['new_teacher_credentials'] = {
                    'name': user.display_name,
                    'email': user.email,
                    'username': user.username,
                    'password': temp_password,
                }
                messages.success(
                    request,
                    f'Teacher account created for {user.display_name}. Login details are shown below.',
                )
                return redirect('admin_teachers')
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = CreateTeacherForm()

    ctx['form'] = form
    return render(request, 'admin/teacher_form.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_teacher_detail(request, teacher_id):
    ctx = _admin_context(request, 'teachers')
    teacher = get_object_or_404(
        Teacher.objects.select_related('user', 'department').prefetch_related(
            'subject_assignments__subject__semester',
            'subject_assignments__subject__department',
        ),
        pk=teacher_id,
    )
    ctx['teacher'] = teacher
    return render(request, 'admin/teacher_detail.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_teacher_edit(request, teacher_id):
    ctx = _admin_context(request, 'teachers')
    teacher = get_object_or_404(
        Teacher.objects.select_related('user', 'department'),
        pk=teacher_id,
    )

    if request.method == 'POST':
        form = EditTeacherForm(request.POST, teacher=teacher)
        if form.is_valid():
            try:
                update_teacher_profile(
                    teacher,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    department=form.cleaned_data['department'],
                    subjects=list(form.cleaned_data.get('subjects') or []),
                    performed_by=request.user,
                )
                messages.success(request, f'Teacher profile updated for {teacher.user.display_name}.')
                return redirect('admin_teacher_detail', teacher_id=teacher.pk)
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = EditTeacherForm(teacher=teacher)

    ctx.update({'form': form, 'teacher': teacher})
    return render(request, 'admin/teacher_edit.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
@require_POST
def admin_teacher_toggle(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id, user__role='teacher')
    user = teacher.user
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    log_user_status_change(user, user.is_active, request.user)

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'{user.display_name} has been {status}.')
    return redirect(request.POST.get('next') or 'admin_teachers')


@login_required(login_url='/accounts/login/')
@admin_required
def admin_students(request):
    ctx = _admin_context(request, 'students')
    filter_form = StudentFilterForm(request.GET or None)

    students = Student.objects.select_related(
        'user',
        'year',
        'year__department',
        'semester',
    ).filter(user__role='student').order_by('-user__date_joined')

    if filter_form.is_valid():
        q = filter_form.cleaned_data.get('q', '').strip()
        status = filter_form.cleaned_data.get('status')
        department = filter_form.cleaned_data.get('department')
        year = filter_form.cleaned_data.get('year')
        semester = filter_form.cleaned_data.get('semester')

        if q:
            students = students.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
                | Q(user__username__icontains=q)
            )
        if status == 'active':
            students = students.filter(user__is_active=True)
        elif status == 'inactive':
            students = students.filter(user__is_active=False)
        if department:
            students = students.filter(year__department=department)
        if year:
            students = students.filter(year=year)
        if semester:
            students = students.filter(semester=semester)

    paginator = Paginator(students, 15)
    page = paginator.get_page(request.GET.get('page'))

    ctx.update({
        'filter_form': filter_form,
        'students_page': page,
        'new_student_credentials': request.session.pop('new_student_credentials', None),
        'import_summary': request.session.pop('student_import_summary', None),
    })
    return render(request, 'admin/students.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_student_create(request):
    ctx = _admin_context(request, 'students')

    if request.method == 'POST':
        form = CreateStudentForm(request.POST)
        if form.is_valid():
            try:
                student, temp_password = create_student_account(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    year=form.cleaned_data['year'],
                    semester=form.cleaned_data['semester'],
                    performed_by=request.user,
                )
                user = student.user
                request.session['new_student_credentials'] = {
                    'name': user.display_name,
                    'email': user.email,
                    'username': user.username,
                    'password': temp_password,
                }
                messages.success(
                    request,
                    f'Student account created for {user.display_name}. Login details are shown below.',
                )
                return redirect('admin_students')
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = CreateStudentForm()

    ctx['form'] = form
    return render(request, 'admin/student_form.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_student_import(request):
    ctx = _admin_context(request, 'students')

    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            result = import_students_from_excel(
                form.cleaned_data['file'],
                year=form.cleaned_data['year'],
                semester=form.cleaned_data['semester'],
                performed_by=request.user,
            )
            request.session['student_import_summary'] = result
            if result['created']:
                messages.success(
                    request,
                    f"Imported {result['created']} student(s) into "
                    f"{form.cleaned_data['department'].code} — "
                    f"Year {form.cleaned_data['year'].number}, "
                    f"Semester {form.cleaned_data['semester'].number}.",
                )
            if result['skipped']:
                messages.warning(
                    request,
                    f"{result['skipped']} row(s) were skipped. Review the import summary below.",
                )
            if not result['created'] and not result['skipped']:
                messages.error(request, 'No student rows were found in the uploaded file.')
            return redirect('admin_students')
    else:
        form = StudentImportForm()

    ctx['form'] = form
    return render(request, 'admin/student_import.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_student_import_template(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Students'
    sheet.append(['first_name', 'last_name', 'email'])
    sheet.append(['Jane', 'Doe', 'jane.doe@example.com'])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
    return response


@login_required(login_url='/accounts/login/')
@admin_required
def admin_student_detail(request, student_id):
    ctx = _admin_context(request, 'students')
    student = get_object_or_404(
        Student.objects.select_related('user', 'year', 'year__department', 'semester'),
        pk=student_id,
        user__role='student',
    )
    ctx['student'] = student
    return render(request, 'admin/student_detail.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
def admin_student_edit(request, student_id):
    ctx = _admin_context(request, 'students')
    student = get_object_or_404(
        Student.objects.select_related('user', 'year', 'year__department', 'semester'),
        pk=student_id,
        user__role='student',
    )

    if request.method == 'POST':
        form = EditStudentForm(request.POST, student=student)
        if form.is_valid():
            try:
                update_student_profile(
                    student,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    year=form.cleaned_data['year'],
                    semester=form.cleaned_data['semester'],
                    performed_by=request.user,
                )
                messages.success(request, f'Student profile updated for {student.user.display_name}.')
                return redirect('admin_student_detail', student_id=student.pk)
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = EditStudentForm(student=student)

    ctx.update({'form': form, 'student': student})
    return render(request, 'admin/student_edit.html', ctx)


@login_required(login_url='/accounts/login/')
@admin_required
@require_POST
def admin_student_toggle(request, student_id):
    student = get_object_or_404(Student, pk=student_id, user__role='student')
    user = student.user
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    log_user_status_change(user, user.is_active, request.user)

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'{user.display_name} has been {status}.')
    return redirect(request.POST.get('next') or 'admin_students')


@login_required(login_url='/accounts/login/')

@admin_required

def admin_classes(request):

    ctx = _admin_context(request, 'classes')

    class_list = CollegeClass.objects.annotate(

        enrolled_count=Count('students', distinct=True),

        assigned_teachers=Count('teachers', distinct=True),

    )

    ctx['classes'] = class_list

    return render(request, 'admin/classes.html', ctx)





@login_required(login_url='/accounts/login/')

@admin_required

def admin_class_create(request):

    ctx = _admin_context(request, 'classes')



    if request.method == 'POST':

        form = CollegeClassForm(request.POST)

        if form.is_valid():

            college_class = form.save()

            ActivityLog.objects.create(

                performed_by=request.user,

                action=ActivityLog.ACTION_CLASS_CREATED,

                description=f'Created class {college_class.name}',

            )

            messages.success(request, f'Class "{college_class.name}" created.')

            return redirect('admin_class_detail', class_id=college_class.pk)

    else:

        form = CollegeClassForm()



    ctx['form'] = form

    return render(request, 'admin/class_form.html', ctx)





@login_required(login_url='/accounts/login/')

@admin_required

def admin_class_detail(request, class_id):

    ctx = _admin_context(request, 'classes')

    college_class = get_object_or_404(

        CollegeClass.objects.prefetch_related(

            'teachers__user',

            'students__user',

        ),

        pk=class_id,

    )



    assigned_teacher_ids = college_class.teachers.values_list('pk', flat=True)

    enrolled_student_ids = college_class.students.values_list('pk', flat=True)



    available_teachers = Teacher.objects.exclude(pk__in=assigned_teacher_ids).select_related('user')

    available_students = Student.objects.exclude(pk__in=enrolled_student_ids).select_related('user')



    ctx.update({

        'college_class': college_class,

        'available_teachers': available_teachers,

        'available_students': available_students,

        'all_classes': CollegeClass.objects.exclude(pk=class_id),

    })

    return render(request, 'admin/class_detail.html', ctx)





@login_required(login_url='/accounts/login/')

@admin_required

@require_POST

def admin_class_assign_teachers(request, class_id):

    college_class = get_object_or_404(CollegeClass, pk=class_id)

    teacher_ids = request.POST.getlist('teacher_ids')



    for teacher in Teacher.objects.filter(pk__in=teacher_ids):

        _, created = ClassTeacher.objects.get_or_create(

            college_class=college_class,

            teacher=teacher,

        )

        if created:

            ActivityLog.objects.create(

                performed_by=request.user,

                action=ActivityLog.ACTION_TEACHER_ASSIGNED,

                description=f'Assigned {teacher} to {college_class.name}',

            )



    messages.success(request, 'Teacher assignment updated.')

    return redirect('admin_class_detail', class_id=class_id)





@login_required(login_url='/accounts/login/')

@admin_required

@require_POST

def admin_class_remove_teacher(request, class_id, teacher_id):

    college_class = get_object_or_404(CollegeClass, pk=class_id)

    ClassTeacher.objects.filter(college_class=college_class, teacher_id=teacher_id).delete()

    messages.success(request, 'Teacher removed from class.')

    return redirect('admin_class_detail', class_id=class_id)





@login_required(login_url='/accounts/login/')

@admin_required

@require_POST

def admin_class_enroll_students(request, class_id):

    college_class = get_object_or_404(CollegeClass, pk=class_id)

    student_ids = request.POST.getlist('student_ids')



    for student in Student.objects.filter(pk__in=student_ids):

        _, created = ClassEnrollment.objects.get_or_create(

            college_class=college_class,

            student=student,

        )

        if created:

            ActivityLog.objects.create(

                performed_by=request.user,

                action=ActivityLog.ACTION_STUDENT_ENROLLED,

                description=f'Enrolled {student} in {college_class.name}',

            )



    messages.success(request, 'Student enrollment updated.')

    return redirect('admin_class_detail', class_id=class_id)





@login_required(login_url='/accounts/login/')

@admin_required

@require_POST

def admin_class_remove_student(request, class_id, student_id):

    college_class = get_object_or_404(CollegeClass, pk=class_id)

    ClassEnrollment.objects.filter(college_class=college_class, student_id=student_id).delete()

    messages.success(request, 'Student removed from class.')

    return redirect('admin_class_detail', class_id=class_id)





@login_required(login_url='/accounts/login/')

@admin_required

@require_POST

def admin_class_reassign_teacher(request, class_id, teacher_id):

    """Move a teacher from this class to another class."""

    college_class = get_object_or_404(CollegeClass, pk=class_id)

    target_class_id = request.POST.get('target_class_id')

    target_class = get_object_or_404(CollegeClass, pk=target_class_id)



    ClassTeacher.objects.filter(college_class=college_class, teacher_id=teacher_id).delete()

    ClassTeacher.objects.get_or_create(college_class=target_class, teacher_id=teacher_id)



    ActivityLog.objects.create(

        performed_by=request.user,

        action=ActivityLog.ACTION_TEACHER_ASSIGNED,

        description=f'Reassigned teacher to {target_class.name}',

    )

    messages.success(request, f'Teacher reassigned to {target_class.name}.')

    return redirect('admin_class_detail', class_id=class_id)





@login_required(login_url='/accounts/login/')

@admin_required

def admin_messages_compose(request):

    ctx = _admin_context(request, 'messages')



    if request.method == 'POST':

        form = ComposeMessageForm(request.POST)

        if form.is_valid():

            recipients = _resolve_message_recipients(

                form.cleaned_data['target_type'],

                individual_user=form.cleaned_data.get('individual_user'),

                target_class=form.cleaned_data.get('target_class'),

                custom_recipients=form.cleaned_data.get('custom_recipients'),

            )

            recipients = [u for u in recipients if u and u.email]



            if not recipients:

                messages.error(request, 'No recipients with valid email addresses found.')

            else:

                admin_message = AdminMessage.objects.create(

                    sent_by=request.user,

                    subject=form.cleaned_data['subject'],

                    body=form.cleaned_data['body'],

                    target_type=form.cleaned_data['target_type'],

                    target_class=form.cleaned_data.get('target_class'),

                    recipient_count=len(recipients),

                )



                sender_name = request.user.display_name

                for recipient in recipients:

                    AdminMessageRecipient.objects.create(

                        message=admin_message,

                        user=recipient,

                        email=recipient.email,

                    )

                    send_admin_message_email(

                        recipient.email,

                        form.cleaned_data['subject'],

                        form.cleaned_data['body'],

                        sender_name,

                    )



                ActivityLog.objects.create(

                    performed_by=request.user,

                    action=ActivityLog.ACTION_MESSAGE_SENT,

                    description=f'Sent "{admin_message.subject}" to {len(recipients)} recipient(s)',

                )

                messages.success(request, f'Message sent to {len(recipients)} recipient(s).')

                return redirect('admin_messages_history')

    else:

        form = ComposeMessageForm()



    ctx['form'] = form

    return render(request, 'admin/messages_compose.html', ctx)





@login_required(login_url='/accounts/login/')

@admin_required

def admin_messages_history(request):

    ctx = _admin_context(request, 'messages')

    message_list = AdminMessage.objects.select_related('sent_by', 'target_class')



    paginator = Paginator(message_list, 20)

    ctx['messages_page'] = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin/messages_history.html', ctx)

