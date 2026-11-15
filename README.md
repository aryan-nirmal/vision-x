# Paytm ResolveAI — Autonomous Support Teammate

> **"A support reply is not the same as a resolution."**  
> Built for the Paytm "Build for India" AI Hackathon (Pune).

Paytm ResolveAI is an autonomous, verifiable AI Teammate for customer support that investigates issues across core banking and Paytm systems, takes policy-gated safe actions, and verifies state changes before marking tickets done.

---

## 1. Quickstart (Backend)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run backend server (Listens on http://0.0.0.0:8000)
python run_server.py

# 3. Run self-check tests (Tests all 3 hackathon scenarios)
python backend/test_backend.py
```

---

## 2. Architecture & Documentation
- [PRD & API Contract](PRD_AND_API_CONTRACT.md): The locked schema and scenarios for Frontend/Backend coordination.

---

## 3. Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Customer chat (Intent -> Investigate -> Gate -> Act -> Verify) |
| `GET` | `/api/approvals` | Human supervisor queue for high-risk tickets (e.g. Flight ₹4,800) |
| `POST` | `/api/approvals/{id}/action` | 1-click human approval or rejection |
| `GET` | `/api/transactions` | Live ledger state for real-time frontend verification |
| `GET` | `/api/users` | Customer profiles for simulator dropdown |
| `POST` | `/api/reset` | 1-click demo state reset for live judging |
| `GET` | `/api/health` | Healthcheck & Sarvam AI configuration status |
