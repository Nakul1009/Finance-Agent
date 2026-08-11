from app.analytics.analytics_engine import FinancialAnalyticsEngine

def test_analytics_calculations():
    engine = FinancialAnalyticsEngine()
    sample_txs = [
        {"id": "1", "date": "2026-01-01", "description": "Salary", "merchant": "Acme", "amount": 100000.0, "transaction_type": "income", "category": "Salary / Income"},
        {"id": "2", "date": "2026-01-05", "description": "Rent", "merchant": "Landlord", "amount": 25000.0, "transaction_type": "expense", "category": "Rent / Housing"},
        {"id": "3", "date": "2026-01-10", "description": "Food", "merchant": "Swiggy", "amount": 5000.0, "transaction_type": "expense", "category": "Food & Dining"},
        {"id": "4", "date": "2026-01-15", "description": "Shopping", "merchant": "Amazon", "amount": 10000.0, "transaction_type": "expense", "category": "Shopping"},
    ]

    res = engine.compute_analytics(sample_txs)
    assert res["total_income"] == 100000.0
    assert res["total_expenses"] == 40000.0
    assert res["net_cash_flow"] == 60000.0
    assert res["savings_rate"] == 60.0
    assert res["expense_to_income_ratio"] == 40.0
    assert res["assessment"]["rating"] == "Good"
