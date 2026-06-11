from django.conf import settings
from django.core.exceptions import ValidationError


def validate_pdf_file(uploaded):
    if not uploaded.name.lower().endswith('.pdf'):
        raise ValidationError('Upload a PDF file with the .pdf extension.')
    max_size = getattr(settings, 'MAX_PDF_SIZE', 10 * 1024 * 1024)
    if uploaded.size > max_size:
        raise ValidationError(f'File size must be {max_size // (1024 * 1024)} MB or less.')


def validate_xlsx_file(uploaded):
    if not uploaded.name.lower().endswith('.xlsx'):
        raise ValidationError('Upload an Excel file with the .xlsx extension.')
    max_size = getattr(settings, 'MAX_XLSX_SIZE', 5 * 1024 * 1024)
    if uploaded.size > max_size:
        raise ValidationError(f'File size must be {max_size // (1024 * 1024)} MB or less.')
