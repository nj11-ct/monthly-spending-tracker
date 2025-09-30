# Monthly Spending Tracker (FastAPI + SQLAlchemy + Jinja)

A simple monthly spending tracker with a FastAPI backend, Jinja templates, and SQLite (dev). Supports:
- Transactions CRUD via REST API
- Monthly summary (income, expenses, net)
- Dashboard with inline add (Bootstrap modal)
- Transactions page with totals and list
- Month navigation using `?month=YYYY-MM`

## Project Structure

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

## Quickstart (Windows PowerShell)

```powershell
cd backend
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Initialize DB (Alembic)
```powershell
# One-time (already initialized in repo if committed)
python -m pip install alembic
# ensure env.py is wired; then:
python -m alembic upgrade head
```

### Run the app
```powershell
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/
# API docs: http://127.0.0.1:8000/docs
```

## Seed Demo Data
Populate some income and expenses for a target month.

```powershell
# From backend directory, venv active
python scripts/seed.py --month 2025-09
```
- Omit `--month` to seed current month.
- Idempotent: re-running will skip duplicates for the chosen month.

## Environment
- DB URL: configured in `app/core/config.py` (defaults to `sqlite:///app/app.db`).
- To switch to Postgres, set `DATABASE_URL` and install `psycopg2-binary`.

## Tests (suggested)
- API: create/list/update/delete, month filter, summary totals
- Web: render dashboard/transactions; totals in template

## Notes
- FavIcon: place an icon at `app/static/favicon.ico` and it will be served at `/static/favicon.ico`.
- Month navigation: prev/next links preserve and update `?month=YYYY-MM`.
