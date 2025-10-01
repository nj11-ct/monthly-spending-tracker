from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_api_key
from app.core import models, utils
from app.providers.ollama import OllamaProvider
from app.providers.base import SuggestionRequest, ReportRequest
from typing import List, Dict, Any

router = APIRouter(
    prefix="/api/v1/llm",
    tags=["llm"],
    dependencies=[Depends(require_api_key)],
    responses={401: {"description": "Invalid API key"}}
)

# Initialize Ollama provider
ollama_provider = OllamaProvider()


@router.post("/suggest")
async def suggest_category(request: SuggestionRequest):
    """Suggest transaction type and category based on description"""
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    
    response = await ollama_provider.suggest_category(request)
    
    return {
        "suggested_type": response.suggested_type,
        "suggested_category": response.suggested_category,
        "confidence": response.confidence
    }


@router.post("/reports/monthly")
async def generate_monthly_report(month: str, db: Session = Depends(get_db)):
    """Generate monthly spending report"""
    # Parse month and get transactions
    first = utils.parse_month(month)
    start, end = utils.month_bounds(first)
    
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.date.between(start, end))
        .order_by(models.Transaction.date.desc())
        .all()
    )
    
    if not transactions:
        return {
            "report_text": f"No transactions found for {month}. Start adding some transactions to get insights!",
            "insights": ["No data available for analysis"]
        }
    
    # Convert to dict format for the LLM
    transaction_dicts = [
        {
            "date": str(tx.date),
            "type": tx.type,
            "category": tx.category,
            "amount": float(tx.amount),
            "description": tx.description or ""
        }
        for tx in transactions
    ]
    
    request = ReportRequest(month=month, transactions=transaction_dicts)
    response = await ollama_provider.generate_report(request)
    
    return {
        "month": month,
        "report_text": response.report_text,
        "insights": response.insights,
        "transaction_count": len(transactions)
    }


@router.get("/reports/monthly")
async def get_monthly_report(month: str, db: Session = Depends(get_db)):
    """Get existing monthly report or generate new one"""
    # For now, always generate fresh report
    # Later we can add a reports table to store/cache reports
    return await generate_monthly_report(month, db)
