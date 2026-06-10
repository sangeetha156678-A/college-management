from django import forms

from accounts.models import AdminMessage, CollegeClass, CustomUser


class CreateUserForm(forms.Form):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'adm-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'adm-input'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'adm-input'}))
    subject = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Mathematics'}),
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Science'}),
    )
    course = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. BCA (AI & ML)'}),
    )
    semester = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Sem II'}),
    )

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        if role == 'teacher' and not cleaned.get('subject'):
            self.add_error('subject', 'Subject is required for teachers.')
        if role == 'student' and not cleaned.get('course'):
            self.add_error('course', 'Course is required for students.')
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
