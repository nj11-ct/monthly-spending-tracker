# Monthly Spending Tracker (FastAPI + SQLAlchemy + Jinja)

A small FastAPI app with Jinja templates to track monthly income and expenses. SQLite for local dev, Alembic migrations, Bootstrap UI.

## Features
- Transactions CRUD API under `/api/v1/*`
- Monthly summary: income, expenses, net
- Dashboard with inline add via Bootstrap modal
- Transactions page with totals and list
- Month synced via `?month=YYYY-MM`

## Run locally (Windows PowerShell)

1) Clone and enter backend
```powershell
git clone <your-repo-url>
cd monthly-spending-tracker\backend
```

2) Create venv and install deps
```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3) Create database (Alembic)
```powershell
python -m alembic upgrade head
```

4) (Optional) Seed demo data
```powershell
python scripts/seed.py --month 2025-09
```

5) Start the app
```powershell
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/
# API docs: http://127.0.0.1:8000/docs
```

## Notes
- Database path: `backend/app/app.db` (SQLite). It is ignored by git, so your local data is not pushed to GitHub. Use the seed script or POST via `/docs` to create sample data after a fresh clone.
- To switch databases, set `DATABASE_URL` in environment (e.g., Postgres) and install the appropriate driver.
- FavIcon (optional): place an icon at `app/static/favicon.ico`.

## Project layout
```
backend/
  app/
    core/ (config, database, models, schemas, dependencies, utils)
    api/v1/ (transactions, summary)
    web/ (routes)
    templates/ (base, index, transactions, _transaction_form)
    static/ (css/js, favicon)
  alembic/ (migrations)
  scripts/ (seed.py)
  requirements.txt
```
