import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Document, Transaction
from app.schemas.schemas import DocumentResponse
from app.parsers.factory import DocumentParserFactory
from app.categorization.classifier import HybridTransactionClassifier
from app.sample_data.demo_generator import generate_synthetic_transactions

router = APIRouter()
classifier = HybridTransactionClassifier()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_filename = file.filename or "statement.csv"
    # Guardrail 1: Sanitize filename to prevent path traversal
    filename = os.path.basename(raw_filename)
    ext = os.path.splitext(filename)[1].lower()
    
    # Guardrail 2: Allowed extension whitelist
    if ext not in ['.csv', '.xlsx', '.xls', '.pdf']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, CSV, or XLSX.")

    # Guardrail 3: File size validation (Max 25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds maximum allowed limit of 25 MB.")

    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    # Create document record
    doc = Document(filename=filename, file_type=ext.replace('.', ''), status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        raw_txs = DocumentParserFactory.parse_document(file_path, filename)
        if not raw_txs:
            doc.status = "completed"
            doc.error_message = "No transactions found in file."
            db.commit()
            return doc

        categorized_txs = await classifier.categorize_batch(raw_txs)
        
        # Save to DB
        tx_objects = []
        for t in categorized_txs:
            tx_objects.append(Transaction(
                document_id=doc.id,
                date=t["date"],
                description=t["description"],
                merchant=t["merchant"],
                amount=t["amount"],
                transaction_type=t["transaction_type"],
                category=t["category"],
                confidence=t["confidence"],
                categorization_method=t["categorization_method"],
                balance=t.get("balance"),
                reference=t.get("reference")
            ))

        db.add_all(tx_objects)
        doc.transaction_count = len(tx_objects)
        doc.status = "completed"
        db.commit()
        db.refresh(doc)
        return doc

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/demo", response_model=DocumentResponse)
async def load_demo_document(db: Session = Depends(get_db)):
    # Clear existing demo documents if any
    old_demos = db.query(Document).filter(Document.filename == "Synthetic_Bank_Statement_Demo.csv").all()
    for d in old_demos:
        db.delete(d)
    db.commit()

    doc = Document(filename="Synthetic_Bank_Statement_Demo.csv", file_type="csv", status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    synthetic_txs = generate_synthetic_transactions()
    categorized_txs = await classifier.categorize_batch(synthetic_txs)

    tx_objects = []
    for t in categorized_txs:
        tx_objects.append(Transaction(
            document_id=doc.id,
            date=t["date"],
            description=t["description"],
            merchant=t["merchant"],
            amount=t["amount"],
            transaction_type=t["transaction_type"],
            category=t["category"],
            confidence=t["confidence"],
            categorization_method=t["categorization_method"],
            balance=t.get("balance"),
            reference=t.get("reference")
        ))

    db.add_all(tx_objects)
    doc.transaction_count = len(tx_objects)
    doc.status = "completed"
    db.commit()
    db.refresh(doc)
    return doc

@router.get("", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.upload_date.desc()).all()
