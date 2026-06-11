import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

  initial = True

  dependencies = []

  operations = [
    migrations.CreateModel(
      name='Department',
      fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('code', models.CharField(max_length=20, unique=True)),
        ('name', models.CharField(max_length=100)),
        ('duration_years', models.PositiveSmallIntegerField(default=3)),
        ('is_active', models.BooleanField(default=True)),
      ],
      options={
        'ordering': ['name'],
      },
    ),
    migrations.CreateModel(
      name='Year',
      fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('number', models.PositiveSmallIntegerField()),
        ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='years', to='academics.department')),
      ],
      options={
        'ordering': ['department', 'number'],
        'unique_together': {('department', 'number')},
      },
    ),
    migrations.CreateModel(
      name='Semester',
      fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('number', models.PositiveSmallIntegerField(choices=[(1, 'Semester 1'), (2, 'Semester 2')])),
        ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='academics.year')),
      ],
      options={
        'ordering': ['year', 'number'],
        'unique_together': {('year', 'number')},
      },
    ),
    migrations.CreateModel(
      name='Subject',
      fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('code', models.CharField(max_length=20)),
        ('name', models.CharField(max_length=100)),
        ('credits', models.PositiveSmallIntegerField(blank=True, null=True)),
        ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='academics.department')),
        ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='academics.semester')),
      ],
      options={
        'ordering': ['department', 'semester', 'name'],
        'unique_together': {('department', 'code')},
      },
    ),
  ]
