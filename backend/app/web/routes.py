from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core import utils, models
from app.core.dependencies import get_db

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/")
def dashboard(request: Request, month: str | None = None, db: Session = Depends(get_db)):
    first = utils.parse_month(month)
    start, end = utils.month_bounds(first)

    income_rows = (
        db.query(models.Transaction)
        .filter(models.Transaction.type == "income", models.Transaction.date.between(start, end))
        .order_by(models.Transaction.date.desc())
        .all()
    )
    expense_rows = (
        db.query(models.Transaction)
        .filter(models.Transaction.type == "expense", models.Transaction.date.between(start, end))
        .order_by(models.Transaction.date.desc())
        .all()
    )

    income_total = sum(float(x.amount) for x in income_rows)
    expense_total = sum(float(x.amount) for x in expense_rows)

    month_iso = utils.month_str(first)
    month_label = first.strftime("%B, %Y")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "month": month_iso,
            "month_label": month_label,
            "prev_month": utils.prev_month_str(month_iso),
            "next_month": utils.next_month_str(month_iso),
            "incomes": income_rows,
            "expenses": expense_rows,
            "income_total": income_total,
            "expense_total": expense_total,
        },
    )


@router.get("/transactions")
def transactions_page(request: Request, month: str | None = None, db: Session = Depends(get_db)):
    first = utils.parse_month(month)
    start, end = utils.month_bounds(first)

    txs = (
        db.query(models.Transaction)
        .filter(models.Transaction.date.between(start, end))
        .order_by(models.Transaction.date.desc())
        .all()
    )

    income_total = sum(float(x.amount) for x in txs if x.type == "income")
    expense_total = sum(float(x.amount) for x in txs if x.type == "expense")

    month_iso = utils.month_str(first)
    month_label = first.strftime("%B, %Y")

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "month": month_iso,
            "month_label": month_label,
            "prev_month": utils.prev_month_str(month_iso),
            "next_month": utils.next_month_str(month_iso),
            "transactions": txs,
            "income_total": income_total,
            "expense_total": expense_total,
        },
    )
