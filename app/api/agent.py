from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Transaction
from app.schemas.schemas import (
    AgentChatRequest, AgentChatResponse,
    AgentAuditResponse,
    SimulationRequest, SimulationResponse
)
from app.agent.agent_engine import FinancialAgentEngine

router = APIRouter()
agent_engine = FinancialAgentEngine()

def get_transaction_dicts(db: Session):
    db_txs = db.query(Transaction).all()
    return [
        {
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "merchant": t.merchant,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "category": t.category
        } for t in db_txs
    ]

@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(req: AgentChatRequest, db: Session = Depends(get_db)):
    user_msg = (req.message or "").strip()
    if not user_msg:
        return AgentChatResponse(
            reply="Please provide a valid financial goal or query.",
            execution_trace=[],
            tools_used=[]
        )

    safe_msg = user_msg[:500]
    dict_txs = get_transaction_dicts(db)
    history_dicts = [{"role": h.role, "content": h.content[:500]} for h in (req.history or [])[-6:]]

    res = await agent_engine.execute_agent_workflow(safe_msg, dict_txs, history_dicts)
    return AgentChatResponse(
        reply=res["reply"],
        execution_trace=res["execution_trace"],
        tools_used=res["tools_used"]
    )

@router.post("/audit", response_model=AgentAuditResponse)
async def agent_audit(db: Session = Depends(get_db)):
    dict_txs = get_transaction_dicts(db)
    res = agent_engine.run_financial_audit(dict_txs)
    return AgentAuditResponse(**res)

@router.post("/simulate", response_model=SimulationResponse)
async def agent_simulate(req: SimulationRequest, db: Session = Depends(get_db)):
    dict_txs = get_transaction_dicts(db)
    res = agent_engine.run_scenario_simulation(
        dict_txs,
        scenario_type=req.scenario_type,
        target_amount=req.target_amount if req.target_amount is not None else 0.0,
        time_frame_months=req.time_frame_months if req.time_frame_months is not None else 0,
        monthly_emi=req.monthly_emi if req.monthly_emi is not None else 0.0
    )
    return SimulationResponse(**res)
