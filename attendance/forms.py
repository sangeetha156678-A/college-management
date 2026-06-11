from django import forms

from accounts.validators import validate_xlsx_file


class AttendanceUploadForm(forms.Form):
    file = forms.FileField(
        label='Excel file (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'class': 'adm-input', 'accept': '.xlsx'}),
    )

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        validate_xlsx_file(uploaded)
        return uploaded
