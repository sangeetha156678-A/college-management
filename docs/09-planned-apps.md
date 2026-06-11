# Planned Apps (Not Yet Implemented)

Four Django apps are registered in `INSTALLED_APPS` and scaffolded with default Django app structure, but contain **no models, views, URLs, or admin registrations**. They represent planned features referenced on the landing page and in dashboard navigation placeholders.

## App Status Summary

| App | Models | Views | URLs | Admin | Tests |
|-----|--------|-------|------|-------|-------|
| `attendance` | Empty | Empty | None | Default | Empty |
| `assignments` | Empty | Empty | None | Default | Empty |
| `announcements` | Empty | Empty | None | Default | Empty |
| `fees` | Empty | Empty | None | Default | Empty |
| `students` | Empty | Re-export dashboard | `/student/dashboard/` | Default | Empty |
| `teachers` | Empty | Re-export dashboard | `/teacher/dashboard/` | Default | Empty |

## attendance

**Planned purpose:** Track student attendance per class, per session.

**Referenced in UI:**

- Landing page: "Syllabus & Attendance" feature card
- Student sidebar: Attendance menu item
- Teacher sidebar: Attendance menu item
- Teacher dashboard: Attendance stat card, "Upload" action
- Student dashboard: Attendance metric (currently shows `-`)

**Likely data model (not implemented):**

- Attendance session (class, date, period)
- Attendance record (student, status: present/absent/late)

## assignments

**Planned purpose:** Faculty creates assignments; students submit and track deadlines.

**Referenced in UI:**

- Landing page: "Assignments & Assessment" feature card
- Student sidebar: Assessment, Assignments menu items
- Teacher sidebar: Assignments menu item
- Teacher dashboard: Assignments stat card, "Create New" action
- Student dashboard: Assessment and tasks metrics

**Likely data model (not implemented):**

- Assignment (class, title, description, due date, created by teacher)
- Submission (student, assignment, file/text, submitted at, grade)

## announcements

**Planned purpose:** Campus-wide and class-specific bulletin board.

**Referenced in UI:**

- Landing page: "Announcements & Bulletin" feature card
- Student sidebar: Announcements menu item
- Student dashboard: Announcements metric (currently `0`)

**Note:** Admin messaging (`AdminMessage`) exists in `accounts` for **email broadcasts**, but there is no in-portal announcement feed for students/teachers.

**Likely data model (not implemented):**

- Announcement (title, body, author, target audience, published at, pinned)

## fees

**Planned purpose:** Fee structure, payment tracking, and receipt generation.

**Referenced in UI:**

- Landing page: "Fees & Payments" feature card
- Student sidebar: Fees menu item

**Likely data model (not implemented):**

- Fee structure (course, semester, amount, due date)
- Payment record (student, amount, date, receipt number, status)

## students & teachers Apps

These apps exist primarily as **URL namespace aliases**:

- `students/urls.py` → `/student/dashboard/` → `student_dashboard`
- `teachers/urls.py` → `/teacher/dashboard/` → `teacher_dashboard`

All profile and class data lives in the `accounts` app. When building student/teacher-specific features, either:

1. Implement models/views in these dedicated apps and import from `accounts` for user relationships, or
2. Continue centralizing in `accounts` and use these apps only for URL organization

## Testing

All test files (`tests.py`) across every app are empty placeholders:

```python
from django.test import TestCase
# Create your tests here.
```

No automated test coverage exists yet.

## Dependencies File

No `requirements.txt` or `pyproject.toml` was found in the project root. Dependencies are implied by Django 6.0.5 and MySQL client usage.

## Recommended Implementation Order

Based on UI prominence and admin infrastructure already in place:

1. **Wire student/teacher dashboards to real data** — Use existing `Student`, `Teacher`, `CollegeClass` models
2. **announcements** — In-portal feed complements existing admin email messaging
3. **attendance** — High visibility in both portals
4. **assignments** — Depends on class enrollment (already implemented)
5. **fees** — Independent module, can be added last
