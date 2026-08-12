import pytest
from app.agent.agent_engine import FinancialAgentEngine

@pytest.fixture
def sample_transactions():
    return [
        {
            "id": "tx-1",
            "date": "2026-01-05",
            "description": "SALARY CREDIT",
            "merchant": "ACME CORP",
            "amount": 75000.0,
            "transaction_type": "income",
            "category": "Salary / Income"
        },
        {
            "id": "tx-2",
            "date": "2026-01-10",
            "description": "FLIPKART ONLINE",
            "merchant": "FLIPKART",
            "amount": 12000.0,
            "transaction_type": "expense",
            "category": "Shopping"
        },
        {
            "id": "tx-3",
            "date": "2026-01-15",
            "description": "SWIGGY FOOD ORDER",
            "merchant": "SWIGGY",
            "amount": 1500.0,
            "transaction_type": "expense",
            "category": "Food & Dining"
        },
        {
            "id": "tx-4",
            "date": "2026-02-15",
            "description": "SWIGGY FOOD ORDER",
            "merchant": "SWIGGY",
            "amount": 1500.0,
            "transaction_type": "expense",
            "category": "Food & Dining"
        },
        {
            "id": "tx-5",
            "date": "2026-01-20",
            "description": "NETFLIX RECURRING",
            "merchant": "NETFLIX",
            "amount": 649.0,
            "transaction_type": "expense",
            "category": "Entertainment"
        },
        {
            "id": "tx-6",
            "date": "2026-02-20",
            "description": "NETFLIX RECURRING",
            "merchant": "NETFLIX",
            "amount": 649.0,
            "transaction_type": "expense",
            "category": "Entertainment"
        }
    ]

def test_agent_tools_execution(sample_transactions):
    engine = FinancialAgentEngine()
    
    # Test metrics tool
    metrics = engine.tool_query_financial_metrics(sample_transactions)
    assert metrics["total_income"] == 75000.0
    assert metrics["total_expenses"] == 16298.0
    assert metrics["savings_rate"] > 0

    # Test recurring subscription tool
    subs = engine.tool_audit_recurring_subscriptions(sample_transactions)
    assert subs["recurring_count"] >= 1

    # Test anomalies tool
    anoms = engine.tool_detect_anomalies_and_spikes(sample_transactions)
    assert "total_anomalies" in anoms

def test_agent_autonomous_audit(sample_transactions):
    engine = FinancialAgentEngine()
    audit = engine.run_financial_audit(sample_transactions)

    assert "audit_score" in audit
    assert "risk_level" in audit
    assert "execution_trace" in audit
    assert len(audit["execution_trace"]) >= 4

    # Ensure ReAct actions are logged
    actions = [step["action"] for step in audit["execution_trace"]]
    assert "PLAN" in actions
    assert "TOOL_CALL" in actions
    assert "VERIFICATION" in actions
    assert "SYNTHESIS" in actions

def test_agent_scenario_simulation(sample_transactions):
    engine = FinancialAgentEngine()
    sim = engine.run_scenario_simulation(
        sample_transactions,
        scenario_type="emergency_fund",
        target_amount=30000.0,
        time_frame_months=6
    )

    assert "feasible" in sim
    assert "summary" in sim
    assert "execution_trace" in sim
    assert "recommended_cuts" in sim

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_api_endpoints():
    # Post chat request
    res = client.post("/api/agent/chat", json={"message": "Audit my recurring expenses"})
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "execution_trace" in data

    # Post audit request
    res_audit = client.post("/api/agent/audit")
    assert res_audit.status_code == 200
    data_audit = res_audit.json()
    assert "audit_score" in data_audit
    assert "risk_level" in data_audit

    # Post simulate request
    res_sim = client.post("/api/agent/simulate", json={"scenario_type": "emergency_fund", "target_amount": 50000})
    assert res_sim.status_code == 200
    data_sim = res_sim.json()
    assert "feasible" in data_sim

