from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransactionBase(BaseModel):
    date: str
    description: str
    merchant: str
    amount: float
    transaction_type: str # income, expense, transfer
    category: str
    confidence: float = 1.0
    categorization_method: str = "rule"
    balance: Optional[float] = None
    reference: Optional[str] = None

class TransactionCreate(TransactionBase):
    document_id: str

class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    merchant: Optional[str] = None
    transaction_type: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    document_id: str

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: datetime
    transaction_count: int
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class CategorySpend(BaseModel):
    category: str
    amount: float
    percentage: float
    count: int

class MonthlyTrend(BaseModel):
    month: str # YYYY-MM
    income: float
    expense: float
    net: float

class TopMerchant(BaseModel):
    merchant: str
    category: str
    amount: float
    count: int

class AnomalyItem(BaseModel):
    id: str
    type: str # unusual_large, category_spike, recurring_payment, negative_cashflow, potential_duplicate
    severity: str # high, medium, low
    title: str
    description: str
    date: Optional[str] = None
    amount: Optional[float] = None
    transaction_id: Optional[str] = None

class RecurringPayment(BaseModel):
    merchant: str
    category: str
    estimated_amount: float
    frequency: str # monthly, weekly
    last_date: str

class AssessmentResult(BaseModel):
    rating: str # Good, Moderate, Needs Attention
    estimated_monthly_income: float
    estimated_monthly_expenses: float
    average_net_cashflow: float
    expense_to_income_ratio: float
    savings_rate: float
    income_consistency: str # High, Moderate, Volatile
    summary_explanation: str
    disclaimer: str = "AI-assisted financial analysis — not a lending decision."

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_cash_flow: float
    transaction_count: int
    avg_transaction_value: float
    savings_rate: float
    expense_to_income_ratio: float
    top_categories: List[CategorySpend]
    monthly_trends: List[MonthlyTrend]
    top_merchants: List[TopMerchant]
    recurring_payments: List[RecurringPayment]
    anomalies: List[AnomalyItem]
    assessment: AssessmentResult

class ChatMessage(BaseModel):
    role: str # user, assistant
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[Dict[str, Any]]] = None
