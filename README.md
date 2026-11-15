# Paytm Vasooli AI

> **Intelligent Merchant Operating System & Autonomous Indic AI Teammate for Paytm for Business.**
> *Paytm Hackathon (Track 3: AI Teammates in Sales & Customer Service)*

---

## 📌 Executive Summary

**Paytm Vasooli AI** is an enterprise-grade AI teammate built natively on top of the Paytm merchant ecosystem. Designed for Bharat's millions of retail merchants, it transforms transactional payment history into autonomous sales workflows, intelligent conversational bookkeeping, and automated cash-flow recovery.

Featuring **Vasooli AI**, an autonomous voice-first financial agent powered by Indic speech models (Sarvam AI) and cognitive reasoning (Claude via OpenRouter), Paytm Vasooli AI enables shopkeepers to manage their business hands-free in Hindi, Hinglish, Marathi, and English.

---

## 🚀 Key Modules & Architecture

```
web/          Next.js 16 (React 19, Tailwind CSS v4, Paytm Corporate Design System)
api/          FastAPI (Python 3.12, uv): Vasooli AI agent, Ledger engine, Paytm Gateways
supabase/     PostgreSQL 15 with Row Level Security (RLS), Realtime Pub/Sub, Storage
```

### 1. 🎙️ Vasooli AI (Voice Financial Co-Pilot)
- **Natural Indic Speech:** Zero-latency speech recognition and synthesis using Sarvam AI Saaras STT & Bulbul v3 TTS.
- **Cognitive Tool-Calling Loop:** Executes multi-turn ledger queries, cross-checks customer histories, and schedules collections.
- **Strict Number Guard:** Eliminates hallucinations by verifying all spoken and displayed figures against live transactional rows.
- **Action Confirmation Gate:** Sensitive actions (sending payment reminders, issuing invoices, scheduling recurring dues) require explicit merchant tap-to-confirm.

### 2. 💳 Paytm Dynamic Payment Links & Smart Invoicing
- **Instant Paytm Dynamic QR:** Generates custom Paytm UPI QR codes and dynamic payment links on the fly.
- **Webhook Integration & Checksum Validation:** Full SHA-256 HMAC signature verification with Paytm Gateway.
- **Automated Settlement Tracking:** Instant status updates via Supabase Realtime when invoices are paid.

### 3. 📞 Autonomous Voice Recovery (Sarvam Telephony)
- **Outbound Voice Recovery:** Dispatches automated Indic voice reminders to overdue buyers via Sarvam AI Voice Agents.
- **In-Call Payment Dispatch:** Sends Paytm payment links via SMS/Email while the customer is on the phone.
- **Promise-to-Pay Ledger:** Captures customer commitments and populates the dashboard's "Promised on Calls" tracker.

### 4. 📈 Merchant Growth & Working Capital Intelligence
- **Creditworthiness Scoring:** Analyzes 90-day UPI collection consistency (7,800+ transactions) to pre-approve instant working capital loans.
- **Customer Rhythm & Lapsed Regular Alerts:** Automatically flags regulars whose shopping rhythm has dropped.

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.12+ & `uv`
- Node.js 20+ & `npm`
- Supabase Project (PostgreSQL + Auth + Storage)

### 1. Environment Setup
Fill `.env` with your API keys:
```bash
cp .env.example .env
```
Key parameters:
- `OPENROUTER_API_KEY`: API key for model reasoning
- `SARVAM_API_KEY`: Sarvam AI speech key
- `SUPABASE_URL` & `DATABASE_URL`: Remote Supabase database credentials
- `PAYTM_MODE`: `mock` or `staging`

### 2. Database Migration & Seeding
```bash
# Seed Joshi Supermarket (Pune) demo history (40 customers, ~7,800 transactions)
cd api
uv run python -m app.seed
```

### 3. Launch Services
**Backend (FastAPI):**
```bash
cd api
uv run uvicorn app.main:app --port 8000 --reload
```

**Frontend (Next.js 16):**
```bash
cd web
npm run dev -- --port 3000
```

Open [http://localhost:3000](http://localhost:3000) and sign in:
- **Email:** `demo@paytmvyapaar.in`
- **Password:** `paytm-demo-2026`

---

## 🧪 Testing & Verification

```bash
# Run backend test suite
cd api && uv run pytest -q

# Run end-to-end browser suite
cd web && npx playwright test
```

---

## 🏆 Pune Merchant Demo Persona
- **Merchant:** Joshi Supermarket (FC Road, Shivaji Nagar, Pune)
- **MID:** `PTM00MOCK0000001`
- **Volume:** ₹7,50,000+ GMV over 90 days across 40 accounts
- **Assistant:** Vasooli AI ("वसूली AI")
