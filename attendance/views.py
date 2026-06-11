from io import BytesIO

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from openpyxl import Workbook

from accounts.decorators import student_required, teacher_required
from accounts.views import _teacher_portal_context
from attendance.forms import AttendanceUploadForm
from attendance.models import AttendanceRecord
from attendance.services.attendance_service import (
    commit_attendance_records,
    get_attendance_summary_for_student,
    parse_attendance_workbook,
)


@teacher_required
def teacher_attendance(request):
    teacher = request.user.teacher_profile
    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'attendance',
        'form': AttendanceUploadForm(),
        'recent_records': AttendanceRecord.objects.filter(
            recorded_by=teacher,
        ).select_related('student__user', 'subject').order_by('-created_at')[:20],
    })
    return render(request, 'teacher/attendance.html', ctx)


@teacher_required
def teacher_attendance_upload(request):
    teacher = request.user.teacher_profile

    if request.method == 'POST':
        form = AttendanceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            result = parse_attendance_workbook(form.cleaned_data['file'], teacher)
            request.session['attendance_upload_preview'] = result
            return redirect('teacher_attendance_preview')
    else:
        form = AttendanceUploadForm()

    ctx = _teacher_portal_context(request)
    ctx.update({'active_nav': 'attendance', 'form': form})
    return render(request, 'teacher/attendance_upload.html', ctx)


@teacher_required
def teacher_attendance_preview(request):
    preview = request.session.get('attendance_upload_preview')
    if not preview:
        messages.error(request, 'No attendance upload to preview. Please upload a file first.')
        return redirect('teacher_attendance_upload')

    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'attendance',
        'preview': preview,
    })
    return render(request, 'teacher/attendance_preview.html', ctx)


@teacher_required
def teacher_attendance_commit(request):
    if request.method != 'POST':
        return redirect('teacher_attendance_preview')

    preview = request.session.pop('attendance_upload_preview', None)
    if not preview or not preview.get('valid_rows'):
        messages.error(request, 'No valid rows to commit.')
        return redirect('teacher_attendance_upload')

    teacher = request.user.teacher_profile
    count = commit_attendance_records(preview['valid_rows'], teacher)
    messages.success(request, f'Successfully recorded attendance for {count} row(s).')
    return redirect('teacher_attendance')


@teacher_required
def teacher_attendance_template(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Attendance'
    sheet.append(['Roll Number', 'Date', 'Status', 'Subject'])
    sheet.append(['STU001', '2026-06-01', 'Present', 'BCA101'])
    sheet.append(['student@college.edu', '2026-06-01', 'Absent', 'BCA101'])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="attendance_upload_template.xlsx"'
    return response


@student_required
def student_attendance(request):
    student = request.user.student_profile
    summary = get_attendance_summary_for_student(student)

    display_name = request.user.get_full_name().strip() or request.user.username
    ctx = {
        'student_display_name': display_name,
        'registration_no': student.display_roll_number,
        'semester': f'Semester {student.semester.number}',
        'course': student.year.department.name,
        'year_label': f'Year {student.year.number}',
        'active_nav': 'attendance',
        'summary': summary,
    }
    return render(request, 'student/attendance.html', ctx)
