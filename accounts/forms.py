from django import forms
from django.core.exceptions import ValidationError

from academics.models import Department, Semester, Subject, Year
from academics.validators import validate_student_placement
from accounts.models import AdminMessage, CollegeClass, CustomUser


class DataAttributeMixin:
    def __init__(self, data_map=None, data_attr='data-id', extra_data_maps=None, *args, **kwargs):
        self.data_map = data_map or {}
        self.data_attr = data_attr
        self.extra_data_maps = extra_data_maps or {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs,
        )
        if value:
            key = str(value)
            if key in self.data_map:
                option['attrs'][self.data_attr] = self.data_map[key]
            for attr, mapping in self.extra_data_maps.items():
                if key in mapping:
                    option['attrs'][attr] = mapping[key]
        return option


class DataAttributeSelect(DataAttributeMixin, forms.Select):
    pass


class DataAttributeSelectMultiple(DataAttributeMixin, forms.SelectMultiple):
    pass


def _apply_data_widget(field, widget):
    widget.choices = field.choices
    field.widget = widget


class CreateUserForm(forms.Form):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'adm-input'}))
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.select_related('semester', 'department').order_by('department', 'semester', 'name'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'adm-input adm-multiselect', 'size': 6}),
        label='Subjects',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.select_related('department').order_by('department', 'number'),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.select_related('year', 'year__department').order_by('year', 'number'),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['department'].label_from_instance = lambda dept: f'{dept.code} — {dept.name}'

        all_years = Year.objects.select_related('department').order_by('department', 'number')
        self.fields['year'].queryset = all_years
        self.fields['year'].label_from_instance = lambda year: f'{year.department.code} — Year {year.number}'
        _apply_data_widget(
            self.fields['year'],
            DataAttributeSelect(
                data_map={str(y.pk): str(y.department_id) for y in all_years},
                data_attr='data-department-id',
                attrs={'class': 'adm-input', 'id': 'id_year'},
            ),
        )

        all_semesters = Semester.objects.select_related('year', 'year__department').order_by('year', 'number')
        self.fields['semester'].queryset = all_semesters
        self.fields['semester'].label_from_instance = lambda sem: f'Semester {sem.number}'
        _apply_data_widget(
            self.fields['semester'],
            DataAttributeSelect(
                data_map={str(s.pk): str(s.year_id) for s in all_semesters},
                data_attr='data-year-id',
                attrs={'class': 'adm-input', 'id': 'id_semester'},
            ),
        )

        all_subjects = Subject.objects.select_related(
            'semester', 'semester__year', 'department',
        ).order_by('department', 'semester__year', 'semester', 'name')
        self.fields['subjects'].queryset = all_subjects
        self.fields['subjects'].label_from_instance = lambda subj: subj.name
        _apply_data_widget(
            self.fields['subjects'],
            DataAttributeSelectMultiple(
                data_map={str(s.pk): str(s.department_id) for s in all_subjects},
                data_attr='data-department-id',
                extra_data_maps={
                    'data-year-id': {str(s.pk): str(s.semester.year_id) for s in all_subjects},
                    'data-semester-id': {str(s.pk): str(s.semester_id) for s in all_subjects},
                },
                attrs={'class': 'adm-input adm-multiselect', 'size': 8, 'id': 'id_subjects'},
            ),
        )

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')

        if role == 'teacher':
            if not cleaned.get('department'):
                self.add_error('department', 'Department is required for teachers.')
            subjects = cleaned.get('subjects')
            if subjects:
                semesters_seen = set()
                for subject in subjects:
                    if subject.department_id != cleaned['department'].pk:
                        self.add_error(
                            'subjects',
                            f'{subject.code} does not belong to the selected department.',
                        )
                        break
                    if subject.semester_id in semesters_seen:
                        self.add_error(
                            'subjects',
                            'Cannot assign multiple subjects from the same semester.',
                        )
                        break
                    semesters_seen.add(subject.semester_id)

        if role == 'student':
            year = cleaned.get('year')
            semester = cleaned.get('semester')
            if not year:
                self.add_error('year', 'Year is required for students.')
            if not semester:
                self.add_error('semester', 'Semester is required for students.')
            if year and semester:
                try:
                    validate_student_placement(year, semester)
                except ValidationError as exc:
                    self.add_error('semester', exc.messages[0])

        return cleaned


