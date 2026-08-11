from typing import List, Dict, Any

def generate_synthetic_transactions() -> List[Dict[str, Any]]:
    """
    Generates 6 months of realistic synthetic bank statement data.
    """
    txs = [
        # January 2026
        {"date": "2026-01-01", "description": "ACH SALARY CREDIT ACME TECH CORP", "amount": 85000.0, "transaction_type": "income", "balance": 125000.0, "reference": "SAL20260101"},
        {"date": "2026-01-03", "description": "SWIGGY BANGALORE IN", "amount": 420.0, "transaction_type": "expense", "balance": 124580.0, "reference": "UPI1092301"},
        {"date": "2026-01-05", "description": "HOUSE RENT PAYMENT TO LANDLORD", "amount": 22000.0, "transaction_type": "expense", "balance": 102580.0, "reference": "UPI1092302"},
        {"date": "2026-01-07", "description": "UBER RIDE CITY TRIP", "amount": 350.0, "transaction_type": "expense", "balance": 102230.0, "reference": "UPI1092303"},
        {"date": "2026-01-10", "description": "BESCOM ELECTRICITY BILL", "amount": 1850.0, "transaction_type": "expense", "balance": 100380.0, "reference": "BILL202601"},
        {"date": "2026-01-12", "description": "AMAZON INDIA RETAIL", "amount": 3499.0, "transaction_type": "expense", "balance": 96881.0, "reference": "AMZ202601"},
        {"date": "2026-01-15", "description": "NETFLIX MONTHLY SUBSCRIPTION", "amount": 649.0, "transaction_type": "expense", "balance": 96232.0, "reference": "NFLX202601"},
        {"date": "2026-01-18", "description": "ZOMATO RESTAURANT ORDER", "amount": 680.0, "transaction_type": "expense", "balance": 95552.0, "reference": "UPI1092304"},
        {"date": "2026-01-22", "description": "ATM CASH WITHDRAWAL NFS HDFC", "amount": 5000.0, "transaction_type": "expense", "balance": 90552.0, "reference": "ATM202601"},
        {"date": "2026-01-25", "description": "MUTUAL FUND SIP ZERODHA", "amount": 15000.0, "transaction_type": "expense", "balance": 75552.0, "reference": "SIP202601"},

        # February 2026
        {"date": "2026-02-01", "description": "ACH SALARY CREDIT ACME TECH CORP", "amount": 85000.0, "transaction_type": "income", "balance": 160552.0, "reference": "SAL20260201"},
        {"date": "2026-02-04", "description": "SWIGGY INSTAMART GROCERIES", "amount": 1250.0, "transaction_type": "expense", "balance": 159302.0, "reference": "UPI2092301"},
        {"date": "2026-02-05", "description": "HOUSE RENT PAYMENT TO LANDLORD", "amount": 22000.0, "transaction_type": "expense", "balance": 137302.0, "reference": "UPI2092302"},
        {"date": "2026-02-08", "description": "AIRTEL BROADBAND BILL", "amount": 1199.0, "transaction_type": "expense", "balance": 136103.0, "reference": "BILL202602"},
        {"date": "2026-02-12", "description": "Croma Electronics Store", "amount": 48500.0, "transaction_type": "expense", "balance": 87603.0, "reference": "POS20260212"}, # UNUSUAL LARGE EXPENSE ANOMALY
        {"date": "2026-02-15", "description": "NETFLIX MONTHLY SUBSCRIPTION", "amount": 649.0, "transaction_type": "expense", "balance": 86954.0, "reference": "NFLX202602"},
        {"date": "2026-02-20", "description": "OLA CABS TRANSPORT", "amount": 420.0, "transaction_type": "expense", "balance": 86534.0, "reference": "UPI2092303"},
        {"date": "2026-02-25", "description": "MUTUAL FUND SIP ZERODHA", "amount": 15000.0, "transaction_type": "expense", "balance": 71534.0, "reference": "SIP202602"},

        # March 2026
        {"date": "2026-03-01", "description": "ACH SALARY CREDIT ACME TECH CORP", "amount": 85000.0, "transaction_type": "income", "balance": 156534.0, "reference": "SAL20260301"},
        {"date": "2026-03-05", "description": "HOUSE RENT PAYMENT TO LANDLORD", "amount": 22000.0, "transaction_type": "expense", "balance": 134534.0, "reference": "UPI3092301"},
        {"date": "2026-03-06", "description": "SWIGGY BANGALORE IN", "amount": 550.0, "transaction_type": "expense", "balance": 133984.0, "reference": "UPI3092302"},
        {"date": "2026-03-06", "description": "SWIGGY BANGALORE IN", "amount": 550.0, "transaction_type": "expense", "balance": 133434.0, "reference": "UPI3092303"}, # POTENTIAL DUPLICATE ANOMALY
        {"date": "2026-03-10", "description": "BESCOM ELECTRICITY BILL", "amount": 1920.0, "transaction_type": "expense", "balance": 131514.0, "reference": "BILL202603"},
        {"date": "2026-03-15", "description": "NETFLIX MONTHLY SUBSCRIPTION", "amount": 649.0, "transaction_type": "expense", "balance": 130865.0, "reference": "NFLX202603"},
        {"date": "2026-03-25", "description": "MUTUAL FUND SIP ZERODHA", "amount": 15000.0, "transaction_type": "expense", "balance": 115865.0, "reference": "SIP202603"},
        {"date": "2026-03-28", "description": "APOLLO PHARMACY MEDICALS", "amount": 1450.0, "transaction_type": "expense", "balance": 114415.0, "reference": "UPI3092304"},
    ]
    return txs
