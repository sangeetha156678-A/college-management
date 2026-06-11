from django.db import migrations


BCA_SUBJECTS = {
    (1, 1): [
        ('BCA101', 'Fundamentals of computer', 4),
        ('BCA102', 'Mathematical foundation', 4),
        ('BCA103', 'C-programming', 4),
        ('BCA104', 'Office Management', 3),
        ('BCA105', 'Environmental Studies', 3),
        ('BCA106', 'English C-programming Practical', 3),
        ('BCA107', 'Language', 3),
    ],
    (1, 2): [
        ('BCA108', 'People Management', 3),
        ('BCA109', 'Discrete Mathematical Structures', 4),
        ('BCA110', 'Data Structure Using C', 4),
        ('BCA111', 'Object Oriented concepts Using Java', 4),
        ('BCA112', 'Language', 3),
        ('BCA113', 'English', 3),
    ],
    (2, 1): [
        ('BCA201', 'Rural Marketing', 3),
        ('BCA202', 'India and Indian constitution', 3),
        ('BCA203', 'Database Management System', 4),
        ('BCA204', 'Computer communication networks', 4),
        ('BCA205', 'C# and Dot net Framework', 4),
        ('BCA206', 'English', 3),
        ('BCA207', 'Language', 3),
    ],
    (2, 2): [
        ('BCA208', 'Python Programming', 4),
        ('BCA209', 'Computer Multimedia Animation', 4),
        ('BCA210', 'Open source tool', 3),
        ('BCA211', 'English', 3),
        ('BCA212', 'Business leadership Skills', 3),
        ('BCA213', 'Language', 3),
        ('BCA214', 'Operating system concepts', 4),
    ],
    (3, 1): [
        ('BCA301', 'Design and Analysis of Algorithm', 4),
        ('BCA302', 'Software Engineering', 4),
        ('BCA303', 'R-programming', 4),
        ('BCA304', 'Cloud computing', 4),
        ('BCA305', 'Cyber Security', 4),
        ('BCA306', 'Digital Marketing', 3),
    ],
    (3, 2): [
        ('BCA307', 'Php & Mysql', 4),
        ('BCA308', 'Mobile Application development', 4),
        ('BCA309', 'Artificial Intelligent', 4),
        ('BCA310', 'Web content development', 4),
    ],
}


def update_bca_curriculum(apps, schema_editor):
    Department = apps.get_model('academics', 'Department')
    Year = apps.get_model('academics', 'Year')
    Semester = apps.get_model('academics', 'Semester')
    Subject = apps.get_model('academics', 'Subject')

    try:
        department = Department.objects.get(code='BCA')
    except Department.DoesNotExist:
        return

    Subject.objects.filter(department=department).delete()

    for year_num in range(1, 4):
        year = Year.objects.get(department=department, number=year_num)
        for sem_num in (1, 2):
            semester = Semester.objects.get(year=year, number=sem_num)
            for code, name, credits in BCA_SUBJECTS.get((year_num, sem_num), []):
                Subject.objects.create(
                    department=department,
                    semester=semester,
                    code=code,
                    name=name,
                    credits=credits,
                )


def revert_bca_curriculum(apps, schema_editor):
    Department = apps.get_model('academics', 'Department')
    Subject = apps.get_model('academics', 'Subject')

    try:
        department = Department.objects.get(code='BCA')
    except Department.DoesNotExist:
        return

    Subject.objects.filter(department=department).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_seed_academic_data'),
    ]

    operations = [
        migrations.RunPython(update_bca_curriculum, revert_bca_curriculum),
    ]
