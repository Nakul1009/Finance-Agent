from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.schemas import ChatRequest, ChatResponse
from app.analytics.analytics_engine import FinancialAnalyticsEngine
from app.llm.llm_service import LLMService

router = APIRouter()
analytics_engine = FinancialAnalyticsEngine()
llm_service = LLMService()

@router.post("", response_model=ChatResponse)
async def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    user_msg = (req.message or "").strip()
    if not user_msg:
        return ChatResponse(reply="Please ask a valid financial query about your bank statement.")

    # Guardrail: Cap prompt length to 500 characters
    safe_msg = user_msg[:500]

    db_txs = db.query(Transaction).all()
    dict_txs = [
        {
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "merchant": t.merchant,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "category": t.category
        } for t in db_txs
    ]

    analytics_context = analytics_engine.compute_analytics(dict_txs)
    
    # Guardrail: Cap history items to last 6 messages
    history_dicts = [{"role": h.role, "content": h.content[:500]} for h in (req.history or [])[-6:]]

    reply = await llm_service.answer_financial_query(safe_msg, analytics_context, history_dicts)
    return ChatResponse(reply=reply)
