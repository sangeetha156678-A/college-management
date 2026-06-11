import mimetypes

from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import student_required, teacher_required
from accounts.services.portal_scope import (
    get_subjects_for_student,
    get_subjects_for_teacher,
    student_has_subject,
    teacher_has_subject,
)
from accounts.views import _teacher_portal_context
from assignments.forms import AssignmentUploadForm, StudyMaterialForm, SubmissionReviewForm
from assignments.models import AssignmentSubmission, StudyMaterial
from assignments.services.assignment_service import create_submission, review_submission
from assignments.services.material_service import create_study_material, delete_study_material


def _student_portal_context(request, student, active_nav):
    display_name = request.user.get_full_name().strip() or request.user.username
    return {
        'student_display_name': display_name,
        'registration_no': student.display_roll_number,
        'semester': f'Semester {student.semester.number}',
        'course': student.year.department.name,
        'year_label': f'Year {student.year.number}',
        'active_nav': active_nav,
    }


@teacher_required
def teacher_materials(request):
    teacher = request.user.teacher_profile
    subjects = get_subjects_for_teacher(teacher)
    subject_id = request.GET.get('subject')
    materials = StudyMaterial.objects.filter(
        uploaded_by=teacher,
        is_active=True,
    ).select_related('subject').order_by('-uploaded_at')

    if subject_id and teacher_has_subject(teacher, subject_id):
        materials = materials.filter(subject_id=subject_id)

    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'materials',
        'subjects': subjects,
        'materials': materials,
        'selected_subject_id': subject_id,
        'form': StudyMaterialForm(subjects=subjects),
    })
    return render(request, 'teacher/materials.html', ctx)


@teacher_required
def teacher_material_upload(request):
    teacher = request.user.teacher_profile
    subjects = get_subjects_for_teacher(teacher)

    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES, subjects=subjects)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            if not teacher_has_subject(teacher, subject.pk):
                messages.error(request, 'You are not assigned to this subject.')
            else:
                material = create_study_material(
                    teacher=teacher,
                    subject=subject,
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data.get('description', ''),
                    topic=form.cleaned_data.get('topic', ''),
                    uploaded_file=form.cleaned_data['file'],
                )
                from accounts.services.email_service import notify_students_new_material
                notify_students_new_material(material)
                messages.success(request, f'Uploaded "{material.title}" successfully.')
                return redirect('teacher_materials')
    else:
        form = StudyMaterialForm(subjects=subjects)

    ctx = _teacher_portal_context(request)
    ctx.update({'active_nav': 'materials', 'form': form})
    return render(request, 'teacher/material_upload.html', ctx)


@teacher_required
def teacher_material_delete(request, material_id):
    if request.method != 'POST':
        return redirect('teacher_materials')

    teacher = request.user.teacher_profile
    material = get_object_or_404(StudyMaterial, pk=material_id, uploaded_by=teacher, is_active=True)
    title = material.title
    delete_study_material(material)
    messages.success(request, f'Deleted "{title}".')
    return redirect('teacher_materials')


@student_required
def student_materials(request):
    student = request.user.student_profile
    subjects = get_subjects_for_student(student)
    subject_materials = []

    for subject in subjects:
        materials = StudyMaterial.objects.filter(
            subject=subject,
            is_active=True,
        ).select_related('uploaded_by__user').order_by('-uploaded_at')
        subject_materials.append({
            'subject': subject,
            'materials': materials,
        })

    ctx = _student_portal_context(request, student, 'materials')
    ctx['subject_materials'] = subject_materials
    return render(request, 'student/materials.html', ctx)


@student_required
def student_material_download(request, material_id):
    student = request.user.student_profile
    material = get_object_or_404(StudyMaterial, pk=material_id, is_active=True)

    if not student_has_subject(student, material.subject_id):
        raise Http404

    content_type, _ = mimetypes.guess_type(material.file.name)
    response = FileResponse(material.file.open('rb'), content_type=content_type or 'application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{material.title}.pdf"'
    return response


@teacher_required
def teacher_assignments(request):
    teacher = request.user.teacher_profile
    subjects = get_subjects_for_teacher(teacher)
    subject_id = request.GET.get('subject')
    status = request.GET.get('status', '')

    submissions = AssignmentSubmission.objects.filter(
        subject__in=subjects,
    ).select_related('student__user', 'subject').order_by('-submitted_at')

    if subject_id and teacher_has_subject(teacher, subject_id):
        submissions = submissions.filter(subject_id=subject_id)
    if status:
        submissions = submissions.filter(status=status)

    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'assignments',
        'subjects': subjects,
        'submissions': submissions,
        'selected_subject_id': subject_id,
        'selected_status': status,
        'status_choices': AssignmentSubmission.STATUS_CHOICES,
    })
    return render(request, 'teacher/assignments.html', ctx)


