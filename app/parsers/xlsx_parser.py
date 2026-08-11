import pandas as pd
from typing import List, Dict, Any
from app.parsers.csv_parser import CSVParser

class XLSXParser(CSVParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        df = self._read_excel_robust(file_path)
        if df is None or df.empty:
            return []

        col_map = self._detect_columns(df)
        transactions = []

        for _, row in df.iterrows():
            date_col = col_map.get('date')
            raw_date = row[date_col] if date_col and pd.notna(row[date_col]) else None
            date_str = self.clean_date(raw_date)

            desc_col = col_map.get('desc')
            desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else "Transaction"
            if not desc or desc.lower() == 'nan':
                desc = "Transaction"

            amount = 0.0
            tx_type = "expense"

            debit_col = col_map.get('debit')
            credit_col = col_map.get('credit')
            amount_col = col_map.get('amount')
            type_col = col_map.get('type')

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
                raw_amt = row[amount_col]
                if pd.notna(raw_amt):
                    str_amt = str(raw_amt).strip()
                    amount = self.clean_amount(str_amt)
                    if '-' in str_amt or (isinstance(raw_amt, (int, float)) and raw_amt < 0):
                        tx_type = "expense"
                    elif type_col and pd.notna(row[type_col]):
                        t_str = str(row[type_col]).lower()
                        if 'cr' in t_str or 'credit' in t_str or 'in' in t_str:
                            tx_type = "income"
                        else:
                            tx_type = "expense"
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

        return transactions

    def _read_excel_robust(self, file_path: str) -> pd.DataFrame:
        for skiprows in range(0, 10):
            try:
                df = pd.read_excel(file_path, skiprows=skiprows)
                df.columns = [str(c).strip() for c in df.columns]
                cols_lower = [c.lower() for c in df.columns]
                has_date = any(any(alias in c for alias in self.DATE_ALIASES) for c in cols_lower)
                has_desc = any(any(alias in c for alias in self.DESC_ALIASES) for c in cols_lower)
                has_amt = any(any(alias in c for alias in self.AMOUNT_ALIASES + self.DEBIT_ALIASES + self.CREDIT_ALIASES) for c in cols_lower)
                if (has_date and has_amt) or (has_date and has_desc):
                    return df
            except Exception:
                continue
        try:
            return pd.read_excel(file_path)
        except Exception:
            return None
