# TaskWise

> A smart productivity web app built by **Due-It Squad** (Muit, Panliboton, Sanglay)

TaskWise is a task management system developed across two software engineering courses, evolving from a desktop prototype to a full-stack web application.

---

## Versions

| | TaskWise v2.0 | TaskWise v3.0 |
|---|---|---|
| **Folder** | `flet_version/` | `flask_version/` |
| **Status** | Completed prototype | Current version |
| **Frontend** | Python (Flet) | React + Material UI + Vite |
| **Backend** | Python (Flet + SQLite) | Flask (Python) |
| **Database** | SQLite (local file) | PostgreSQL (Supabase) |
| **Auth** | bcrypt + session | Supabase Auth + Google OAuth |
| **AI** | Task categorization (basic) | Journal reflection via Groq (Llama) |
| **Deployment** | Desktop / Web via Flet | Runs locally; Vercel + Supabase deployment planned |
| **Multi-user** | ✅ | ✅ |
| **Google Integration** | ❌ | ✅ Classroom + Calendar sync |
| **Admin Panel** | ✅ | ✅ (improved) |

---

## Repository Structure

```
TaskWise/
├── flet_version/        # v2.0 — Python desktop app (SE1)
│   ├── taskwise/
│   ├── main.py
│   ├── db.py
│   └── README.md
│
├── flask_version/       # v3.0 — Full-stack web app (SE2)
│   ├── frontend/        # React + Vite
│   ├── backend/         # Flask API
│   └── README.md
│
└── README.md            # This file
```

---

## Team

**Due-It Squad**

| Member | Role |
|--------|------|
| Muit, Ivy Pauline B. | Backend / Database |
| Panliboton, Ayelyn Janne F. | UI/UX |
| Sanglay, Rhea Lizza B. | Documentation / QA |

---

## Quick Start

See the README inside each version folder for full setup instructions:

- [`flet_version/README.md`](./flet_version/README.md) — Python/Flet desktop app
- [`flask_version/README.md`](./flask_version/README.md) — Flask/React web app
