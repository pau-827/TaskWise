# TaskWise v3.0 — Flask + React Version

TaskWise v3.0 is a full-stack productivity web app. It rebuilds the original Flet/SQLite version (v2.0) on **React + Material UI**, **Flask**, and **Supabase**, and adds Google integrations, AI journaling, a recipe manager, and a hidden admin panel.

**Team:** Due-It Squad (Muit, Panliboton, Sanglay)

---

## Why We Rebuilt It

The Flet version hit limits in UI effects and account authentication. Moving to React + Supabase gave us:

- Richer UI (animations, themes, responsive layouts)
- Real authentication (email + OTP verification, Google OAuth)
- A cloud database with Row Level Security instead of a local SQLite file
- A backend that can call external APIs (Google Classroom, Groq AI)

---

## Features

### Accounts and Security
- Email + password signup with a **6-digit OTP email verification**
- **Continue with Google** (OAuth 2.0 through Supabase)
- Row Level Security: users can only access their own data
- Settings: edit display name, profile photo, change password, delete account data

### Tasks
- Create, edit, delete, and complete tasks (title, description, category, priority, due date/time, reminder time)
- Search, filter by category, and sort (date created, due date, priority, title)
- Category mix donut chart and progress summary (total, pending, completed, overdue)
- **Export to PDF**: current view or all tasks, with summary stats
- **Google Classroom sync**: import assignments as tasks, with an unsync button that removes only the imported ones

