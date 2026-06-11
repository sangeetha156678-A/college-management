from django.db import migrations, models


def backfill_roll_numbers(apps, schema_editor):
    Student = apps.get_model('accounts', 'Student')
    for student in Student.objects.select_related('user').iterator():
        if not student.roll_number:
            student.roll_number = student.user.username
            student.save(update_fields=['roll_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_teacher_phone_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='roll_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.RunPython(backfill_roll_numbers, migrations.RunPython.noop),
    ]
