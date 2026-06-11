# Admin Dashboard

The custom admin dashboard lives at `/admin-dashboard/` and is implemented in `accounts/admin_views.py` with templates under `templates/admin/`.

All views require login and the `admin` role (`@admin_required`).

## Navigation

Sidebar (`templates/admin/partials/sidebar.html`):

| Nav item | URL name | Path |
|----------|----------|------|
| Dashboard | `admin_dashboard` | `/admin-dashboard/` |
| User Management | `admin_users` | `/admin-dashboard/users/` |
| Classes | `admin_classes` | `/admin-dashboard/classes/` |
| Messages | `admin_messages_compose` | `/admin-dashboard/messages/` |
| Message History | `admin_messages_history` | `/admin-dashboard/messages/history/` |

## Dashboard (`admin_dashboard`)

**Template:** `templates/admin/dashboard.html`

Displays:

- **Stats cards** — teacher count, student count, class count, active/inactive accounts
- **Quick actions** — links to create account, create class, send message
- **Recent activity** — last 10 `ActivityLog` entries
- **Class stats** — up to 8 classes with enrollment/teacher counts
- **Recent messages** — last 5 `AdminMessage` records

Context includes time-based greeting (`Good Morning/Afternoon/Evening`) and admin name.

## User Management

### List Users (`admin_users`)

**Template:** `templates/admin/users.html`  
**URL:** `/admin-dashboard/users/`

Features:

- Lists teachers and students (excludes admins)
- Filter by search query (`q`), role, and active/inactive status via `UserFilterForm`
- Pagination (15 per page)
- Prefetches `teacher_profile` and `student_profile`

### Create User (`admin_user_create`)

**Template:** `templates/admin/user_form.html`  
**URL:** `/admin-dashboard/users/create/`

- Uses `CreateUserForm`
- Calls `create_user_account()` service
- On success: flash message + redirect to user list
- On duplicate email: error message

### Toggle User Status (`admin_user_toggle`)

**URL:** `/admin-dashboard/users/<user_id>/toggle/`  
**Method:** POST only

Flips `is_active` for a single teacher/student. Logs status change.

### Bulk Actions (`admin_users_bulk`)

**URL:** `/admin-dashboard/users/bulk/`  
**Method:** POST only

Actions: `activate` or `deactivate` for selected `user_ids`.

## Class Management

### List Classes (`admin_classes`)

**Template:** `templates/admin/classes.html`  
**URL:** `/admin-dashboard/classes/`

Lists all `CollegeClass` records with annotated `enrolled_count` and `assigned_teachers`.

### Create Class (`admin_class_create`)

**Template:** `templates/admin/class_form.html`  
**URL:** `/admin-dashboard/classes/create/`

- Uses `CollegeClassForm` (name, grade, section, subject)
- Logs `ACTION_CLASS_CREATED`
- Redirects to class detail on success

### Class Detail (`admin_class_detail`)

**Template:** `templates/admin/class_detail.html`  
**URL:** `/admin-dashboard/classes/<class_id>/`

Shows:

- Class metadata
- Assigned teachers and enrolled students
- Available teachers/students not yet in this class
- Other classes (for teacher reassignment)

### Assign Teachers (`admin_class_assign_teachers`)

**URL:** `/admin-dashboard/classes/<class_id>/assign-teachers/`  
**Method:** POST

Accepts `teacher_ids` list. Creates `ClassTeacher` records (idempotent via `get_or_create`). Logs new assignments.

### Remove Teacher (`admin_class_remove_teacher`)

**URL:** `/admin-dashboard/classes/<class_id>/remove-teacher/<teacher_id>/`  
**Method:** POST

Deletes the `ClassTeacher` join record.

### Enroll Students (`admin_class_enroll_students`)

**URL:** `/admin-dashboard/classes/<class_id>/enroll-students/`  
**Method:** POST

Accepts `student_ids` list. Creates `ClassEnrollment` records. Logs new enrollments.

### Remove Student (`admin_class_remove_student`)

**URL:** `/admin-dashboard/classes/<class_id>/remove-student/<student_id>/`  
**Method:** POST

Deletes the `ClassEnrollment` join record.

### Reassign Teacher (`admin_class_reassign_teacher`)

**URL:** `/admin-dashboard/classes/<class_id>/reassign-teacher/<teacher_id>/`  
**Method:** POST

Moves a teacher from the current class to `target_class_id` (from POST data).

## Messaging

### Compose Message (`admin_messages_compose`)

**Template:** `templates/admin/messages_compose.html`  
**URL:** `/admin-dashboard/messages/`

Flow:

1. Admin fills `ComposeMessageForm` (subject, body, target type, recipients)
2. `_resolve_message_recipients()` builds recipient list based on target type
3. Filters to users with valid email addresses
4. Creates `AdminMessage` and `AdminMessageRecipient` records
5. Sends email to each recipient via `send_admin_message_email()`
6. Logs `ACTION_MESSAGE_SENT`
7. Redirects to message history

**Recipient resolution logic:**

| Target type | Recipients |
|-------------|------------|
| Individual | Selected user |
| All Teachers | Active users with `role='teacher'` |
| All Students | Active users with `role='student'` |
| All Users | Active teachers + students |
| By Class | Active teachers and students enrolled in the class |
| Custom | Selected users from multiselect |

### Message History (`admin_messages_history`)

**Template:** `templates/admin/messages_history.html`  
**URL:** `/admin-dashboard/messages/history/`

Paginated list (20 per page) of all `AdminMessage` records with sender and target class info.

## Flash Messages

Admin templates include `templates/admin/partials/flash_messages.html` for Django messages framework feedback (success, warning, error).