### Calendar
- Month grid showing TaskWise tasks
- **Google Calendar events** displayed directly (read-only, not copied into the task list)
- **Philippine public holidays** from the free Nager.Date API (no key needed)
- "To-do Today" mini checklist (stored in the browser's localStorage)

### Journal
- Entry list with search, mood selector, and autosaved timestamps
- **AI Reflect**: Groq (Llama 3.3) returns an empathetic reflection and suggests a mood. The suggestion pre-selects the mood chip and can be overridden.

### Recipes
- Add recipes with category (Breakfast, Lunch, Dinner, Dessert, Snack, Beverages, Others), ingredients, steps, and budget range
- Photo upload to Supabase Storage

### Admin Panel
- Reached through a hidden, tongue-in-cheek login page, not the normal login
- Role check against the `profiles` table (`role = 'admin'`)
- Platform stats, user list with search, ban/unban, delete user data, and an activity log

### Support
- **Report Issue** sends an email to the admin team through EmailJS

### Themes
- Light, Dark, and Pink. The theme applies to the app and to the loading and landing pages.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Material UI, React Router, Recharts, dayjs |
| Backend | Flask, Flask-CORS |
| Database / Auth / Storage | Supabase (PostgreSQL, Auth, Storage) |
| AI | Groq API (`llama-3.3-70b-versatile`) |
| Integrations | Google Classroom API, Google Calendar API, Nager.Date, EmailJS |

---

## Architecture

```text
┌──────────────────────┐        ┌───────────────────────────┐
│   React (Vite, MUI)  │ ─────► │   Supabase                │
│                      │        │   Auth · Postgres · Storage│
│ Tasks · Calendar     │        └───────────────────────────┘
│ Journal · Recipes    │
│ Settings · Admin     │        ┌───────────────────────────┐
│                      │ ─────► │   Flask API               │
└──────────┬───────────┘        │   /api/classroom/*        │
           │                    │   /api/journal/reflect    │
           │                    └────────────┬──────────────┘
           │                                 │
           ▼                                 ▼
  Google Calendar API              Google Classroom API · Groq
  Nager.Date (holidays)
  EmailJS (issue reports)
```

**Rule of thumb:** anything that is plain data access goes straight to Supabase from the browser. Anything that needs a secret key or server-side calls (Classroom sync, AI reflection) goes through Flask.

---

## Project Structure

```
flask_version/
├── frontend/
│   └── src/
│       ├── admin/            # AdminLogin, AdminPanel, AdminRoute
│       ├── components/       # AppShell, Header, LoadingScreen
│       ├── context/          # AppContext/Provider, ThemeContext/Provider
│       ├── pages/            # Landing, Login, Signup, Tasks, Calendar,
│       │                     # Journal, Recipes, Settings
│       ├── services/         # supabase.js, api.js
│       ├── theme/            # themes.js
│       ├── App.jsx
│       └── main.jsx
│
└── backend/
    ├── routes/               # task_routes, classroom_routes, journal_routes
    ├── services/             # task_service, classroom_service, journal_service
    ├── utils/                # supabase_client.py
    ├── app.py
    └── .env
```

---

## Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- A Supabase project
- (Optional) Google Cloud project with OAuth, Classroom API, and Calendar API enabled
- (Optional) Groq API key

### 1. Clone

```bash
git clone https://github.com/pau-827/TaskWise.git
cd TaskWise/flask_version
```

### 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Run it:

```bash
npm run dev
```

### 3. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install flask flask-cors supabase python-dotenv groq google-api-python-client google-auth
```

Create `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GROQ_API_KEY=your-groq-key
FLASK_ENV=development
```

Run it:

```bash
python app.py
```

The API runs at `http://localhost:5000`.

### 4. Supabase Setup

**Tables** (all with RLS enabled):

| Table | Purpose |
|---|---|
| `tasks` | `id, user_id, title, description, category, priority, status, due_date, reminder_at, synced_from, created_at` |
| `journal_entries` | `id, user_id, title, content, mood, ai_reflection, ai_mood, created_at, updated_at` |
| `recipes` | `id, user_id, title, category, ingredients, steps, budget_min, budget_max, image_url, created_at` |
| `profiles` | `id, email, display_name, role, status, created_at` |
| `admin_logs` | `id, action, details, target_email, created_at` |

**Storage:** create a **public** bucket named `recipe-images`.

**RLS policies:**
- `tasks`, `journal_entries`, `recipes`: SELECT / INSERT / UPDATE / DELETE where `auth.uid() = user_id`
- `profiles`: users can read, insert, update, and delete their own row. A separate policy lets admins read all rows.
- `admin_logs`: admins only

**Profile trigger:** a database trigger on `auth.users` creates a `profiles` row for every new user with `role = 'user'`.

**Make an admin:**

```sql
UPDATE public.profiles SET role = 'admin' WHERE email = 'your-admin@email.com';
```

**Auth settings:**
- Enable the email provider with **Confirm email**, and edit the *Confirm signup* template to use `{{ .Token }}` so users receive an OTP code instead of a link
- Enable the Google provider with your Client ID and Secret
- Add these Redirect URLs: `http://localhost:5173/tasks` and `http://localhost:5173/auth/admin-callback`

### 5. Google Setup (for Classroom and Calendar)

In Google Cloud Console:
1. Enable **Google Classroom API** and **Google Calendar API**
2. Configure the OAuth consent screen and add the scopes:
   - `classroom.courses.readonly`
   - `classroom.coursework.me.readonly`
   - `calendar.readonly`
3. Add your Supabase callback URL to the authorized redirect URIs

> Classroom and Calendar features only work when the user signed in **with Google**. Email/password accounts have no Google access token.

---

## API Endpoints (Flask)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks` | List tasks |
| POST | `/api/classroom/sync` | Import Google Classroom assignments as tasks |
| DELETE | `/api/classroom/unsync` | Remove tasks imported from Classroom |
| POST | `/api/journal/reflect` | Generate an AI reflection and suggested mood |

---

## Security Notes

- Supabase JWTs authenticate every request; RLS enforces per-user data access
- Secrets live in `.env` files, which are excluded through `.gitignore`
- Admin access requires `role = 'admin'` in `profiles`, checked client-side by `AdminRoute`

---

## Known Limitations

- The Flask backend currently runs locally. Classroom sync and AI reflection need it running.
- Google provider tokens are short-lived and are not refreshed automatically. Log in with Google again if sync stops working.
- **Ban** sets a status flag in `profiles`; login does not yet block banned users.
- **Delete user** in the admin panel removes the user's data and profile, but not the Supabase Auth record, since that requires a server-side service-role call.
- The EmailJS keys are currently hard-coded in `Settings.jsx`. Move them to `VITE_` environment variables before deploying.
- Reminder time is saved per task, but scheduled reminder delivery is not implemented yet.
- No automated test suite yet.

---

## Future Enhancements

- Deploy Flask (Render, Railway, or similar) and the frontend (Vercel)
- Token refresh for Google integrations
- Scheduled reminders and notifications
- Enforce bans at login and delete Auth users through a service-role endpoint
- CI/CD with GitHub Actions plus automated tests
- Recurring tasks, shared task lists, and a PWA install option

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Blank page after login | Missing import or a runtime error. Check the browser console. |
| `500` from `/rest/v1/profiles` | An RLS policy on `profiles` is erroring. Recreate the policies. |
| `new row violates row-level security policy` | An insert is missing `user_id`, or the request lacks the user's JWT. |
| Classroom sync says no Google token | The account was not signed in through Google. |
| AI reflection fails with `model_decommissioned` | Update the Groq model name in `journal_service.py`. |
| OTP email contains a link, not a code | The *Confirm signup* email template still uses `{{ .ConfirmationURL }}`. |

---

## Screenshots

_Add screenshots here: Landing, Tasks, Calendar, Journal, Recipes, Settings, Admin Panel, and the three themes._
