# Goodwill Christian College — College Management System

A Django 6.0 web portal for **Goodwill Christian College For Women** (GCCW). The system provides role-based access for admins, lecturers, and students, with a fully functional admin dashboard and UI shells for student and teacher portals.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6.0.5 |
| Database | MySQL (`college_management`) |
| Auth | Custom user model (`accounts.CustomUser`) |
| Templates | Django Templates + Bootstrap Icons |
| Email | Console backend (development) |

## Quick Start

```bash
# Create MySQL database: college_management
python manage.py migrate
python manage.py create_demo_users
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

### Demo Credentials (DEBUG mode)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Lecturer | `lecturer` | `lecturer123` |
| Student | `student` | `student123` |

Demo users are auto-created on migrate and on first login page load when `AUTO_CREATE_DEMO_USERS = True`.

## Documentation

Detailed implementation docs live in the [`docs/`](docs/) folder:

| Document | Description |
|----------|-------------|
| [Overview](docs/01-overview.md) | Project scope and implementation status |
| [Architecture](docs/02-architecture.md) | Directory layout, settings, URL routing |
| [Authentication](docs/03-authentication.md) | Login flow, roles, demo user provisioning |
| [Accounts App](docs/04-accounts-app.md) | Models, forms, services, Django admin |
| [Admin Dashboard](docs/05-admin-dashboard.md) | User, class, and messaging management |
| [Student Portal](docs/06-student-portal.md) | Student dashboard UI |
| [Teacher Portal](docs/07-teacher-portal.md) | Lecturer dashboard UI |
| [Frontend](docs/08-frontend.md) | Templates, CSS, JavaScript |
| [Planned Apps](docs/09-planned-apps.md) | Scaffolded apps not yet implemented |

## Implementation Summary

| Area | Status |
|------|--------|
| Landing page | Implemented |
| Role-based login | Implemented |
| Admin dashboard (custom UI) | Fully implemented |
| User & class management | Fully implemented |
| Admin messaging (email) | Fully implemented |
| Student dashboard | UI shell with static/demo data |
| Teacher dashboard | UI shell with static/demo data |
| Attendance | App scaffolded, no models/views |
| Assignments | App scaffolded, no models/views |
| Announcements | App scaffolded, no models/views |
| Fees | App scaffolded, no models/views |
