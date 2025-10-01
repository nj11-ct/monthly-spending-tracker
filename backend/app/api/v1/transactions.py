from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_api_key
from app.core import models, schemas, utils

router = APIRouter(
    prefix="/api/v1/transactions", 
    tags=["transactions"], 
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid API key"}}
)


@router.get("/", response_model=list[schemas.TransactionRead], dependencies=[Depends(require_api_key)])
def list_transactions(month: str | None = Query(None), db: Session = Depends(get_db)):
    first = utils.parse_month(month)
    start, end = utils.month_bounds(first)
    rows = (
        db.query(models.Transaction)
        .filter(models.Transaction.date.between(start, end))
        .order_by(models.Transaction.date.desc())
        .all()
    )
    return rows


@router.post("/", response_model=schemas.TransactionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    obj = models.Transaction(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{tx_id}", response_model=schemas.TransactionRead, dependencies=[Depends(require_api_key)])
def update_transaction(tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Transaction, tx_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_api_key)])
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Transaction, tx_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(obj)
    db.commit()
    return None
