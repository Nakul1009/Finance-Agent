from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.schemas import TransactionResponse, TransactionUpdate

router = APIRouter()

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    document_id: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    search: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)

    if document_id:
        query = query.filter(Transaction.document_id == document_id)
    if category:
        query = query.filter(Transaction.category == category)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if search:
        s_term = f"%{search}%"
        query = query.filter(
            (Transaction.description.ilike(s_term)) |
            (Transaction.merchant.ilike(s_term)) |
            (Transaction.category.ilike(s_term))
        )

    return query.order_by(Transaction.date.desc()).all()

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if update_data.category is not None:
        ALLOWED_CATEGORIES = {
            "Salary / Income", "Food & Dining", "Shopping", "Utilities",
            "Rent / Housing", "Transport", "Healthcare", "Education",
            "Entertainment", "Insurance", "Investments", "Transfers",
            "ATM / Cash Withdrawal", "Fees / Charges", "Other"
        }
        if update_data.category not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{update_data.category}'. Allowed categories: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )
        tx.category = update_data.category
        tx.categorization_method = "manual"
        tx.confidence = 1.0
    if update_data.merchant is not None:
        tx.merchant = update_data.merchant
    if update_data.transaction_type is not None:
        tx.transaction_type = update_data.transaction_type

    db.commit()
    db.refresh(tx)
    return tx
