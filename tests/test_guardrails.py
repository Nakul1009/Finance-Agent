from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_invalid_extension():
    response = client.post(
        "/api/documents/upload",
        files={"file": ("malicious_script.exe", b"echo 'hack'", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_empty_file():
    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty_statement.csv", b"", "text/csv")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_upload_oversized_file():
    # 26 MB dummy content
    oversized_data = b"0" * (26 * 1024 * 1024)
    response = client.post(
        "/api/documents/upload",
        files={"file": ("huge_statement.csv", oversized_data, "text/csv")}
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed limit" in response.json()["detail"]

def test_chat_empty_message():
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 200
    assert "valid financial query" in response.json()["reply"]

def test_transaction_invalid_category_update():
    # First load demo document to get a valid transaction ID
    demo_res = client.post("/api/documents/demo")
    assert demo_res.status_code == 200
    
    txs_res = client.get("/api/transactions")
    txs = txs_res.json()
    assert len(txs) > 0
    
    tx_id = txs[0]["id"]
    update_res = client.patch(
        f"/api/transactions/{tx_id}",
        json={"category": "Invalid_Fake_Category"}
    )
    assert update_res.status_code == 400
    assert "Invalid category" in update_res.json()["detail"]
