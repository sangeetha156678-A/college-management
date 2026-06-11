import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ('accounts', '0005_academic_hierarchy_fks'),
  ]

  operations = [
    migrations.RemoveField(
      model_name='student',
      name='course',
    ),
    migrations.RemoveField(
      model_name='student',
      name='semester',
    ),
    migrations.RemoveField(
      model_name='teacher',
      name='subject',
    ),
    migrations.AlterField(
      model_name='student',
      name='year',
      field=models.ForeignKey(
        on_delete=django.db.models.deletion.PROTECT,
        related_name='students',
        to='academics.year',
      ),
    ),
    migrations.AlterField(
      model_name='student',
      name='current_semester',
      field=models.ForeignKey(
        on_delete=django.db.models.deletion.PROTECT,
        related_name='students',
        to='academics.semester',
      ),
    ),
    migrations.RenameField(
      model_name='student',
      old_name='current_semester',
      new_name='semester',
    ),
  ]
