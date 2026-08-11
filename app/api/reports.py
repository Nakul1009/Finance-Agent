from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.models import Transaction, Document
from app.analytics.analytics_engine import FinancialAnalyticsEngine
from app.llm.llm_service import LLMService
from app.reports.report_generator import ReportGenerator

router = APIRouter()
analytics_engine = FinancialAnalyticsEngine()
llm_service = LLMService()

@router.get("/generate")
async def generate_report(document_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Transaction)
    doc_name = "FinBank_Statement_Report.pdf"
    if document_id:
        query = query.filter(Transaction.document_id == document_id)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc_name = doc.filename

    db_txs = query.all()
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

    analytics_data = analytics_engine.compute_analytics(dict_txs)
    exec_summary = await llm_service.generate_executive_summary(analytics_data)

    pdf_bytes = ReportGenerator.generate_pdf_report(analytics_data, doc_name, exec_summary)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="FinBank_Financial_Report_{doc_name}.pdf"'
        }
    )
