from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import re

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a document file and returns a list of normalized transaction dictionaries.
        Each dictionary contains:
            date (str: YYYY-MM-DD)
            description (str)
            merchant (str)
            amount (float > 0)
            transaction_type (str: 'income' | 'expense' | 'transfer')
            balance (float, optional)
            reference (str, optional)
        """
        pass

    def clean_amount(self, val: Any) -> float:
        if val is None or val == "":
            return 0.0
        if isinstance(val, (int, float)):
            return float(abs(val))
        s = str(val).strip()
        # Remove currency symbols ($, ₹, €, £, Rs., INR), commas, spaces
        s = re.sub(r'[^\d.\-]', '', s)
        try:
            return float(abs(float(s)))
        except ValueError:
            return 0.0

    def clean_date(self, val: Any) -> str:
        if not val:
            return "2026-01-01"
        s = str(val).strip()
        # Match common date patterns: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, MM/DD/YYYY, YYYY/MM/DD, DD-MMM-YYYY
        # Try pandas parse or regex
        import pandas as pd
        try:
            dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
            if not pd.isna(dt):
                return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        return "2026-01-01"
