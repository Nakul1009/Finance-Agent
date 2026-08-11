import sys
from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    print("=== FinBank AI End-to-End Verification ===")
    client = TestClient(app)

    # 1. Health check
    res = client.get("/api/health")
    print(f"[1/6] Health Check: Status {res.status_code} -> {res.json()}")
    assert res.status_code == 200

    # 2. Demo document loading
    res = client.post("/api/documents/demo")
    print(f"[2/6] Load Demo Statement: Status {res.status_code} -> Tx Count: {res.json().get('transaction_count')}")
    assert res.status_code == 200

    # 3. Get transactions
    res = client.get("/api/transactions")
    txs = res.json()
    print(f"[3/6] Get Transactions: Retrived {len(txs)} transactions")
    assert res.status_code == 200 and len(txs) > 0

    # 4. Get analytics
    res = client.get("/api/analytics")
    an = res.json()
    print(f"[4/6] Analytics Summary:")
    print(f"      - Income: INR {an['total_income']:,.2f}")
    print(f"      - Expenses: INR {an['total_expenses']:,.2f}")
    print(f"      - Net Cash Flow: INR {an['net_cash_flow']:,.2f}")
    print(f"      - Savings Rate: {an['savings_rate']}%")
    print(f"      - Stability Rating: {an['assessment']['rating']}")
    assert res.status_code == 200

    # 5. AI Chat Assistant
    res = client.post("/api/chat", json={"message": "How much did I spend on food?"})
    reply = res.json().get('reply', '')
    safe_reply = reply.replace('\u20b9', 'INR ').replace('**', '')
    print(f"[5/6] AI Assistant Q&A:")
    print(f"      User Query: 'How much did I spend on food?'")
    print(f"      AI Reply: {safe_reply}")
    assert res.status_code == 200 and len(reply) > 0

    # 6. Report Generation
    res = client.get("/api/reports/generate")
    pdf_bytes = res.content
    print(f"[6/6] PDF Report Generation: Received {len(pdf_bytes)} bytes of application/pdf")
    assert res.status_code == 200 and len(pdf_bytes) > 1000

    print("\nALL 6 END-TO-END VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_verification()
