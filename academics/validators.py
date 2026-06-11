from django.core.exceptions import ValidationError


def validate_semester_belongs_to_year(semester, year):
  if semester is None or year is None:
    return
  if semester.year_id != year.pk:
    raise ValidationError('Semester must belong to the selected year.')


def validate_subject_department_chain(subject):
  if subject.department_id is None or subject.semester_id is None:
    return
  if subject.semester.year.department_id != subject.department_id:
    raise ValidationError(
      'Subject department must match the department of its semester/year chain.'
    )


def validate_student_placement(year, semester):
  validate_semester_belongs_to_year(semester, year)