class CollegeClassForm(forms.ModelForm):
    class Meta:
        model = CollegeClass
        fields = ['name', 'grade', 'section', 'subject']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. BCA-A'}),
            'grade': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. BCA'}),
            'section': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. A'}),
            'subject': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Database Systems'}),
        }


class ComposeMessageForm(forms.Form):
    TARGET_CHOICES = (
        (AdminMessage.TARGET_INDIVIDUAL, 'Individual'),
        (AdminMessage.TARGET_ROLE_TEACHERS, 'All Teachers'),
        (AdminMessage.TARGET_ROLE_STUDENTS, 'All Students'),
        (AdminMessage.TARGET_ROLE_ALL, 'All Users'),
        (AdminMessage.TARGET_CLASS, 'By Class'),
        (AdminMessage.TARGET_CUSTOM, 'Custom Selection'),
    )

    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'adm-input'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'adm-input adm-textarea', 'rows': 8}),
    )
    target_type = forms.ChoiceField(
        choices=TARGET_CHOICES,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_target_type'}),
    )
    individual_user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role__in=['teacher', 'student']).order_by('first_name'),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input'}),
        label='Recipient',
    )
    target_class = forms.ModelChoiceField(
        queryset=CollegeClass.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input'}),
        label='Class',
    )
    custom_recipients = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role__in=['teacher', 'student']).order_by('first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'adm-input adm-multiselect', 'size': 8}),
        label='Select recipients',
    )

    def clean(self):
        cleaned = super().clean()
        target = cleaned.get('target_type')

        if target == AdminMessage.TARGET_INDIVIDUAL and not cleaned.get('individual_user'):
            self.add_error('individual_user', 'Select a recipient.')
        if target == AdminMessage.TARGET_CLASS and not cleaned.get('target_class'):
            self.add_error('target_class', 'Select a class.')
        if target == AdminMessage.TARGET_CUSTOM and not cleaned.get('custom_recipients'):
            self.add_error('custom_recipients', 'Select at least one recipient.')

        return cleaned


class _TeacherSubjectFieldsMixin:
    def _init_teacher_subject_widgets(self):
        self.fields['department'].label_from_instance = lambda dept: f'{dept.code} — {dept.name}'

        all_years = Year.objects.select_related('department').order_by('department', 'number')
        self.fields['year'].queryset = all_years
        self.fields['year'].label_from_instance = lambda year: f'Year {year.number}'
        _apply_data_widget(
            self.fields['year'],
            DataAttributeSelect(
                data_map={str(y.pk): str(y.department_id) for y in all_years},
                data_attr='data-department-id',
                attrs={'class': 'adm-input', 'id': 'id_year'},
            ),
        )

        all_semesters = Semester.objects.select_related('year', 'year__department').order_by('year', 'number')
        self.fields['semester'].queryset = all_semesters
        self.fields['semester'].label_from_instance = lambda sem: f'Semester {sem.number}'
        _apply_data_widget(
            self.fields['semester'],
            DataAttributeSelect(
                data_map={str(s.pk): str(s.year_id) for s in all_semesters},
                data_attr='data-year-id',
                attrs={'class': 'adm-input', 'id': 'id_semester'},
            ),
        )

        all_subjects = Subject.objects.select_related(
            'semester', 'semester__year', 'department',
        ).order_by('department', 'semester__year', 'semester', 'name')
        self.fields['subjects'].queryset = all_subjects
        self.fields['subjects'].label_from_instance = lambda subj: subj.name
        _apply_data_widget(
            self.fields['subjects'],
            DataAttributeSelectMultiple(
                data_map={str(s.pk): str(s.department_id) for s in all_subjects},
                data_attr='data-department-id',
                extra_data_maps={
                    'data-year-id': {str(s.pk): str(s.semester.year_id) for s in all_subjects},
                    'data-semester-id': {str(s.pk): str(s.semester_id) for s in all_subjects},
                },
                attrs={'class': 'adm-input adm-multiselect', 'size': 8, 'id': 'id_subjects'},
            ),
        )

    def _clean_teacher_subjects(self, cleaned):
        if not cleaned.get('department'):
            self.add_error('department', 'Department is required.')
            return cleaned

        subjects = cleaned.get('subjects')
        if subjects:
            semesters_seen = set()
            for subject in subjects:
                if subject.department_id != cleaned['department'].pk:
                    self.add_error(
                        'subjects',
                        f'{subject.code} does not belong to the selected department.',
                    )
                    break
                if subject.semester_id in semesters_seen:
                    self.add_error(
                        'subjects',
                        'Cannot assign multiple subjects from the same semester.',
                    )
                    break
                semesters_seen.add(subject.semester_id)
        return cleaned


