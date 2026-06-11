# Authentication

## Login Flow

Entry point: `accounts.views.user_login` at `/accounts/login/`

### Role Tabs

The login page presents three tabs (Admin, Lecturers, Students). The active tab is determined by:

- `?role=admin|lecturer|student` query parameter (GET)
- `login_role` hidden form field (POST)

### Validation Steps

On POST, the view performs these checks in order:

1. Username and password are non-empty
2. `authenticate()` succeeds
3. User `is_active` is `True`
4. User's database `role` matches the selected tab's expected role

If any check fails, the login form re-renders with an error message. Invalid role mismatch shows a generic "Invalid credentials" message (does not reveal which field failed).

### Post-Login Redirect

Defined in `LOGIN_ROLE_MAP` (`accounts/views.py`):

| Tab | DB role | Redirect URL name | Path |
|-----|---------|-------------------|------|
| `admin` | `admin` | `admin_dashboard` | `/admin-dashboard/` |
| `lecturer` | `teacher` | `lecturer_dashboard` | `/lecturer-dashboard/` |
| `student` | `student` | `student_dashboard` | `/student-dashboard/` |

The selected tab is stored in `request.session['login_role']`.

### Logout

`accounts.views.user_logout` calls `logout()` and redirects to the login page.

## Access Control

### `@login_required`

Student and teacher dashboard views require authentication (`login_url='/accounts/login/'`).

### `@admin_required`

Custom decorator in `accounts/decorators.py`:

- Redirects unauthenticated users to `login`
- Redirects authenticated non-admin users to `login`
- Does not use Django's `user_passes_test` — checks `request.user.role != 'admin'`

All views in `accounts/admin_views.py` use both `@login_required` and `@admin_required`.

## Custom User Model

`accounts.CustomUser` extends `AbstractUser` with:

```python
ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)
role = models.CharField(max_length=20, choices=ROLE_CHOICES)
```

Properties:

- `display_name` — full name if set, otherwise username

## Demo User Provisioning

### Configuration

`AUTO_CREATE_DEMO_USERS = True` in settings enables automatic demo account creation.

### Demo Accounts

Defined in `accounts/demo_users.py`:

| Username | Password | Role | Email | Staff | Superuser |
|----------|----------|------|-------|-------|-----------|
| `admin` | `admin123` | admin | admin@goodwillcollege.edu | Yes | Yes |
| `lecturer` | `lecturer123` | teacher | lecturer@goodwillcollege.edu | Yes | No |
| `student` | `student123` | student | student@goodwillcollege.edu | No | No |

Teacher and student demo users also get `Teacher` / `Student` profile records.

### Trigger Points

1. **Post-migrate signal** — `AccountsConfig.ready()` → `ensure_demo_users_on_migrate`
2. **Login page load** — `ensure_demo_users_if_needed()` (lazy, once per process)
3. **Management command** — `python manage.py create_demo_users`

### DEBUG Credentials Display

When `DEBUG = True`, demo credentials are passed to the login template as `demo_credentials` for developer convenience.

## User Account Creation (Admin)

Admins create accounts via the admin dashboard, not self-registration. See [Accounts App — User Service](04-accounts-app.md#user-service).

New accounts receive:

- Auto-generated username (slugified from name, with numeric suffix if needed)
- Random temporary password (`secrets.token_urlsafe(8)`)
- Welcome email with credentials

## Security Notes (Development)

Current settings are **not production-ready**:

- `DEBUG = True`
- Hardcoded `SECRET_KEY` in settings
- `ALLOWED_HOSTS = []`
- Database credentials in plain text
- Console email backend

These should be externalized via environment variables before deployment.
