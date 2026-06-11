# Student Portal

## Entry Points

| URL | View | Notes |
|-----|------|-------|
| `/student-dashboard/` | `accounts.views.student_dashboard` | Primary route |
| `/student/dashboard/` | Re-export via `students.views` | Alias |

Both resolve to the same view and template.

## Access Control

- Requires `@login_required`
- Redirects to login if `request.user.role != 'student'`

## View Implementation

`accounts.views.student_dashboard` renders `templates/student_dashboard.html` with **hardcoded context** — it does not query the `Student` profile or database:

```python
{
    'student_display_name': display_name,      # From user full name or username
    'registration_no': '25BBCAI008',           # Hardcoded (not from DB)
    'semester': 'Sem II',                      # Hardcoded
    'course': 'BCA (AI & ML)',                 # Hardcoded
    'section': 'A',                            # Hardcoded
    'current_datetime': ...,                    # Live timestamp
    'metrics': {
        'announcements': 0,
        'attendance': '-',
        'assessment': 0,
        'tasks': 4,
        'placement': 0,
    },
}
```

> **Gap:** The view does not use `request.user.student_profile` for course, semester, or enrollment data.

## Template Structure

**Extends:** `dashboard_base.html`

### Sidebar Navigation

The sidebar (`erp-sidebar`) includes links for:

| Menu Item | Status |
|-----------|--------|
| Dashboard | Active (links to `student_dashboard`) |
| Profile | Placeholder (`href="#"`) |
| Syllabus | Placeholder |
| Calendar | Placeholder |
| Time Table | Placeholder |
| Attendance | Placeholder |
| Assessment | Placeholder |
| Assignments | Placeholder |
| Fees | Placeholder |
| Announcements | Placeholder |
| Placement | Placeholder |
| Hostel | Placeholder |
| Library | Placeholder |
| Leave | Placeholder |
| Messages | Placeholder |
| Settings | Placeholder |

### Profile Card

Displays student photo (`default-avatar.svg`), registration number, semester, course, and section from template context.

### Dashboard Metrics

Five metric cards showing announcements, attendance, assessment, tasks, and placement counts from the `metrics` context dict.

### Main Content Area

Additional sections in the template (not fully wired to backend) include quick links and announcement/task placeholders.

## Styling

- CSS: `static/css/student-dashboard.css`
- Shared theme: `static/css/theme.css`
- Icons: Bootstrap Icons (loaded in base template)

## Students App

The `students` Django app contains:

- `models.py` — empty
- `views.py` — re-exports `student_dashboard` from `accounts.views`
- `urls.py` — single route `dashboard/`
- `admin.py` — default (no registrations)
- `tests.py` — empty

No student-specific business logic exists outside `accounts`.

## Future Integration Points

When implementing student features, these areas should connect to:

- `accounts.Student` profile for course/semester
- `accounts.ClassEnrollment` for section and class membership
- `announcements` app for bulletin posts
- `attendance` app for attendance percentages
- `assignments` app for tasks and assessments
- `fees` app for payment status