class CreateTeacherForm(_TeacherSubjectFieldsMixin, forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. +91 98765 43210'}),
        label='Phone number',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'adm-input adm-multiselect', 'size': 6}),
        label='Subjects (optional)',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_teacher_subject_widgets()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError('Phone number is required.')
        return phone

    def clean(self):
        cleaned = super().clean()
        return self._clean_teacher_subjects(cleaned)


class EditTeacherForm(_TeacherSubjectFieldsMixin, forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. +91 98765 43210'}),
        label='Phone number',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'adm-input adm-multiselect', 'size': 6}),
        label='Subjects (optional)',
    )

    def __init__(self, *args, teacher=None, **kwargs):
        self.teacher = teacher
        super().__init__(*args, **kwargs)
        self._init_teacher_subject_widgets()
        if teacher:
            user = teacher.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = teacher.phone
            self.fields['department'].initial = teacher.department_id
            self.fields['subjects'].initial = teacher.subject_assignments.values_list(
                'subject_id', flat=True,
            )
            first_assignment = teacher.subject_assignments.select_related(
                'subject__semester',
            ).first()
            if first_assignment:
                self.fields['year'].initial = first_assignment.subject.semester.year_id
                self.fields['semester'].initial = first_assignment.subject.semester_id

    def clean(self):
        cleaned = super().clean()
        return self._clean_teacher_subjects(cleaned)


class _StudentAcademicFieldsMixin:
    def _init_student_academic_widgets(self):
        self.fields['department'].label_from_instance = lambda dept: f'{dept.code} — {dept.name}'

        all_years = Year.objects.select_related('department').order_by('department', 'number')
        self.fields['year'].queryset = all_years
        self.fields['year'].label_from_instance = lambda year: f'Year {year.number}'
        _apply_data_widget(
            self.fields['year'],
            DataAttributeSelect(
                data_map={str(y.pk): str(y.department_id) for y in all_years},
                data_attr='data-department-id',
                attrs={'class': 'adm-input', 'id': 'id_year'},
            ),
        )

        all_semesters = Semester.objects.select_related('year', 'year__department').order_by('year', 'number')
        self.fields['semester'].queryset = all_semesters
        self.fields['semester'].label_from_instance = lambda sem: f'Semester {sem.number}'
        _apply_data_widget(
            self.fields['semester'],
            DataAttributeSelect(
                data_map={str(s.pk): str(s.year_id) for s in all_semesters},
                data_attr='data-year-id',
                attrs={'class': 'adm-input', 'id': 'id_semester'},
            ),
        )

    def _clean_student_placement(self, cleaned):
        department = cleaned.get('department')
        year = cleaned.get('year')
        semester = cleaned.get('semester')

        if not department:
            self.add_error('department', 'Department is required.')
        if not year:
            self.add_error('year', 'Year is required.')
        if not semester:
            self.add_error('semester', 'Semester is required.')

        if department and year and year.department_id != department.pk:
            self.add_error('year', 'Selected year does not belong to the chosen department.')

        if year and semester:
            try:
                validate_student_placement(year, semester)
            except ValidationError as exc:
                self.add_error('semester', exc.messages[0])

        return cleaned


