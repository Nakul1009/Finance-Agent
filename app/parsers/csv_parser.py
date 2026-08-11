import pandas as pd
from typing import List, Dict, Any
from app.parsers.base_parser import BaseParser

class CSVParser(BaseParser):
    DATE_ALIASES = ['date', 'txn date', 'transaction date', 'value date', 'posting date', 'dt']
    DESC_ALIASES = ['description', 'narration', 'particulars', 'details', 'transaction details', 'remark', 'remarks', 'payee']
    DEBIT_ALIASES = ['debit', 'dr', 'withdrawal', 'withdrawals', 'out', 'debit amount']
    CREDIT_ALIASES = ['credit', 'cr', 'deposit', 'deposits', 'in', 'credit amount']
    AMOUNT_ALIASES = ['amount', 'txn amount', 'sum', 'val']
    BALANCE_ALIASES = ['balance', 'running balance', 'bal', 'closing balance']
    TYPE_ALIASES = ['type', 'txn type', 'transaction type', 'dr/cr', 'd/c']
    REF_ALIASES = ['reference', 'ref', 'ref no', 'chq/ref no', 'transaction id', 'utr']

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        df = self._read_csv_robust(file_path)
        if df is None or df.empty:
            return []

        col_map = self._detect_columns(df)
        transactions = []

        for _, row in df.iterrows():
            # Date
            date_col = col_map.get('date')
            raw_date = row[date_col] if date_col and pd.notna(row[date_col]) else None
            date_str = self.clean_date(raw_date)

            # Description
            desc_col = col_map.get('desc')
            desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else "Transaction"
            if not desc or desc.lower() == 'nan':
                desc = "Transaction"

            # Determine Amount and Transaction Type
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
                    # Check if negative or signed
                    if '-' in str_amt or (isinstance(raw_amt, (int, float)) and raw_amt < 0):
                        tx_type = "expense"
                    elif type_col and pd.notna(row[type_col]):
                        t_str = str(row[type_col]).lower()
                        if 'cr' in t_str or 'credit' in t_str or 'in' in t_str:
                            tx_type = "income"
                        else:
                            tx_type = "expense"
                    else:
                        # Fallback heuristic: check description for keywords
                        if any(kw in desc.lower() for kw in ['salary', 'credit', 'refund', 'cashback', 'deposit', 'received']):
                            tx_type = "income"
                        else:
                            tx_type = "expense"

            if amount <= 0:
                continue # skip 0 amount lines

            # Balance
            bal_col = col_map.get('balance')
            balance = self.clean_amount(row[bal_col]) if bal_col and pd.notna(row[bal_col]) else None

            # Ref
            ref_col = col_map.get('ref')
            reference = str(row[ref_col]).strip() if ref_col and pd.notna(row[ref_col]) else None

            transactions.append({
                "date": date_str,
                "description": desc,
                "merchant": desc, # Will be normalized in categorization step
                "amount": round(amount, 2),
                "transaction_type": tx_type,
                "balance": round(balance, 2) if balance is not None else None,
                "reference": reference
            })

        return transactions

    def _read_csv_robust(self, file_path: str) -> pd.DataFrame:
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            for skiprows in range(0, 10):
                try:
                    df = pd.read_csv(file_path, encoding=encoding, skiprows=skiprows)
                    # Clean column names
                    df.columns = [str(c).strip() for c in df.columns]
                    # Check if dataframe has at least 2 columns matching header candidates
                    cols_lower = [c.lower() for c in df.columns]
                    has_date = any(any(alias in c for alias in self.DATE_ALIASES) for c in cols_lower)
                    has_desc = any(any(alias in c for alias in self.DESC_ALIASES) for c in cols_lower)
                    has_amt = any(any(alias in c for alias in self.AMOUNT_ALIASES + self.DEBIT_ALIASES + self.CREDIT_ALIASES) for c in cols_lower)
                    if (has_date and has_amt) or (has_date and has_desc):
                        return df
                except Exception:
                    continue
        # Fallback to direct read
        try:
            return pd.read_csv(file_path)
        except Exception:
            return None

    def _detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        col_map = {}
        cols = list(df.columns)
        
        def match_alias(aliases):
            for c in cols:
                c_clean = c.lower().strip()
                if c_clean in aliases:
                    return c
            for c in cols:
                c_clean = c.lower().strip()
                if any(alias in c_clean for alias in aliases):
                    return c
            return None

        col_map['date'] = match_alias(self.DATE_ALIASES)
        col_map['desc'] = match_alias(self.DESC_ALIASES)
        col_map['debit'] = match_alias(self.DEBIT_ALIASES)
        col_map['credit'] = match_alias(self.CREDIT_ALIASES)
        col_map['amount'] = match_alias(self.AMOUNT_ALIASES)
        col_map['balance'] = match_alias(self.BALANCE_ALIASES)
        col_map['type'] = match_alias(self.TYPE_ALIASES)
        col_map['ref'] = match_alias(self.REF_ALIASES)

        return col_map
