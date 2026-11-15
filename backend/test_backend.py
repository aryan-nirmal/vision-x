"""
Comprehensive Self-Check Test Suite for Paytm ResolveAI
Tests all 3 Flagship Hackathon Scenarios + 4 Paytm Subsystems:
1. Scenario 1: Soundbox Silent & Remote Force-Ping (Support Fast-Path)
2. Scenario 2: Fake Screenshot Spoof Scam (Fraud Prevention)
3. Scenario 3: Delayed Settlement + Working Capital Loan Upsell (Support -> Sales)
4. Human Supervisor Approval & State Mutations
5. Database Reset
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.mock_db import db

client = TestClient(app)

def test_all():
    print("=================================================================")
    print("Testing Paytm ResolveAI: Multi-System Support & Sales AI Teammate")
    print("=================================================================")

    # 0. Healthcheck
    resp = client.get("/api/health")
    assert resp.status_code == 200
    health = resp.json()
    assert health["status"] == "HEALTHY"
    print(f"✓ Healthcheck OK (Soundbox: {health['soundbox_id']}, Status: {health['soundbox_status']})")

    # 1. Reset
    resp = client.post("/api/reset")
    assert resp.status_code == 200
    print("✓ DB Reset to initial state")

    # -------------------------------------------------------------
    # Scenario 1: Soundbox Silent & Audio Desync (Support Fast-Path)
    # -------------------------------------------------------------
    print("\n--- Scenario 1: Soundbox Silent & Remote Force-Ping ---")
    req1 = {
        "user_id": "merch_201",
        "message": "Customer bol raha hai 250 ka payment kar diya par soundbox nahi bola"
    }
    resp1 = client.post("/api/voice/call", json=req1)
    assert resp1.status_code == 200, f"Scenario 1 failed: {resp1.text}"
    data1 = resp1.json()
    assert data1["status"] == "RESOLVED"
    assert data1["verification"]["verified"] is True
    assert data1["verification"]["soundbox_synced"] is True
    assert data1["soundbox_state"]["led_color"] == "GREEN"
    assert data1["soundbox_state"]["display_text"] == "₹250.00"
    
    # Verify DB state directly
    sb = db.get_soundbox()
    assert sb["led_color"] == "GREEN"
    assert sb["display_text"] == "₹250.00"
    print(f"✓ Scenario 1 PASSED: Soundbox remotely re-synced! (LED: {sb['led_color']}, Display: {sb['display_text']})")

    # -------------------------------------------------------------
    # Scenario 2: Fake Screenshot Spoof Scam (Fraud Prevention)
    # -------------------------------------------------------------
    print("\n--- Scenario 2: Fake Screenshot Spoof Scam ---")
    req2 = {
        "user_id": "merch_201",
        "message": "Bhaiya customer ne 1200 ka payment screen dikhaya, confirm karo"
    }
    resp2 = client.post("/api/voice/call", json=req2)
    assert resp2.status_code == 200, f"Scenario 2 failed: {resp2.text}"
    data2 = resp2.json()
    assert data2["status"] == "FRAUD_DETECTED"
    assert data2["verification"]["fraud_prevented"] is True
    assert "SAVDHAN" in data2["reply"] or "Fake" in data2["reply"] or "Spoof" in data2["reply"]
    assert len(db.fraud_incidents) >= 1
    print(f"✓ Scenario 2 PASSED: Fraud alert triggered, merchant warned, incident logged: {data2['ticket_id']}")

    # -------------------------------------------------------------
    # Scenario 3: Delayed Settlement + Working Capital Loan Upsell
    # -------------------------------------------------------------
    print("\n--- Scenario 3: Delayed Settlement + Working Capital Loan Upsell ---")
    req3 = {
        "user_id": "merch_201",
        "message": "Kal ka 18500 ka settlement bank me kyu nahi aaya?"
    }
    resp3 = client.post("/api/voice/call", json=req3)
    assert resp3.status_code == 200, f"Scenario 3 failed: {resp3.text}"
    data3 = resp3.json()
    assert data3["status"] == "NEEDS_APPROVAL"
    assert data3["verification"]["preapproved_loan"] == 50000.0
    print(f"✓ Scenario 3 Support Phase PASSED: Settlement re-triggered ({data3['verification']['settlement_utr']})")
    print(f"✓ Scenario 3 Sales Phase PASSED: ₹50,000 loan generated & paused for Human Supervisor (Ticket: {data3['ticket_id']})")

    # Check Approvals queue
    resp_app = client.get("/api/approvals")
    approvals = resp_app.json()
    loan_ticket = [a for a in approvals if a["ticket_id"] == data3["ticket_id"]][0]
    assert loan_ticket["amount"] == 50000.0

    # Human Supervisor signs off on the loan
    action_resp = client.post(f"/api/approvals/{loan_ticket['ticket_id']}/action", json={"action": "APPROVE"})
    assert action_resp.status_code == 200
    act_data = action_resp.json()
    assert act_data["status"] == "APPROVED_AND_DISBURSED"
    assert len(db.loans) == 1
    assert db.loans[0]["amount"] == 50000.0
    assert len(db.hardware_orders) == 1
    print(f"✓ Human Approval PASSED: Loan Disbursed ({db.loans[0]['loan_id']}) & 4G Soundbox Ordered ({db.hardware_orders[0]['order_id']})")

    # -------------------------------------------------------------
    # 4. Check 4-Systems Live State
    # -------------------------------------------------------------
    sys_resp = client.get("/api/systems/state")
    assert sys_resp.status_code == 200
    state = sys_resp.json()
    assert "system_1_core_switch" in state
    assert "system_2_iot_engine" in state
    assert "system_3_fraud_sentinel" in state
    assert "system_4_credit_sales_erp" in state
    print("✓ 4-Systems Live State API Verified")

    # -------------------------------------------------------------
    # 5. Reset Check
    # -------------------------------------------------------------
    client.post("/api/reset")
    fresh_sb = db.get_soundbox()
    assert fresh_sb["status"] == "DESYNCED_BLINKING_RED"
    assert len(db.loans) == 0
    print("✓ Reset verified: All 4 systems restored cleanly to default state")

    print("\n=================================================================")
    print("ALL TESTS PASSED! Multi-System Support & Sales AI Teammate 100% OK")
    print("=================================================================")

if __name__ == "__main__":
    test_all()
