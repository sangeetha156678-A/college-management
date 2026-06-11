# Teacher Portal

## Entry Points

| URL | View | Notes |
|-----|------|-------|
| `/lecturer-dashboard/` | `accounts.views.teacher_dashboard` | Primary route (login redirect) |
| `/teacher-dashboard/` | `accounts.views.teacher_dashboard` | Alias |
| `/teacher/dashboard/` | Re-export via `teachers.views` | Alias |

`accounts.views.lecturer_dashboard` is a thin wrapper that calls `teacher_dashboard`.

## Access Control

- Requires `@login_required`
- Redirects to login if `request.user.role != 'teacher'`

## View Implementation

`accounts.views.teacher_dashboard` renders `templates/teacher_dashboard.html` with **static placeholder data**:

```python
{
    'greeting': 'Good Morning/Afternoon/Evening',  # Based on current hour
    'teacher_name': ...,                            # From full name, prefixed "Ms." if no title
    'teacher_short_name': ...,                      # First name extraction
    'stats': {
        'classes': 6,           # Hardcoded
        'students': 148,        # Hardcoded
        'attendance_pct': 87,   # Hardcoded
        'assignments': 12,      # Hardcoded
        'notes': 24,            # Hardcoded
    },
}
```

Default fallback name: `Ms. Priya Sharma` if user has no full name set.

> **Gap:** Stats do not reflect actual `CollegeClass` assignments or enrollment counts from the database.

## Template Structure

**Extends:** `teacher_base.html`

### Sidebar Navigation

| Menu Item | Status |
|-----------|--------|
| Dashboard | Active |
| My Classes | Placeholder |
| Attendance | Placeholder |
| Notes | Placeholder |
| Assignments | Placeholder |
| Students | Placeholder |
| Calendar | Placeholder |
| Messages | Placeholder |
| Reports | Placeholder |
| Settings | Placeholder |

### Dashboard Sections

1. **Overview stats** — Five stat cards (classes, students, attendance %, assignments, notes)
2. **Today's schedule** — Static timetable entries (not from database)
3. **Quick actions** — Links to placeholder actions (mark attendance, upload notes, create assignment)
4. **Recent activity** — Static activity feed
5. **Upcoming deadlines** — Static deadline list

All non-dashboard sidebar links and secondary sections use `href="#"` placeholders.

## Styling

- CSS: `static/css/teacher-dashboard.css`
- Shared theme: `static/css/theme.css`
- Reuses teacher-style stat cards also used by admin dashboard (`tch-stat-card`, `tch-stats`, etc.)

## Teachers App

The `teachers` Django app contains:

- `models.py` — empty
- `views.py` — re-exports `teacher_dashboard` from `accounts.views`
- `urls.py` — single route `dashboard/`
- `admin.py` — default (no registrations)
- `tests.py` — empty

Teacher profile data (`accounts.Teacher`) is managed through the `accounts` app.

## Future Integration Points

When implementing teacher features, connect to:

- `accounts.Teacher` profile for department/subject
- `accounts.ClassTeacher` for assigned classes
- `accounts.ClassEnrollment` for student rosters per class
- `attendance` app for marking and uploading attendance
- `assignments` app for creating and grading assignments
- `announcements` app for class-specific announcements
