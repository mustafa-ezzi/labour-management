# Local development

## Prerequisites

- Node 20+ and npm
- Python 3.12+ (project tested with 3.14) — use `py` on Windows
- Optional: Docker for PostgreSQL (`docker compose up -d` from repo root)

## Backend (Django)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
# Optional PostgreSQL:
# $env:DATABASE_URL="postgresql://labour:labour@127.0.0.1:5432/labour"
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```

API base: `http://127.0.0.1:8000/api/`. If port 8000 is taken, use `runserver 8001` and set `NUXT_PUBLIC_API_BASE` for the frontend.

Create admin user: `.\.venv\Scripts\python manage.py createsuperuser` (email + password).

## Frontend (Nuxt 3)

```powershell
cd frontend
npm install
# Optional: copy .env.example to .env and set NUXT_PUBLIC_API_BASE
npm run dev
```

Open `http://localhost:3000`, register a company, then use the bottom nav: **Home**, **Sites**, **Crew** (labour CRUD + payments), **Mark** (daily attendance with bulk save).

## Production settings

Set `DJANGO_SETTINGS_MODULE=config.settings.prod`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, and `CORS_ALLOWED_ORIGINS`.
