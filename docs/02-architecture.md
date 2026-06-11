# Architecture

## Directory Structure

```
college-management/
├── config/                 # Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── context_processors.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/               # Core app: users, classes, admin dashboard, auth
│   ├── models.py
│   ├── views.py            # Login, student/teacher dashboards
│   ├── admin_views.py      # Custom admin dashboard views
│   ├── admin_urls.py
│   ├── urls.py
│   ├── forms.py
│   ├── decorators.py
│   ├── demo_users.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── email_service.py
│   └── management/commands/create_demo_users.py
├── students/               # URL alias for student dashboard (no models)
├── teachers/               # URL alias for teacher dashboard (no models)
├── attendance/             # Placeholder app
├── assignments/            # Placeholder app
├── announcements/          # Placeholder app
├── fees/                   # Placeholder app
├── templates/              # Shared and role-specific HTML templates
├── static/                 # CSS, JS, images
└── manage.py
```

## Installed Apps

From `config/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'students',
    'teachers',
    'attendance',
    'assignments',
    'announcements',
    'fees',
]
```

## Settings Highlights

| Setting | Value | Purpose |
|---------|-------|---------|
| `AUTH_USER_MODEL` | `accounts.CustomUser` | Custom user with role field |
| `LOGIN_URL` | `/accounts/login/` | Unauthenticated redirect |
| `LOGIN_REDIRECT_URL` | `/student-dashboard/` | Default post-login (overridden per role) |
| `AUTO_CREATE_DEMO_USERS` | `True` | Provision demo accounts on migrate/login |
| `DATABASES` | MySQL `college_management` | Local MySQL on port 3306 |
| `STATICFILES_DIRS` | `static/` | Project-level static assets |
| `MEDIA_ROOT` | `media/` | User uploads (configured, not yet used) |
| `EMAIL_BACKEND` | Console backend | Prints emails to terminal in dev |

## URL Routing

Root URL configuration (`config/urls.py`):

| URL | Handler | Name |
|-----|---------|------|
| `/` | Landing page (`index.html`) | `home` |
| `/admin/` | Django admin site | — |
| `/accounts/login/` | Role-based login | `login` |
| `/accounts/logout/` | Logout | `logout` |
| `/admin-dashboard/` | Custom admin dashboard (included) | `admin_dashboard` |
| `/student-dashboard/` | Student dashboard | `student_dashboard` |
| `/lecturer-dashboard/` | Teacher dashboard | `lecturer_dashboard` |
| `/teacher-dashboard/` | Teacher dashboard (alias) | `teacher_dashboard` |
| `/student/dashboard/` | Student dashboard (alias via `students.urls`) | `student_dashboard` |
| `/teacher/dashboard/` | Teacher dashboard (alias via `teachers.urls`) | `teacher_dashboard` |

Admin dashboard sub-routes are defined in `accounts/admin_urls.py` — see [Admin Dashboard](05-admin-dashboard.md).

## Template Inheritance

```
base.html                    # Landing page layout
login_base.html              # Login page layout
dashboard_base.html          # Student dashboard shell
teacher_base.html            # Teacher dashboard shell
admin_base.html              # Admin dashboard shell
```

Context processor `config.context_processors.college_context` injects `admission_year` (`2026-2027`) into all templates.

## Middleware Stack

Standard Django middleware: Security, Sessions, Common, CSRF, Authentication, Messages, Clickjacking.

## Database

- Engine: `django.db.backends.mysql`
- Name: `college_management`
- User/Password: `root` / `root` (development defaults)
- Host: `localhost:3306`

All migrations currently exist only under `accounts/migrations/` (4 migration files).

## App Startup Hook

`accounts.apps.AccountsConfig.ready()` connects a `post_migrate` signal that calls `ensure_demo_users_on_migrate`, creating demo users after every `migrate` when `AUTO_CREATE_DEMO_USERS` is enabled.
