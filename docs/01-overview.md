# Project Overview

## Purpose

This project is a college management portal for **Goodwill Christian College For Women** (GCCW), affiliated to Bengaluru North University. It is designed to centralize academic operations — user management, class organization, messaging, attendance, assignments, fees, and announcements — behind a single role-based web interface.

## Current State (June 2026)

The codebase is in an **early-to-mid development** phase. Core infrastructure and the **admin experience are production-ready in structure**, while student/teacher portals are **visual prototypes** and several Django apps exist only as placeholders.

### Fully Implemented

- Public landing page with course listings and feature highlights
- Multi-role login (Admin, Lecturer, Student) with role validation
- Custom admin dashboard at `/admin-dashboard/` (separate from Django's `/admin/`)
- User CRUD: create teachers/students, activate/deactivate, bulk actions
- Class management: create classes, assign teachers, enroll students, reassign teachers
- Admin messaging: compose and send emails to individuals, roles, classes, or custom groups
- Activity logging for admin actions
- Demo user auto-provisioning for local development
- Django admin integration for all `accounts` models

### Partially Implemented (UI Only)

- **Student dashboard** — Full sidebar navigation and metric cards, but data is hardcoded in the view (not pulled from the database)
- **Teacher dashboard** — Full layout with stats, schedule, and quick actions, but stats are static placeholders

### Not Yet Implemented

These Django apps are registered in `INSTALLED_APPS` but contain empty `models.py` and `views.py`:

- `attendance`
- `assignments`
- `announcements`
- `fees`

The `students` and `teachers` apps re-export dashboard views from `accounts` and have no models of their own.

## User Roles

| Role | DB value | Login tab | Redirect after login |
|------|----------|-----------|----------------------|
| Admin | `admin` | Admin | `/admin-dashboard/` |
| Lecturer | `teacher` | Lecturers | `/lecturer-dashboard/` |
| Student | `student` | Students | `/student-dashboard/` |

## Key Design Decisions

1. **Single source of truth for profiles** — `Student` and `Teacher` profile models live in the `accounts` app, not in the `students`/`teachers` apps.
2. **Custom admin UI** — Day-to-day admin work uses a branded dashboard (`admin_views.py`), while Django's built-in admin (`/admin/`) is available for superuser data access.
3. **Email via Django mail** — Welcome emails and admin messages use `django.core.mail.send_mail` with a console backend in development.
4. **MySQL** — Production-oriented database choice configured in `config/settings.py`.
