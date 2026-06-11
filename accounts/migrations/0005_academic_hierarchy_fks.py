import django.db.models.deletion
from django.db import migrations, models


def migrate_legacy_profiles(apps, schema_editor):
  Department = apps.get_model('academics', 'Department')
  Year = apps.get_model('academics', 'Year')
  Semester = apps.get_model('academics', 'Semester')
  Student = apps.get_model('accounts', 'Student')
  Teacher = apps.get_model('accounts', 'Teacher')

  bca = Department.objects.filter(code='BCA').first()
  if not bca:
    return

  year1 = Year.objects.filter(department=bca, number=1).first()
  sem2 = Semester.objects.filter(year=year1, number=2).first() if year1 else None

  if year1 and sem2:
    Student.objects.filter(year__isnull=True).update(year=year1, current_semester=sem2)

  Teacher.objects.filter(department__isnull=True).update(department=bca)


def reverse_migrate_legacy_profiles(apps, schema_editor):
  pass


class Migration(migrations.Migration):

  dependencies = [
    ('academics', '0002_seed_academic_data'),
    ('accounts', '0004_alter_customuser_role_alter_student_course_and_more'),
  ]

  operations = [
    migrations.AddField(
      model_name='student',
      name='year',
      field=models.ForeignKey(
        blank=True,
        null=True,
        on_delete=django.db.models.deletion.PROTECT,
        related_name='students',
        to='academics.year',
      ),
    ),
    migrations.AddField(
      model_name='student',
      name='current_semester',
      field=models.ForeignKey(
        blank=True,
        null=True,
        on_delete=django.db.models.deletion.PROTECT,
        related_name='students',
        to='academics.semester',
      ),
    ),
    migrations.RemoveField(
      model_name='teacher',
      name='department',
    ),
    migrations.AddField(
      model_name='teacher',
      name='department',
      field=models.ForeignKey(
        blank=True,
        null=True,
        on_delete=django.db.models.deletion.PROTECT,
        related_name='teachers',
        to='academics.department',
      ),
    ),
    migrations.CreateModel(
      name='TeacherSubjectAssignment',
      fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('assigned_at', models.DateTimeField(auto_now_add=True)),
        ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='academics.subject')),
        ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_assignments', to='accounts.teacher')),
      ],
      options={
        'unique_together': {('teacher', 'subject')},
      },
    ),
    migrations.RunPython(migrate_legacy_profiles, reverse_migrate_legacy_profiles),
  ]
