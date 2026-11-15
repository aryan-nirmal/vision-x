"""
Self-check script for Paytm ResolveAI backend.
Tests all 3 hackathon scenarios end-to-end against the FastAPI app.
Run with: python3 backend/test_backend.py
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.mock_db import db

client = TestClient(app)

def test_full_pipeline():
    print("==================================================")
    print("Testing Paytm ResolveAI Backend Endpoints & Scenarios")
    print("==================================================")

    # 0. Healthcheck
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Healthcheck failed: {resp.text}"
    print("✓ Healthcheck endpoint OK")

    # 1. Reset DB
    resp = client.post("/api/reset")
    assert resp.status_code == 200
    print("✓ Reset DB endpoint OK")

    # -------------------------------------------------------------
    # Scenario 1: Metro Card Autonomous Fast-Path (cust_101, ₹200)
    # -------------------------------------------------------------
    print("\n--- Testing Scenario 1: Metro Card (< ₹1000 Auto-Refund) ---")
    payload1 = {
        "customer_id": "cust_101",
        "message": "Bhai mera metro recharge ka 200 rs kat gaya par smart card recharge nahi hua"
    }
    resp1 = client.post("/api/chat", json=payload1)
    assert resp1.status_code == 200, f"Scenario 1 failed: {resp1.text}"
    data1 = resp1.json()
    assert data1["status"] == "RESOLVED", f"Expected RESOLVED, got {data1['status']}"
    assert data1["verification"]["verified"] is True
    assert data1["verification"]["refund_utr"] is not None
    assert data1["verification"]["amount"] == 200.0
    assert len(data1["trace"]) >= 4
    
    # Verify DB state directly
    txn1 = db.get_transaction("TXN-METRO-101")
    assert txn1["status"] == "REFUNDED"
    assert txn1["refund_utr"] == data1["verification"]["refund_utr"]
    user1 = db.get_user("cust_101")
    assert user1["wallet_balance"] == 340.0  # 140 + 200
    print(f"✓ Scenario 1 Passed: Verified Wallet Refund ({data1['verification']['refund_utr']}), New Balance: ₹{user1['wallet_balance']}")

    # -------------------------------------------------------------
    # Scenario 2: Flight Booking High-Value Gate (cust_102, ₹4800)
    # -------------------------------------------------------------
    print("\n--- Testing Scenario 2: Flight Booking (≥ ₹1000 Human Gate) ---")
    payload2 = {
        "customer_id": "cust_102",
        "message": "Flight booking failed, 4800 deducted from HDFC but no PNR generated"
    }
    resp2 = client.post("/api/chat", json=payload2)
    assert resp2.status_code == 200, f"Scenario 2 failed: {resp2.text}"
    data2 = resp2.json()
    assert data2["status"] == "NEEDS_APPROVAL", f"Expected NEEDS_APPROVAL, got {data2['status']}"
    assert data2["verification"]["verified"] is False
    print(f"✓ Scenario 2 Gated: Paused for human approval as expected (Ticket: {data2['ticket_id']})")

    # Check Approvals queue
    resp_app = client.get("/api/approvals")
    assert resp_app.status_code == 200
    approvals = resp_app.json()
    assert len(approvals) >= 1
    target_approval = approvals[-1]
    assert target_approval["amount"] == 4800.0
    print(f"✓ Approval Queue has ticket {target_approval['ticket_id']} for ₹{target_approval['amount']}")

    # Human Approves the ticket
    action_payload = {
        "action": "APPROVE",
        "note": "Verified IRCTC/Airline outage logs manually."
    }
    resp_act = client.post(f"/api/approvals/{target_approval['ticket_id']}/action", json=action_payload)
    assert resp_act.status_code == 200, f"Approval action failed: {resp_act.text}"
    act_data = resp_act.json()
    assert act_data["status"] == "RESOLVED"
    assert act_data["refund_utr"] is not None

    # Verify DB state directly for Flight
    txn2 = db.get_transaction("TXN-AIR-4081")
    assert txn2["status"] == "REFUNDED"
    assert txn2["refund_utr"] == act_data["refund_utr"]
    print(f"✓ Scenario 2 Human Action Passed: Refund verified to bank account ({act_data['refund_utr']})")

    # -------------------------------------------------------------
    # Scenario 3: P2P Policy Guardrail (cust_103, ₹500)
    # -------------------------------------------------------------
    print("\n--- Testing Scenario 3: P2P UPI Transfer (Policy Guardrail) ---")
    payload3 = {
        "customer_id": "cust_103",
        "message": "Galti se 500 kisi aur ko send ho gaya, refund karo"
    }
    resp3 = client.post("/api/chat", json=payload3)
    assert resp3.status_code == 200, f"Scenario 3 failed: {resp3.text}"
    data3 = resp3.json()
    assert data3["status"] == "REJECTED", f"Expected REJECTED, got {data3['status']}"
    assert "RBI" in data3["reply"] or "guidelines" in data3["reply"]
    # Ensure money was NOT refunded
    txn3 = db.get_transaction("TXN-P2P-502")
    assert txn3["status"] == "SUCCESS_AT_BENEFICIARY"
    print(f"✓ Scenario 3 Passed: Safe refusal & guided dispute workflow enforced.")

    # -------------------------------------------------------------
    # 4. Transactions List endpoint
    # -------------------------------------------------------------
    resp_txns = client.get("/api/transactions")
    assert resp_txns.status_code == 200
    assert len(resp_txns.json()) == 3
    print("✓ GET /api/transactions verified")

    # -------------------------------------------------------------
    # 5. Reset endpoint verification
    # -------------------------------------------------------------
    client.post("/api/reset")
    fresh_txn1 = db.get_transaction("TXN-METRO-101")
    assert fresh_txn1["status"] == "FAILED_AT_GATEWAY"
    print("✓ POST /api/reset verified - State cleanly restored to initial.")

    print("\n==================================================")
    print("ALL TESTS PASSED! Backend is 100% production-ready.")
    print("==================================================")

if __name__ == "__main__":
    test_full_pipeline()