@teacher_required
def teacher_assignment_review(request, submission_id):
    teacher = request.user.teacher_profile
    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related('student__user', 'subject'),
        pk=submission_id,
    )

    if not teacher_has_subject(teacher, submission.subject_id):
        raise Http404

    if request.method == 'POST':
        form = SubmissionReviewForm(request.POST)
        if form.is_valid():
            review_submission(
                submission=submission,
                teacher=teacher,
                status=form.cleaned_data['status'],
                feedback=form.cleaned_data.get('feedback', ''),
            )
            from accounts.services.email_service import notify_student_assignment_reviewed
            notify_student_assignment_reviewed(submission)
            messages.success(request, 'Submission review saved.')
            return redirect('teacher_assignments')
    else:
        form = SubmissionReviewForm(initial={
            'status': submission.status if submission.status != AssignmentSubmission.STATUS_PENDING else 'approved',
            'feedback': submission.feedback,
        })

    ctx = _teacher_portal_context(request)
    ctx.update({
        'active_nav': 'assignments',
        'submission': submission,
        'form': form,
    })
    return render(request, 'teacher/assignment_review.html', ctx)


@teacher_required
def teacher_assignment_download(request, submission_id):
    teacher = request.user.teacher_profile
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id)

    if not teacher_has_subject(teacher, submission.subject_id):
        raise Http404

    content_type, _ = mimetypes.guess_type(submission.file.name)
    response = FileResponse(submission.file.open('rb'), content_type=content_type or 'application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{submission.student.display_roll_number}_{submission.subject.code}_v{submission.version}.pdf"'
    )
    return response


@student_required
def student_assignments(request):
    student = request.user.student_profile
    subjects = get_subjects_for_student(student)
    subject_data = []

    for subject in subjects:
        submissions = AssignmentSubmission.objects.filter(
            student=student,
            subject=subject,
        ).select_related('reviewed_by__user').order_by('-version')
        latest = submissions.first()
        subject_data.append({
            'subject': subject,
            'latest': latest,
            'submissions': submissions,
            'can_submit': AssignmentSubmission.can_resubmit(student, subject),
        })

    ctx = _student_portal_context(request, student, 'assignments')
    ctx.update({
        'subject_data': subject_data,
        'form': AssignmentUploadForm(subjects=subjects),
        'status_choices': AssignmentSubmission.STATUS_CHOICES,
    })
    return render(request, 'student/assignments.html', ctx)


@student_required
def student_assignment_upload(request):
    student = request.user.student_profile
    subjects = get_subjects_for_student(student)

    if request.method == 'POST':
        form = AssignmentUploadForm(request.POST, request.FILES, subjects=subjects)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            if not student_has_subject(student, subject.pk):
                messages.error(request, 'You are not enrolled in this subject.')
            else:
                try:
                    submission = create_submission(
                        student=student,
                        subject=subject,
                        uploaded_file=form.cleaned_data['file'],
                    )
                    messages.success(
                        request,
                        f'Assignment submitted for {subject.code} (version {submission.version}).',
                    )
                    return redirect('student_assignments')
                except ValueError as exc:
                    messages.error(request, str(exc))
    else:
        form = AssignmentUploadForm(subjects=subjects)
        subject_id = request.GET.get('subject')
        if subject_id and student_has_subject(student, subject_id):
            form.fields['subject'].initial = subject_id

    ctx = _student_portal_context(request, student, 'assignments')
    ctx['form'] = form
    return render(request, 'student/assignment_upload.html', ctx)


@student_required
def student_assignment_download(request, submission_id):
    student = request.user.student_profile
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id, student=student)

    content_type, _ = mimetypes.guess_type(submission.file.name)
    response = FileResponse(submission.file.open('rb'), content_type=content_type or 'application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{submission.subject.code}_v{submission.version}.pdf"'
    )
    return response
