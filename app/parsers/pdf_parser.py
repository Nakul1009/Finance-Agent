import re
import fitz # PyMuPDF
import pdfplumber
from typing import List, Dict, Any
from app.parsers.base_parser import BaseParser
from app.parsers.csv_parser import CSVParser

class PDFParser(BaseParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        # 1. Try structured table extraction via pdfplumber
        transactions = self._parse_with_pdfplumber_tables(file_path)
        if transactions:
            return transactions

        # 2. Try line-by-line text pattern extraction via fitz / pdfplumber text
        transactions = self._parse_with_text_regex(file_path)
        if transactions:
            return transactions

        # 3. OCR fallback handled by OCRParser if needed
        return []

    def _parse_with_pdfplumber_tables(self, file_path: str) -> List[Dict[str, Any]]:
        transactions = []
        try:
            with pdfplumber.open(file_path) as pdf:
                csv_parser_helper = CSVParser()
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        # Clean cells
                        cleaned_table = []
                        for row in table:
                            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                            cleaned_table.append(cleaned_row)
                        
                        # Convert to DataFrame
                        headers = cleaned_table[0]
                        data_rows = cleaned_table[1:]
                        import pandas as pd
                        df = pd.DataFrame(data_rows, columns=headers)
                        
                        # Detect columns using CSVParser logic
                        col_map = csv_parser_helper._detect_columns(df)
                        if not col_map.get('date') or not (col_map.get('amount') or col_map.get('debit') or col_map.get('credit')):
                            continue

                        for _, row in df.iterrows():
                            date_col = col_map.get('date')
                            raw_date = row[date_col] if date_col and pd.notna(row[date_col]) else None
                            date_str = self.clean_date(raw_date)

                            desc_col = col_map.get('desc')
                            desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else "Transaction"
                            if not desc or desc.lower() in ['nan', 'none', '']:
                                continue

                            amount = 0.0
                            tx_type = "expense"

                            debit_col = col_map.get('debit')
                            credit_col = col_map.get('credit')
                            amount_col = col_map.get('amount')

                            if debit_col and credit_col:
                                debit_val = self.clean_amount(row[debit_col]) if pd.notna(row[debit_col]) else 0.0
                                credit_val = self.clean_amount(row[credit_col]) if pd.notna(row[credit_col]) else 0.0
                                if credit_val > 0:
                                    amount = credit_val
                                    tx_type = "income"
                                elif debit_val > 0:
                                    amount = debit_val
                                    tx_type = "expense"
                            elif amount_col:
                                raw_amt = str(row[amount_col]).strip()
                                amount = self.clean_amount(raw_amt)
                                if '-' in raw_amt or 'dr' in raw_amt.lower():
                                    tx_type = "expense"
                                elif 'cr' in raw_amt.lower():
                                    tx_type = "income"
                                else:
                                    if any(kw in desc.lower() for kw in ['salary', 'credit', 'refund', 'cashback', 'deposit', 'received']):
                                        tx_type = "income"
                                    else:
                                        tx_type = "expense"

                            if amount <= 0:
                                continue

                            bal_col = col_map.get('balance')
                            balance = self.clean_amount(row[bal_col]) if bal_col and pd.notna(row[bal_col]) else None

                            ref_col = col_map.get('ref')
                            reference = str(row[ref_col]).strip() if ref_col and pd.notna(row[ref_col]) else None

                            transactions.append({
                                "date": date_str,
                                "description": desc,
                                "merchant": desc,
                                "amount": round(amount, 2),
                                "transaction_type": tx_type,
                                "balance": round(balance, 2) if balance is not None else None,
                                "reference": reference
                            })
        except Exception:
            pass

        return transactions

    def _parse_with_text_regex(self, file_path: str) -> List[Dict[str, Any]]:
        transactions = []
        full_text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                full_text += page.get_text() + "\n"
        except Exception:
            return []

        if not full_text.strip():
            return []

        lines = full_text.splitlines()
        # Common line pattern: Date (DD/MM/YYYY or YYYY-MM-DD or DD-MMM-YYYY) followed by narration and numbers
        date_pattern = re.compile(r'(\d{1,2}[\/\-\.](?:\d{1,2}|[A-Za-z]{3})[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})')
        number_pattern = re.compile(r'[\s]+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(Cr|Dr)?')

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            date_match = date_pattern.search(line_str)
            if not date_match:
                continue

            raw_date = date_match.group(1)
            date_str = self.clean_date(raw_date)

            # Find all numbers in the line
            numbers = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2})', line_str)
            if not numbers:
                continue

            # Extract amount (usually the first or second number)
            amounts = [self.clean_amount(n) for n in numbers if self.clean_amount(n) > 0]
            if not amounts:
                continue

            amount = amounts[0]
            balance = amounts[1] if len(amounts) > 1 else None

            # Narration is text between date and numbers
            narration = date_pattern.sub('', line_str)
            for num_str in numbers:
                narration = narration.replace(num_str, '')
            narration = re.sub(r'\b(Cr|Dr|INR|USD|EUR)\b', '', narration, flags=re.IGNORECASE).strip()

            if not narration:
                narration = "Bank Transaction"

            tx_type = "expense"
            if 'cr' in line_str.lower() or any(kw in narration.lower() for kw in ['salary', 'credit', 'deposit', 'received']):
                tx_type = "income"

            transactions.append({
                "date": date_str,
                "description": narration,
                "merchant": narration,
                "amount": round(amount, 2),
                "transaction_type": tx_type,
                "balance": round(balance, 2) if balance is not None else None,
                "reference": None
            })

        return transactions
