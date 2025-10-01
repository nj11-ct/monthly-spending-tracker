from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core import utils, models, schemas
from app.core.dependencies import get_db, require_api_key

router = APIRouter(
    prefix="/api/v1/summary", 
    tags=["summary"], 
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid API key"}}
)


@router.get("/", response_model=schemas.Summary, dependencies=[Depends(require_api_key)])
def month_summary(month: str | None = Query(None), db: Session = Depends(get_db)):
    first = utils.parse_month(month)
    start, end = utils.month_bounds(first)
    income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(
            models.Transaction.type == "income",
            models.Transaction.date.between(start, end),
        )
        .scalar()
        or 0
    )
    expenses = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(
            models.Transaction.type == "expense",
            models.Transaction.date.between(start, end),
        )
        .scalar()
        or 0
    )
    return schemas.Summary(
        income=float(income), expenses=float(expenses), net=float(income) - float(expenses)
    )
