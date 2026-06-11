from django.core.exceptions import ValidationError
from django.db import models

from academics.validators import validate_subject_department_chain


class Department(models.Model):
  code = models.CharField(max_length=20, unique=True)
  name = models.CharField(max_length=100)
  duration_years = models.PositiveSmallIntegerField(default=3)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ['name']

  def __str__(self):
    return self.name


class Year(models.Model):
  department = models.ForeignKey(
    Department,
    on_delete=models.CASCADE,
    related_name='years',
  )
  number = models.PositiveSmallIntegerField()

  class Meta:
    ordering = ['department', 'number']
    unique_together = [['department', 'number']]

  def __str__(self):
    return f'{self.department.code} — Year {self.number}'


class Semester(models.Model):
  SEMESTER_CHOICES = (
    (1, 'Semester 1'),
    (2, 'Semester 2'),
  )

  year = models.ForeignKey(
    Year,
    on_delete=models.CASCADE,
    related_name='semesters',
  )
  number = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)

  class Meta:
    ordering = ['year', 'number']
    unique_together = [['year', 'number']]

  def __str__(self):
    return f'{self.year} — Semester {self.number}'

  def clean(self):
    super().clean()
    if self.number not in (1, 2):
      raise ValidationError({'number': 'Semester number must be 1 or 2.'})


class Subject(models.Model):
  department = models.ForeignKey(
    Department,
    on_delete=models.CASCADE,
    related_name='subjects',
  )
  semester = models.ForeignKey(
    Semester,
    on_delete=models.CASCADE,
    related_name='subjects',
  )
  code = models.CharField(max_length=20)
  name = models.CharField(max_length=100)
  credits = models.PositiveSmallIntegerField(null=True, blank=True)

  class Meta:
    ordering = ['department', 'semester', 'name']
    unique_together = [['department', 'code']]

  def __str__(self):
    return f'{self.code} — {self.name}'

  def clean(self):
    super().clean()
    validate_subject_department_chain(self)

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
