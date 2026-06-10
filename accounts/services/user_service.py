import secrets



from django.contrib.auth import get_user_model

from django.db import transaction

from django.utils.text import slugify



from accounts.models import ActivityLog, Student, Teacher

from accounts.services.email_service import send_welcome_email



User = get_user_model()





def _generate_username(first_name, last_name, email):

    base = slugify(f'{first_name}-{last_name}') or slugify(email.split('@')[0]) or 'user'

    base = base[:20]

    candidate = base

    suffix = 1

    while User.objects.filter(username=candidate).exists():

        candidate = f'{base}{suffix}'

        suffix += 1

    return candidate





def _generate_temp_password():

    return secrets.token_urlsafe(8)





def create_user_account(

    *,

    first_name,

    last_name,

    email,

    role,

    subject='',

    department='',

    course='',

    semester='',

    performed_by=None,

):

    email = email.strip().lower()

    if User.objects.filter(email=email).exists():

        raise ValueError('A user with this email already exists.')



    username = _generate_username(first_name, last_name, email)

    temp_password = _generate_temp_password()



    with transaction.atomic():

        user = User.objects.create_user(

            username=username,

            email=email,

            password=temp_password,

            first_name=first_name.strip(),

            last_name=last_name.strip(),

            role=role,

            is_active=True,

        )



        if role == 'teacher':

            Teacher.objects.create(

                user=user,

                subject=subject.strip(),

                department=department.strip(),

            )

        elif role == 'student':

            Student.objects.create(

                user=user,

                course=course.strip(),

                semester=semester.strip(),

            )



        ActivityLog.objects.create(

            performed_by=performed_by,

            action=ActivityLog.ACTION_USER_CREATED,

            description=f'Created {role} account for {user.display_name} ({email})',

        )



    send_welcome_email(user, temp_password)

    return user, temp_password





def log_user_status_change(user, is_active, performed_by):

    action = (

        ActivityLog.ACTION_USER_ACTIVATED

        if is_active

        else ActivityLog.ACTION_USER_DEACTIVATED

    )

    status = 'activated' if is_active else 'deactivated'

    ActivityLog.objects.create(

        performed_by=performed_by,

        action=action,

        description=f'{status.title()} account for {user.display_name}',

    )

