from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.schemas import AnalyticsSummary
from app.analytics.analytics_engine import FinancialAnalyticsEngine

router = APIRouter()
analytics_engine = FinancialAnalyticsEngine()

@router.get("", response_model=AnalyticsSummary)
def get_analytics(document_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Transaction)
    if document_id:
        query = query.filter(Transaction.document_id == document_id)
    
    db_txs = query.all()
    
    # Convert DB models to dict list for analytics engine
    dict_txs = []
    for t in db_txs:
        dict_txs.append({
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "merchant": t.merchant,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "category": t.category,
            "confidence": t.confidence,
            "categorization_method": t.categorization_method,
            "balance": t.balance,
            "reference": t.reference
        })

    return analytics_engine.compute_analytics(dict_txs)
