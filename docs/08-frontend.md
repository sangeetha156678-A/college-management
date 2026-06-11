# Frontend

## Template Files

### Public Pages

| Template | Extends | Purpose |
|----------|---------|---------|
| `index.html` | `base.html` | Landing page with hero, features, courses |
| `login.html` | `login_base.html` | Role-tabbed login form |

### Dashboard Shells

| Template | Used By |
|----------|---------|
| `dashboard_base.html` | Student dashboard |
| `teacher_base.html` | Teacher dashboard |
| `admin_base.html` | Admin dashboard |

### Admin Templates

| Template | Purpose |
|----------|---------|
| `admin/dashboard.html` | Admin overview |
| `admin/users.html` | User list with filters |
| `admin/user_form.html` | Create user form |
| `admin/classes.html` | Class list |
| `admin/class_form.html` | Create class form |
| `admin/class_detail.html` | Class detail with assign/enroll UI |
| `admin/messages_compose.html` | Message composition |
| `admin/messages_history.html` | Sent message history |
| `admin/partials/sidebar.html` | Admin navigation |
| `admin/partials/flash_messages.html` | Django messages display |

### Role Dashboards

| Template | Purpose |
|----------|---------|
| `student_dashboard.html` | Student portal home |
| `teacher_dashboard.html` | Teacher portal home |

## Static Assets

### CSS

| File | Scope |
|------|-------|
| `static/css/theme.css` | Global design tokens, shared components |
| `static/css/login-portal.css` | Login page styling |
| `static/css/student-dashboard.css` | Student ERP sidebar and dashboard |
| `static/css/teacher-dashboard.css` | Teacher/admin shared dashboard components |
| `static/css/admin-dashboard.css` | Admin-specific overrides |

Admin dashboard reuses teacher dashboard CSS classes (`tch-sidebar`, `tch-stat-card`, `tch-actions`, etc.) with admin-specific additions in `admin-dashboard.css`.

### JavaScript

| File | Purpose |
|------|---------|
| `static/js/landing.js` | Landing page interactions (smooth scroll, mobile nav) |
| `static/js/login-portal.js` | Login form enhancements |
| `static/js/admin-dashboard.js` | Admin dashboard UI (target type toggling in message compose, bulk user selection) |

### Images

| File | Usage |
|------|-------|
| `static/img/goodwill-logo.svg` | College logo on login and headers |
| `static/img/default-avatar.svg` | Default profile photo on student dashboard |

### Standalone HTML

| File | Notes |
|------|-------|
| `static/student-dashboard-standalone.html` | Static prototype (not served by Django views) |

## Design System

### Icon Library

Bootstrap Icons (`bi bi-*`) loaded via CDN in base templates.

### Color-Coded Stat Cards

Teacher and admin dashboards use colored stat card variants:

- `blue` — classes / teachers
- `purple` — students
- `green` — attendance / classes
- `orange` — assignments / active accounts
- `pink` — notes / inactive accounts

### Responsive Layout

- Sidebar + main content layout for all dashboards
- Sidebar toggle via `id="erp-sidebar"` / `id="tch-sidebar"`
- Login page uses tabbed role selector

## Landing Page Features

`templates/index.html` sections:

1. **Hero** — College name, tagline, login CTA
2. **Features grid** — Six portal feature cards (all link to login)
3. **Courses** — BCA, B.Com, BBA program cards
4. **About** — College description
5. **Contact** — Address and contact info
6. **Footer** — Copyright and links

Context: `admission_year` from `college_context` processor (`2026-2027`).

## Login Page Features

- Three role tabs (Admin, Lecturers, Students)
- Hidden `login_role` field synced with active tab
- Error message display
- Demo credentials panel (visible only when `DEBUG = True`)
- "Back To Home" link

## Form Styling

Admin forms use CSS classes:

- `adm-input` — text inputs and selects
- `adm-textarea` — message body
- `adm-multiselect` — custom recipient picker
- `adm-search` — user search field

## Media Files

`MEDIA_URL` and `MEDIA_ROOT` are configured in settings but no views currently handle file uploads. Profile photos use a static default avatar.
