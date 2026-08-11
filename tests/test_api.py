from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app_name"] == "FinBank AI"

def test_demo_endpoint():
    response = client.post("/api/documents/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["transaction_count"] > 0

def test_analytics_endpoint():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "assessment" in data

def test_transactions_endpoint():
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
