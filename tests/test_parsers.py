import os
import tempfile
import pandas as pd
from app.parsers.csv_parser import CSVParser
from app.parsers.xlsx_parser import XLSXParser

def test_csv_parser_standard():
    parser = CSVParser()
    csv_data = """Date,Description,Debit,Credit,Balance
2026-01-01,ACH SALARY CREDIT,,85000.0,85000.0
2026-01-03,SWIGGY FOOD ORDER,450.0,,84550.0
2026-01-05,HOUSE RENT PAYMENT,22000.0,,62550.0
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        tmp.write(csv_data)
        tmp_path = tmp.name

    try:
        txs = parser.parse(tmp_path)
        assert len(txs) == 3
        assert txs[0]["transaction_type"] == "income"
        assert txs[0]["amount"] == 85000.0
        assert txs[1]["transaction_type"] == "expense"
        assert txs[1]["amount"] == 450.0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_xlsx_parser_standard():
    parser = XLSXParser()
    df = pd.DataFrame([
        {"Txn Date": "2026-02-01", "Narration": "SALARY CREDIT", "Credit Amount": 90000.0, "Debit Amount": None},
        {"Txn Date": "2026-02-05", "Narration": "UBER RIDE", "Credit Amount": None, "Debit Amount": 350.0}
    ])
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        txs = parser.parse(tmp_path)
        assert len(txs) == 2
        assert txs[0]["transaction_type"] == "income"
        assert txs[1]["amount"] == 350.0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
