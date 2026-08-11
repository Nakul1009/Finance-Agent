import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    transaction_count = Column(Integer, default=0)
    status = Column(String(30), default="processing")
    error_message = Column(Text, nullable=True)

    transactions = relationship("Transaction", back_populates="document", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    date = Column(String(10), nullable=False, index=True) # YYYY-MM-DD
    description = Column(Text, nullable=False)
    merchant = Column(String(150), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False, index=True) # income, expense, transfer
    category = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    categorization_method = Column(String(20), default="rule") # rule, nemotron, manual
    balance = Column(Float, nullable=True)
    reference = Column(String(100), nullable=True)

    document = relationship("Document", back_populates="transactions")
