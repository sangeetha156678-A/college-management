from django.db import transaction

from assignments.models import StudyMaterial


def create_study_material(*, teacher, subject, title, description, topic, uploaded_file):
    with transaction.atomic():
        material = StudyMaterial.objects.create(
            subject=subject,
            uploaded_by=teacher,
            title=title.strip(),
            description=description.strip(),
            topic=topic.strip(),
            file=uploaded_file,
        )
    return material


def delete_study_material(material):
    with transaction.atomic():
        if material.file:
            material.file.delete(save=False)
        material.delete()