class CreateStudentForm(_StudentAcademicFieldsMixin, forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    roll_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Optional — defaults to username'}),
        label='Roll number',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_student_academic_widgets()

    def clean(self):
        cleaned = super().clean()
        return self._clean_student_placement(cleaned)


class EditStudentForm(_StudentAcademicFieldsMixin, forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    roll_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input'}),
        label='Roll number',
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )

    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        self._init_student_academic_widgets()
        if student:
            user = student.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['roll_number'].initial = student.roll_number or ''
            self.fields['year'].initial = student.year_id
            self.fields['semester'].initial = student.semester_id
            if student.year_id:
                self.fields['department'].initial = student.year.department_id

    def clean(self):
        cleaned = super().clean()
        return self._clean_student_placement(cleaned)


class StudentFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All statuses'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'adm-input adm-search',
        'placeholder': 'Search by name, email, or username…',
    }))
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input'}),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label='All departments',
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.select_related('department').order_by('department', 'number'),
        required=False,
        empty_label='All years',
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.select_related('year').order_by('year', 'number'),
        required=False,
        empty_label='All semesters',
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].label_from_instance = lambda dept: f'{dept.code} — {dept.name}'
        all_years = Year.objects.select_related('department').order_by('department', 'number')
        self.fields['year'].queryset = all_years
        self.fields['year'].label_from_instance = lambda year: f'{year.department.code} Y{year.number}'
        _apply_data_widget(
            self.fields['year'],
            DataAttributeSelect(
                data_map={str(y.pk): str(y.department_id) for y in all_years},
                data_attr='data-department-id',
                attrs={'class': 'adm-input', 'id': 'id_year'},
            ),
        )
        all_semesters = Semester.objects.select_related('year', 'year__department').order_by('year', 'number')
        self.fields['semester'].queryset = all_semesters
        self.fields['semester'].label_from_instance = lambda sem: f'Semester {sem.number}'
        _apply_data_widget(
            self.fields['semester'],
            DataAttributeSelect(
                data_map={str(s.pk): str(s.year_id) for s in all_semesters},
                data_attr='data-year-id',
                attrs={'class': 'adm-input', 'id': 'id_semester'},
            ),
        )


class StudentImportForm(_StudentAcademicFieldsMixin, forms.Form):
    file = forms.FileField(
        label='Excel file (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'class': 'adm-input', 'accept': '.xlsx'}),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_department'}),
        label='Department',
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_year'}),
        label='Year',
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input', 'id': 'id_semester'}),
        label='Semester',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_student_academic_widgets()

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        if not uploaded.name.lower().endswith('.xlsx'):
            raise ValidationError('Upload an Excel file with the .xlsx extension.')
        if uploaded.size > 5 * 1024 * 1024:
            raise ValidationError('File size must be 5 MB or less.')
        return uploaded

    def clean(self):
        cleaned = super().clean()
        return self._clean_student_placement(cleaned)


class TeacherFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All statuses'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'adm-input adm-search',
        'placeholder': 'Search by name, email, or phone…',
    }))
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'adm-input'}),
    )


class UserFilterForm(forms.Form):
    ROLE_CHOICES = (
        ('', 'All roles'),
        ('teacher', 'Teachers'),
        ('student', 'Students'),
    )
    STATUS_CHOICES = (
        ('', 'All statuses'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'adm-input adm-search',
        'placeholder': 'Search by name or email…',
    }))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'adm-input'}))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'adm-input'}))
