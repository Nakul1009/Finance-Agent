import re
from typing import Tuple

class CategorizationRulesEngine:
    CATEGORIES = [
        "Salary / Income",
        "Food & Dining",
        "Shopping",
        "Utilities",
        "Rent / Housing",
        "Transport",
        "Healthcare",
        "Entertainment",
        "Education",
        "Insurance",
        "Investments",
        "Transfers",
        "ATM / Cash Withdrawal",
        "Fees / Charges",
        "Other"
    ]

    RULE_PATTERNS = [
        # (Category, confidence, keywords_list)
        ("Salary / Income", 0.98, [r'salary', r'payroll', r'stipend', r'divident', r'freelance', r'interest credit']),
        ("Food & Dining", 0.95, [r'swiggy', r'zomato', r'domino', r'mcdonald', r'starbucks', r'restaurant', r'cafe', r'diner', r'pizza', r'burger', r'bakery', r'dining', r'food', r'instamart', r'blinkit', r'zepto']),
        ("Shopping", 0.90, [r'amazon', r'flipkart', r'myntra', r'zara', r'apparel', r'clothing', r'supermarket', r'retail', r'dmart', r'bigbasket', r'mall']),
        ("Utilities", 0.95, [r'electricity', r'water bill', r'gas bill', r'broadband', r'wifi', r'airtel', r'jio', r'vi', r'dth', r'utility', r'bescom']),
        ("Rent / Housing", 0.98, [r'house rent', r'apartment rent', r'rent payment', r'maintenance charge', r'society fee', r'landlord']),
        ("Transport", 0.95, [r'uber', r'ola', r'rapido', r'metro', r'railway', r'irctc', r'cab', r'taxi', r'petrol', r'fuel', r'shell', r'toll', r'parking']),
        ("Healthcare", 0.92, [r'hospital', r'clinic', r'pharmacy', r'chemist', r'apollo', r'1mg', r'pharmeasy', r'dental', r'doctor', r'lab test', r'medical']),
        ("Entertainment", 0.95, [r'netflix', r'spotify', r'prime video', r'pvr', r'inox', r'cinema', r'movie', r'bookmyshow', r'gaming', r'hotstar', r'youtube']),
        ("Education", 0.92, [r'udemy', r'coursera', r'tuition', r'school', r'college', r'university', r'coaching', r'exam fee', r'books']),
        ("Insurance", 0.95, [r'insurance', r'lic india', r'hdfc ergo', r'max bupa', r'premium', r'policybazaar', r'health insurance']),
        ("Investments", 0.95, [r'zerodha', r'groww', r'upstox', r'mutual fund', r'sip', r'nps', r'ppf', r'stocks', r'demat', r'fd deposit']),
        ("ATM / Cash Withdrawal", 0.98, [r'atm', r'cash withdrawal', r'cash wdl', r'nfs']),
        ("Fees / Charges", 0.95, [r'bank charge', r'penalty', r'annual fee', r'interest debit', r'forex fee', r'processing fee', r'late fee']),
        ("Transfers", 0.85, [r'transfer to', r'transfer from', r'self transfer', r'own account', r'to account']),
    ]

    def classify_by_rules(self, merchant: str, description: str, tx_type: str) -> Tuple[str, float]:
        text = f"{merchant} {description}".lower()

        if tx_type == "income" and any(re.search(pat, text) for pat in [r'salary', r'payroll', r'stipend']):
            return ("Salary / Income", 0.98)

        for category, conf, patterns in self.RULE_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, text):
                    return (category, conf)

        # Fallback income vs expense rule
        if tx_type == "income":
            return ("Salary / Income", 0.65)

        return ("Other", 0.50) # Low confidence trigger for Nemotron LLM
