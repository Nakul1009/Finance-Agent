import re

class MerchantNormalizer:
    MERCHANT_PATTERNS = [
        (r'swiggy', 'Swiggy'),
        (r'zomato', 'Zomato'),
        (r'domino', 'Domino\'s Pizza'),
        (r'mcdonald|mcd', 'McDonald\'s'),
        (r'starbucks', 'Starbucks'),
        (r'uber', 'Uber'),
        (r'ola', 'Ola Cabs'),
        (r'rapido', 'Rapido'),
        (r'metro', 'City Metro'),
        (r'netflix|nflx', 'Netflix'),
        (r'spotify', 'Spotify'),
        (r'prime video|amazon prime', 'Amazon Prime'),
        (r'amazon', 'Amazon'),
        (r'flipkart', 'Flipkart'),
        (r'myntra', 'Myntra'),
        (r'blinkit|grofers', 'Blinkit'),
        (r'zepto', 'Zepto'),
        (r'instamart', 'Swiggy Instamart'),
        (r'bigbasket', 'BigBasket'),
        (r'dmart', 'DMart'),
        (r'airtel', 'Airtel Broadband/Mobile'),
        (r'jio', 'Reliance Jio'),
        (r'bescom|electricity|power', 'Electricity Bill'),
        (r'water board|water bill', 'Water Supply'),
        (r'lic india|lic', 'LIC Insurance'),
        (r'hdfc ergo|insurance', 'Insurance Payment'),
        (r'zerodha|groww|upstox', 'Investment / Stock Broker'),
        (r'mutual fund|mf', 'Mutual Fund SIP'),
        (r'salary|payroll', 'Salary Credit'),
        (r'rent|house rent', 'House Rent'),
        (r'atm|cash withdrawal', 'ATM Cash Withdrawal'),
        (r'bank charges|penalty|service charge', 'Bank Fee / Charge'),
        (r'udemy|coursera|school|college|tuition', 'Education Fee'),
        (r'apollo|pharmacy|1mg|pharmeasy|hospital|clinic', 'Healthcare / Pharmacy'),
    ]

    def normalize(self, description: str) -> str:
        if not description:
            return "General Transaction"
        
        desc_lower = description.lower()
        for pattern, clean_name in self.MERCHANT_PATTERNS:
            if re.search(pattern, desc_lower):
                return clean_name
        
        # Clean generic raw narration: strip UPI prefixes, POS, NEFT, IMPS, numbers
        clean = re.sub(r'\b(UPI|POS|NEFT|IMPS|RTGS|ACH|BILLDESK|PAYTM|INB|TFR|CR|DR)\b', '', description, flags=re.IGNORECASE)
        clean = re.sub(r'[\d\-\/\.\#\@]', ' ', clean)
        clean = ' '.join(clean.split())
        
        if len(clean) > 3:
            return clean.title()[:40]
        return description.title()[:40]
