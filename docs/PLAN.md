# Paytm Vyapaar AI — Build Plan

Build contract: `docs/ARCHITECTURE.md`, `docs/paytm/PAYTM_INTEGRATION.md`.

## Milestones

- [x] **M1 Schema + seed**: migrations (tables, `app_now()`, views, RLS, realtime publication, storage bucket), seed script (Joshi Supermarket (Pune), 40 payers, 90 days, ~7,800 rows, Ram, Sharma Traders, lapsed regular, open invoices), demo merchant login.
- [x] **M2 Ledger API**: JWT auth → merchant, `GET /dashboard/summary`, payers search/profile/patch/merge, `PATCH /transactions/{id}`, transactions list.
- [x] **M3 Dashboard UI**: login, dashboard (KPIs, trend, peak hours, slow-day banner, lost-regular alerts, search), customer list + payer profile, edit description, merge.
- [x] **M4 Invoices + Paytm Gateways + webhook**: `PaytmClient` (Mock/Real), checksum validation, invoices API, QR generation, `/mock-pay`, webhooks (verify, dedupe, match, mark paid), realtime flip in UI.
- [x] **M5 Recurring + clock**: recurring schedules, `/jobs/tick` (dues, overdue reminders, status polling, AI descriptions, alerts), `/admin/clock`, demo clock UI.
- [x] **M6 Voice agent**: typed tools, Claude tool loop (Haiku → Sonnet retry), number guard, components, pending actions + confirm, Sarvam STT/TTS, Vyapaar Mitra UI with push-to-talk and text fallback.
- [x] **M7 Polish**: Paytm corporate tokens (#002E6E, #00BAF2), Joshi Supermarket (Pune) branding, working capital analytics.
