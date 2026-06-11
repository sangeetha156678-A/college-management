from django import forms

from academics.models import Subject
from accounts.validators import validate_pdf_file


class StudyMaterialForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input'}),
        label='Subject',
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'adm-input'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'adm-input', 'rows': 3}),
    )
    topic = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'adm-input'}),
    )
    file = forms.FileField(
        label='PDF file',
        widget=forms.ClearableFileInput(attrs={'class': 'adm-input', 'accept': '.pdf'}),
    )

    def __init__(self, *args, subjects=None, **kwargs):
        super().__init__(*args, **kwargs)
        if subjects is not None:
            self.fields['subject'].queryset = subjects
            self.fields['subject'].label_from_instance = lambda s: f'{s.code} — {s.name}'

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        validate_pdf_file(uploaded)
        return uploaded


class AssignmentUploadForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'adm-input'}),
        label='Subject',
    )
    file = forms.FileField(
        label='Assignment PDF',
        widget=forms.ClearableFileInput(attrs={'class': 'adm-input', 'accept': '.pdf'}),
    )

    def __init__(self, *args, subjects=None, **kwargs):
        super().__init__(*args, **kwargs)
        if subjects is not None:
            self.fields['subject'].queryset = subjects
            self.fields['subject'].label_from_instance = lambda s: f'{s.code} — {s.name}'

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        validate_pdf_file(uploaded)
        return uploaded


class SubmissionReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('needs_rework', 'Needs Rework'),
        ],
        widget=forms.Select(attrs={'class': 'adm-input'}),
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'adm-input', 'rows': 3, 'placeholder': 'Optional feedback for the student'}),
    )
