from django.db import migrations


DEPARTMENTS = [
  {
    'code': 'BCA',
    'name': 'Bachelor of Computer Applications',
    'subjects': {
      (1, 1): [
        ('BCA101', 'Programming Fundamentals', 4),
        ('BCA102', 'Mathematics', 4),
        ('BCA103', 'English', 3),
      ],
      (1, 2): [
        ('BCA104', 'Data Structures', 4),
        ('BCA105', 'Digital Logic', 3),
      ],
      (2, 1): [
        ('BCA201', 'Database Systems', 4),
        ('BCA202', 'Operating Systems', 4),
      ],
      (2, 2): [
        ('BCA203', 'Computer Networks', 4),
        ('BCA204', 'Software Engineering', 3),
      ],
      (3, 1): [
        ('BCA301', 'Machine Learning', 4),
        ('BCA302', 'Web Technologies', 4),
      ],
      (3, 2): [
        ('BCA303', 'Cloud Computing', 4),
        ('BCA304', 'Project Work', 6),
      ],
    },
  },
  {
    'code': 'BCOM',
    'name': 'Bachelor of Commerce',
    'subjects': {
      (1, 1): [
        ('BCOM101', 'Financial Accounting', 4),
        ('BCOM102', 'Business Economics', 4),
      ],
      (1, 2): [
        ('BCOM103', 'Business Mathematics', 3),
        ('BCOM104', 'Corporate Accounting', 4),
      ],
      (2, 1): [
        ('BCOM201', 'Cost Accounting', 4),
        ('BCOM202', 'Business Law', 3),
      ],
      (2, 2): [
        ('BCOM203', 'Income Tax', 4),
        ('BCOM204', 'Banking', 3),
      ],
      (3, 1): [
        ('BCOM301', 'Auditing', 4),
        ('BCOM302', 'Financial Management', 4),
      ],
      (3, 2): [
        ('BCOM303', 'GST', 3),
        ('BCOM304', 'Project Work', 6),
      ],
    },
  },
  {
    'code': 'BBA',
    'name': 'Bachelor of Business Administration',
    'subjects': {
      (1, 1): [
        ('BBA101', 'Principles of Management', 4),
        ('BBA102', 'Business Communication', 3),
      ],
      (1, 2): [
        ('BBA103', 'Microeconomics', 4),
        ('BBA104', 'Organizational Behavior', 3),
      ],
      (2, 1): [
        ('BBA201', 'Marketing Management', 4),
        ('BBA202', 'Human Resource Management', 4),
      ],
      (2, 2): [
        ('BBA203', 'Financial Management', 4),
        ('BBA204', 'Operations Management', 3),
      ],
      (3, 1): [
        ('BBA301', 'Strategic Management', 4),
        ('BBA302', 'Entrepreneurship', 3),
      ],
      (3, 2): [
        ('BBA303', 'Business Analytics', 4),
        ('BBA304', 'Project Work', 6),
      ],
    },
  },
]


def seed_academic_data(apps, schema_editor):
  Department = apps.get_model('academics', 'Department')
  Year = apps.get_model('academics', 'Year')
  Semester = apps.get_model('academics', 'Semester')
  Subject = apps.get_model('academics', 'Subject')

  for dept_data in DEPARTMENTS:
    department, _ = Department.objects.get_or_create(
      code=dept_data['code'],
      defaults={
        'name': dept_data['name'],
        'duration_years': 3,
        'is_active': True,
      },
    )

    for year_num in range(1, 4):
      year, _ = Year.objects.get_or_create(
        department=department,
        number=year_num,
      )

      for sem_num in (1, 2):
        semester, _ = Semester.objects.get_or_create(
          year=year,
          number=sem_num,
        )

        for code, name, credits in dept_data['subjects'].get((year_num, sem_num), []):
          Subject.objects.get_or_create(
            department=department,
            code=code,
            defaults={
              'semester': semester,
              'name': name,
              'credits': credits,
            },
          )


def unseed_academic_data(apps, schema_editor):
  Department = apps.get_model('academics', 'Department')
  Department.objects.filter(code__in=['BCA', 'BCOM', 'BBA']).delete()


class Migration(migrations.Migration):

  dependencies = [
    ('academics', '0001_initial'),
  ]

  operations = [
    migrations.RunPython(seed_academic_data, unseed_academic_data),
  ]
