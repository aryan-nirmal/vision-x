"""
FastAPI Server for Paytm ResolveAI
Exposes REST endpoints defined in PRD_AND_API_CONTRACT.md.
"""
import uuid
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .mock_db import db
from .agent import agent_orchestrator
from .sarvam import sarvam

app = FastAPI(
    title="Paytm ResolveAI Backend",
    description="Autonomous, verifiable AI teammate for Paytm hackathon",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    customer_id: str
    message: str

class ApprovalActionRequest(BaseModel):
    action: str  # "APPROVE" or "REJECT"
    note: Optional[str] = "Supervisor review"

# --- Endpoints ---

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/", response_class=HTMLResponse)
@app.get("/demo", response_class=HTMLResponse)
def serve_demo_ui():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Paytm ResolveAI Backend Live</h1>", status_code=200)
    return HTMLResponse(content=index_file.read_text(), status_code=200)

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "sarvam_configured": bool(sarvam.api_key),
        "active_transactions": len(db.transactions),
        "pending_approvals": len([a for a in db.approvals if a.get("status") == "PENDING"])
    }

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    """
    Core customer conversation endpoint.
    Orchestrates Intent -> Investigate -> Policy -> Act -> Verify.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return agent_orchestrator.process_customer_message(req.customer_id, req.message)

@app.get("/api/approvals")
def list_approvals():
    """
    Retrieves high-risk or policy-gated tickets requiring human supervisor approval.
    """
    # Return pending approvals first, or all approvals
    return db.get_approvals()

@app.post("/api/approvals/{ticket_id}/action")
def take_approval_action(ticket_id: str, req: ApprovalActionRequest):
    """
    Human-in-the-Loop action endpoint.
    Supervisor can APPROVE or REJECT a pre-compiled case packet.
    """
    approval = db.get_approval(ticket_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval ticket not found")

    action_upper = req.action.upper()
    if action_upper not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE' or 'REJECT'")

    if action_upper == "APPROVE":
        txn_id = approval["evidence"]["transaction_id"]
        refund_utr = f"REF-BANK-{uuid.uuid4().hex[:6].upper()}"
        
        # Mutate database state
        db.update_transaction_refund(txn_id, refund_utr=refund_utr, refund_target="BANK_ACCOUNT")
        db.resolve_approval(ticket_id, action="APPROVE", note=req.note or "Approved by supervisor")

        return {
            "ticket_id": ticket_id,
            "status": "RESOLVED",
            "refund_utr": refund_utr,
            "message": f"Refund of ₹{int(approval['amount'])} to source bank executed and verified successfully."
        }
    else:
        db.resolve_approval(ticket_id, action="REJECT", note=req.note or "Rejected by supervisor")
        return {
            "ticket_id": ticket_id,
            "status": "REJECTED",
            "refund_utr": None,
            "message": f"Claim of ₹{int(approval['amount'])} rejected: {req.note}"
        }

@app.get("/api/transactions")
def list_transactions(customer_id: Optional[str] = None):
    """
    Returns live ledger state so frontend can show real-time state mutation.
    """
    if customer_id:
        return db.get_transactions_for_user(customer_id)
    return db.transactions

@app.get("/api/users")
def list_users():
    """
    Returns mock user accounts for the customer simulator dropdown.
    """
    return list(db.users.values())

@app.post("/api/reset")
def reset_database():
    """
    1-click reset endpoint for hackathon live judging demos.
    Restores all transactions and balances to initial seed state.
    """
    db.reset()
    return {
        "status": "RESET_SUCCESS",
        "message": "Mock database restored to initial seed state."
    }

