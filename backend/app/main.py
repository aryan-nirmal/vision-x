"""
FastAPI Server for Paytm ResolveAI
Multi-System Customer Service & Sales AI Teammate.
"""
import uuid
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .mock_db import db
from .agent import agent_orchestrator
from .sarvam import sarvam

app = FastAPI(
    title="Paytm ResolveAI Backend",
    description="Multi-System Support & Sales AI Teammate with Sarvam AI Voice & Soundbox IoT Engine",
    version="2.0.0"
)

# Enable CORS for local & public mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    user_id: Optional[str] = "merch_201"
    message: str

class VoiceCallRequest(BaseModel):
    user_id: Optional[str] = "merch_201"
    message: Optional[str] = None
    audio_base64: Optional[str] = None

class ApprovalActionRequest(BaseModel):
    action: str  # "APPROVE" or "REJECT"
    note: Optional[str] = "Approved by Operations Supervisor"

class SoundboxPingRequest(BaseModel):
    amount: float = 250.0

# --- Frontend Delivery ---
@app.get("/", response_class=HTMLResponse)
@app.get("/demo", response_class=HTMLResponse)
def serve_demo_ui():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Paytm ResolveAI Backend Running</h1>", status_code=200)
    return HTMLResponse(content=index_file.read_text(), status_code=200)

# --- Core AI Teammate Endpoints ---

@app.get("/api/health")
def health_check():
    sb = db.get_soundbox()
    return {
        "status": "HEALTHY",
        "sarvam_ai_configured": bool(sarvam.api_key),
        "soundbox_id": sb["device_id"],
        "soundbox_status": sb["status"],
        "pending_approvals": len([a for a in db.approvals if a.get("status") == "PENDING"]),
        "fraud_incidents_count": len(db.fraud_incidents)
    }

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    """
    Text-based query endpoint.
    Orchestrates Intent -> Multi-System Investigation -> Action -> Verification.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return agent_orchestrator.process_message(req.user_id or "merch_201", req.message)

@app.post("/api/voice/call")
def handle_voice_call(req: VoiceCallRequest):
    """
    In-App Web Voice Call Hotline (0120-4440440).
    Processes browser audio or text, executes across all 4 systems,
    and returns text + Sarvam Bulbul voice audio + Soundbox chime.
    """
    query_text = req.message or ""

    # If audio_base64 is sent, transcribe using Sarvam Saaras STT
    if req.audio_base64 and not query_text:
        try:
            audio_bytes = base64.b64decode(req.audio_base64.split(",")[-1])
            stt_res = sarvam.transcribe_audio(audio_bytes)
            query_text = stt_res.get("transcript", "")
        except Exception as e:
            query_text = "Mera 250 ka payment soundbox me nahi bola"

    if not query_text.strip():
        query_text = "Mera 250 ka payment soundbox me nahi bola"

    # Process through multi-agent orchestrator
    result = agent_orchestrator.process_message(req.user_id or "merch_201", query_text)
    result["input_transcript"] = query_text
    return result

# --- Soundbox IoT Hardware Endpoints ---

@app.get("/api/soundbox/status")
def get_soundbox_status():
    """Returns live telemetry for the interactive physical Soundbox simulator widget."""
    return db.get_soundbox()

@app.post("/api/soundbox/ping")
def test_soundbox_ping(req: SoundboxPingRequest):
    """Manually test remote MQTT ping & Paytm audio chime on Soundbox."""
    updated = db.remote_force_ping_soundbox(req.amount, "MANUAL-TEST-PING")
    chime_audio = sarvam.generate_soundbox_chime(req.amount)
    return {
        "status": "PING_DELIVERED",
        "soundbox": updated,
        "chime_audio": chime_audio
    }

# --- Human Supervisor Desk Endpoints ---

@app.get("/api/approvals")
def list_approvals():
    """Returns tickets paused for human supervisor authorization."""
    return db.get_approvals()

@app.post("/api/approvals/{ticket_id}/action")
def take_approval_action(ticket_id: str, req: ApprovalActionRequest):
    """
    Human supervisor signs off on high-value actions (e.g. ₹50,000 Working Capital Loan).
    """
    approval = db.get_approval(ticket_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval ticket not found")

    action_upper = req.action.upper()
    if action_upper not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE' or 'REJECT'")

    if action_upper == "APPROVE":
        merchant_id = approval.get("merchant_id", "merch_201")
        amount = approval.get("amount", 50000.0)
        
        # Disburse loan & dispatch 4G Soundbox upgrade
        loan = db.disburse_loan(merchant_id, amount)
        order = db.order_soundbox_upgrade(merchant_id)
        db.resolve_approval(ticket_id, action="APPROVE", note=req.note or "Approved by Supervisor")

        return {
            "ticket_id": ticket_id,
            "status": "APPROVED_AND_DISBURSED",
            "loan": loan,
            "hardware_order": order,
            "message": f"Successfully approved & disbursed ₹{int(amount)} Working Capital Loan to {approval.get('merchant_name')}! 4G Soundbox dispatch confirmed."
        }
    else:
        db.resolve_approval(ticket_id, action="REJECT", note=req.note or "Rejected by Supervisor")
        return {
            "ticket_id": ticket_id,
            "status": "REJECTED",
            "message": f"Ticket {ticket_id} rejected by supervisor."
        }

# --- 4-System State Inspector Endpoint ---

@app.get("/api/systems/state")
def get_systems_state():
    """
    Returns real-time state across all 4 Paytm internal subsystems:
    1. Core Bank Switch, 2. Soundbox IoT Engine, 3. Fraud Sentinel, 4. Credit/Sales ERP
    """
    return {
        "system_1_core_switch": {
            "name": "NPCI & Core Banking Switch",
            "transactions_count": len(db.transactions),
            "transactions": db.transactions
        },
        "system_2_iot_engine": {
            "name": "Soundbox IoT Telemetry Engine",
            "soundbox": db.get_soundbox()
        },
        "system_3_fraud_sentinel": {
            "name": "Merchant Fraud & Spoof Engine",
            "incidents_count": len(db.fraud_incidents),
            "incidents": db.fraud_incidents
        },
        "system_4_credit_sales_erp": {
            "name": "Credit Underwriting & Sales ERP",
            "loans_disbursed": db.loans,
            "hardware_orders": db.hardware_orders
        }
    }

# --- Reset Endpoint for Demos ---

@app.post("/api/reset")
def reset_database():
    """1-click reset for hackathon demos. Restores all 4 systems to initial state."""
    db.reset()
    return {
        "status": "RESET_SUCCESS",
        "message": "All 4 Paytm mock subsystems restored to initial seed state."
    }
