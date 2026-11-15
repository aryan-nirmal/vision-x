# Paytm ResolveAI — PRD & API Contract

## 1. Product Summary
An autonomous, verifiable AI Teammate for Paytm customer support that:
1. **Investigates** across mock core systems (Bank UTR, NPCI, Paytm Wallet, Merchant).
2. **Acts** safely based on policy thresholds (< ₹1,000 auto-refund; ≥ ₹1,000 escalates to human).
3. **Verifies** database state before marking any ticket "DONE" ("No done until verified").
4. **Supports Indic Speech/Text** using Sarvam AI.

---

## 2. The 3 Demo Scenarios (Pre-seeded Data)

| Customer ID | Scenario | Pre-seeded Transaction | Expected Flow |
|---|---|---|---|
| `cust_101` | **1. Auto-Resolution** (Low Risk) | Metro Recharge: `₹200` (Status: `FAILED_AT_GATEWAY`, Debited: `YES`) | AI investigates → verifies failure → auto-refunds ₹200 to Paytm Wallet → DB verified → Done. |
| `cust_102` | **2. Human Approval Gate** (High Risk) | Flight Booking: `₹4,800` (Status: `PNR_NOT_GENERATED`, Debited: `YES`) | AI investigates → policy flag (>₹1,000) → pauses → creates approval card on Human Ops desk → Human clicks "Approve" → AI executes & verifies. |
| `cust_103` | **3. Policy Guardrail** (P2P Transfer) | P2P Transfer: `₹500` (Status: `SUCCESS_AT_BENEFICIARY`) | AI investigates → beneficiary bank confirmed receipt → explains RBI/P2P policy cannot auto-reverse → opens guided dispute. |

---

## 3. Strict API Contract

Backend runs at: `http://localhost:8000`

### A. Customer Chat Endpoint
`POST /api/chat`

**Request Body:**
```json
{
  "customer_id": "cust_101",
  "message": "Mera metro recharge ka 200 kat gaya par card recharge nahi hua"
}
```

**Response Body (200 OK):**
```json
{
  "ticket_id": "TCK-1001",
  "reply": "Humne check kiya hai ki aapka ₹200 kat gaya tha par metro gateway ne confirm nahi kiya. ₹200 aapke Paytm Wallet me turant refund kar diya gaya hai.",
  "status": "RESOLVED",
  "verification": {
    "verified": true,
    "target": "PAYTM_WALLET",
    "refund_utr": "REF-WAL-982143",
    "amount": 200,
    "timestamp": "2026-11-15T11:30:00Z"
  },
  "trace": [
    {
      "agent": "Supervisor",
      "action": "INTENT_DETECTED",
      "details": "Classified intent: METRO_RECHARGE_FAILED (Hinglish)",
      "timestamp": "11:30:01"
    },
    {
      "agent": "Payment Specialist",
      "action": "NPCI_GATEWAY_CHECK",
      "details": "Queried Bank UTR #UTR101. Money debited from user, gateway failed.",
      "timestamp": "11:30:02"
    },
    {
      "agent": "Policy Engine",
      "action": "POLICY_EVALUATED",
      "details": "Amount ₹200 is under ₹1,000 auto-threshold. Auto-refund permitted.",
      "timestamp": "11:30:02"
    },
    {
      "agent": "Action Service",
      "action": "EXECUTE_REFUND",
      "details": "Initiated instant wallet credit to cust_101.",
      "timestamp": "11:30:03"
    },
    {
      "agent": "Verification Specialist",
      "action": "STATE_VERIFICATION",
      "details": "Verified ledger state changed to REFUNDED. Balance confirmed +₹200.",
      "timestamp": "11:30:03"
    }
  ]
}
```

*Note on status enum:*
- `"RESOLVED"`: Completely resolved & verified.
- `"NEEDS_APPROVAL"`: Paused, sent to human supervisor desk.
- `"REJECTED"`: Policy denied (e.g. valid P2P transfer).

---

### B. Pending Approvals Endpoint (For Human Desk)
`GET /api/approvals`

**Response Body (200 OK):**
```json
[
  {
    "ticket_id": "TCK-1002",
    "customer_id": "cust_102",
    "customer_name": "Rahul Sharma",
    "issue": "Flight ticket payment debited without PNR",
    "amount": 4800,
    "risk_level": "HIGH",
    "evidence": {
      "transaction_id": "TXN-AIR-4081",
      "bank_utr": "UTR-HDFC-99120",
      "irctc_pnr": "NOT_GENERATED",
      "bank_status": "DEBITED"
    },
    "recommendation": "Approve instant reversal of ₹4,800 to HDFC Bank A/C ending in 4102.",
    "created_at": "2026-11-15T11:32:00Z"
  }
]
```

---

### C. Human Action on Approval
`POST /api/approvals/{ticket_id}/action`

**Request Body:**
```json
{
  "action": "APPROVE",
  "note": "Verified IRCTC failure log manually"
}
```
*(action can be `"APPROVE"` or `"REJECT"`)*

**Response Body (200 OK):**
```json
{
  "ticket_id": "TCK-1002",
  "status": "RESOLVED",
  "refund_utr": "REF-BANK-772910",
  "message": "Refund of ₹4,800 executed and verified successfully."
}
```

---

### D. Mock Transaction Inspector (Live DB State)
`GET /api/transactions`

**Response Body (200 OK):**
Returns the live mock database transactions so the frontend can display real-time updates when an agent updates the status from `FAILED` to `REFUNDED`.

```json
[
  {
    "id": "TXN-METRO-101",
    "customer_id": "cust_101",
    "title": "Delhi Metro Smart Card",
    "amount": 200,
    "status": "REFUNDED",
    "refund_utr": "REF-WAL-982143",
    "updated_at": "11:30:03"
  }
]
```

---

### E. Reset Database (For Demos)
`POST /api/reset`

**Response Body (200 OK):**
```json
{
  "status": "RESET_SUCCESS",
  "message": "Mock database restored to initial seed state."
}
```

