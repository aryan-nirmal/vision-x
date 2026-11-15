# Paytm ResolveAI — Multi-System Support & Sales AI Teammate

> **"A support reply is not the same as a resolution."**  
> Built for the **Paytm "Build for India" AI Hackathon (Pune)**.

Paytm ResolveAI is an autonomous, voice-enabled AI Teammate designed specifically around Paytm's most iconic and highest-volume asset: **The Paytm Soundbox & All-in-One Merchant QR Ecosystem**.

It independently handles customer service and merchant sales workflows end-to-end—investigating across 4 Paytm internal subsystems, taking verified actions, and escalating to humans only when policy gates are reached.

---

## 🌟 Live Demo Links
- **Public Mobile & Web Link (Cloudflare HTTPS)**: [https://mechanical-warning-supervisor-garden.trycloudflare.com](https://mechanical-warning-supervisor-garden.trycloudflare.com)
- **Local Address**: `http://localhost:8000`

*(Judges can scan the on-screen QR code from any phone and speak directly into their microphone!)*

---

## 🚀 The 4 Paytm Subsystems Orchestrated Live

1. **NPCI / Core Banking Switch**: Real-time UTR lookup, merchant settlement clearance, and balance reconciliation.
2. **Soundbox IoT Telemetry Engine**: Monitors SIM connectivity, MQTT broker packet health, and remotely force-pings hardware announcements.
3. **Merchant Fraud & Spoof Sentinel**: Cross-references claims against bank switches to detect and alert against fake "Paytm Spoof" APK scams.
4. **Credit Underwriting & Sales ERP**: Evaluates 30-day merchant QR turnover and provisions instant **Working Capital Loans** and **Soundbox 4G Upgrades**.

---

## 🎙️ Sarvam AI Deep Voice Integration (Zero Telecom Cost)

- **Sarvam Saaras v4 STT**: Transcribes spoken Indian dialects (Hindi, Hinglish, Marathi) directly from the browser mic.
- **Sarvam Bulbul v4-flash TTS**: Returns authentic Indian speech audio for both the AI support teammate and the iconic Paytm Soundbox chime (*"Paytm par ₹250 praapt hue"*).
- **100% In-App Web Audio**: No Twilio, no phone credits, and no SMS charges required.

---

## 🎬 The 3 Flagship Hackathon Scenarios

| Scenario | Input Query | Subsystems Invoked | Action & Outcome | Verification |
|---|---|---|---|---|
| **1. Soundbox Silent (Support Fast-Path)** | *"Customer bol raha hai 250 ka payment kar diya par soundbox nahi bola"* | Banking Switch + Soundbox IoT Engine | Diagnoses 2G packet loss on switch; executes remote MQTT force-ping. | Soundbox turns Green, LCD shows `₹250.00`, and plays voice chime. |
| **2. Fake Screenshot (Fraud Prevention)** | *"Bhaiya customer ne 1200 ka payment screen dikhaya, confirm karo"* | Banking Switch + Fraud Sentinel | Interrogates bank switch (0 records); flags `FAKE_PAYTM_SPOOF_APK` scam. | Merchant warned immediately; fraud alert logged to Paytm Risk Ops. |
| **3. Delayed Settlement & Loan Upsell (Support -> Sales)** | *"Kal ka 18500 ka settlement bank me kyu nahi aaya?"* | Banking Switch + Credit Underwriting ERP + Policy Gate | Re-triggers settlement (UTR assigned); analyzes ₹3.8L turnover; pitches ₹50,000 Working Capital Loan. | Pauses for Human Supervisor sign-off -> 1-click Approval disburses funds & orders Soundbox 4G. |

---

## 🛠️ Quickstart & Commands

```bash
# 1. Activate Environment
source .venv/bin/activate

# 2. Run Self-Check Test Suite (100% Automated Pass)
python backend/test_backend.py

# 3. Start Backend Server
python run_server.py

# 4. Start Cloudflare Public Tunnel for Judges
./start_public_tunnel.sh
```
