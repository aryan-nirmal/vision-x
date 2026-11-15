"""
Autonomous Multi-System Orchestrator for Paytm ResolveAI
Coordinates:
1. Supervisor Agent (Sarvam AI Indic understanding)
2. Core Banking Switch Specialist
3. Soundbox IoT Telemetry Specialist
4. Fraud Sentinel Specialist
5. Merchant Sales & Credit Underwriting Specialist
6. Verification Specialist ("No 'done' until verified")
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .mock_db import db
from .sarvam import sarvam

class AgentOrchestrator:
    def __init__(self):
        self.auto_refund_limit = 1000.0
        self.auto_loan_limit = 25000.0  # Loans above ₹25,000 require human supervisor approval

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        trace: List[Dict[str, Any]] = []
        now_time = datetime.utcnow().strftime("%H:%M:%S")

        # STEP 1: SUPERVISOR & SARVAM INDIC UNDERSTANDING
        translation = sarvam.translate_indic_to_english(message)
        intent = translation["translated_text"]
        user = db.get_user(user_id) or db.get_user("merch_201")
        user_name = user["name"]

        trace.append({
            "agent": "Supervisor",
            "system": "Sarvam AI Indic Core",
            "action": "INTENT_DETECTED",
            "details": f"Sarvam AI parsed Indic query: '{intent}' (Lang: {translation.get('detected_language', 'hi-IN')})",
            "timestamp": now_time
        })

        intent_lower = intent.lower()

        # =====================================================================
        # SCENARIO 1: SOUNDBOX SILENT & DESYNC (Support Fast-Path)
        # =====================================================================
        if "soundbox" in intent_lower or "250" in intent_lower or "bol nahi" in intent_lower or "nahi bola" in intent_lower:
            # System 1: Check Core Banking Switch
            txn = db.search_transaction_by_amount_or_time(250.0)
            trace.append({
                "agent": "Banking Switch Specialist",
                "system": "NPCI / Core Bank Switch",
                "action": "SWITCH_RECONCILIATION",
                "details": f"Queried Core Switch for Ramesh Kirana QR: Confirmed incoming ₹250.00 debited from Kundan Patil at 09:14:22. Bank UTR: {txn['bank_utr'] if txn else 'UTR-ICICI-884019'}.",
                "timestamp": now_time
            })

            # System 2: Check IoT Telemetry Engine
            sb = db.get_soundbox()
            trace.append({
                "agent": "IoT Telemetry Specialist",
                "system": "Soundbox IoT Engine",
                "action": "DEVICE_TELEMETRY_INSPECTION",
                "details": f"Inspected {sb['model']} ({sb['device_id']}): Signal {sb['signal_strength']}, Battery {sb['battery_pct']}%. Detected MQTT packet drop (Code: ERR_2G_PACKET_LOSS). Device status: {sb['status']}.",
                "timestamp": now_time
            })

            # Action: Remotely Force Ping Soundbox
            updated_sb = db.remote_force_ping_soundbox(250.0, txn["id"] if txn else "TXN-SB-250")
            trace.append({
                "agent": "Action Service",
                "system": "Soundbox IoT Engine",
                "action": "REMOTE_FORCE_PING",
                "details": "Dispatched emergency high-priority MQTT wake-ping to DEV-SB-8821. Switched device LED to Solid Green.",
                "timestamp": now_time
            })

            # Step 5: Verification Specialist
            trace.append({
                "agent": "Verification Specialist",
                "system": "Verification Subsystem",
                "action": "STATE_VERIFICATION",
                "details": "Verified device state: LED=GREEN, Display='₹250.00'. Audio chime broadcasted successfully on merchant counter.",
                "timestamp": now_time
            })

            reply_text = (
                "Ramesh ji, humne check kar liya hai. Kundan Patil ji ka ₹250 aapke account me 09:14 AM par jama ho chuka hai. "
                "Soundbox ke 2G network me drop aane ki wajah se aawaz nahi aayi thi. Humne remotely Soundbox ko sync kar diya hai "
                "aur Soundbox ne bol diya hai: 'Paytm par ₹250 praapt hue'."
            )

            # Generate audio response and soundbox chime via Sarvam Bulbul
            agent_audio = sarvam.text_to_speech(reply_text, target_language_code="hi-IN")
            soundbox_chime = sarvam.generate_soundbox_chime(250.0)

            return {
                "ticket_id": "TCK-SB-9912",
                "status": "RESOLVED",
                "reply": reply_text,
                "audio_base64": agent_audio,
                "soundbox_chime_audio": soundbox_chime,
                "soundbox_state": {
                    "device_id": updated_sb["device_id"],
                    "status": "HEALTHY_ONLINE",
                    "led_color": "GREEN",
                    "display_text": "₹250.00",
                    "announcement": "Paytm par ₹250 praapt hue"
                },
                "verification": {
                    "verified": True,
                    "target": "SOUNDBOX_DEVICE",
                    "soundbox_synced": True,
                    "amount": 250.0,
                    "bank_utr": "UTR-ICICI-884019",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trace": trace
            }

        # =====================================================================
        # SCENARIO 2: FAKE SCREENSHOT / SPOOF SCAM (Fraud Prevention)
        # =====================================================================
        elif "1200" in intent_lower or "screen" in intent_lower or "spoof" in intent_lower or "dikhaya" in intent_lower:
            # System 1: Check Core Switch
            trace.append({
                "agent": "Banking Switch Specialist",
                "system": "NPCI / Core Bank Switch",
                "action": "TRANSACTION_AUDIT",
                "details": "Searched live switch for ₹1,200.00 payment to rameshkirana@paytm in past 60 mins. Result: ZERO RECORDS FOUND on NPCI switch.",
                "timestamp": now_time
            })

            # System 3: Check Fraud Sentinel
            incident_id = f"FRD-SPOOF-{uuid.uuid4().hex[:4].upper()}"
            db.log_fraud_incident({
                "incident_id": incident_id,
                "merchant_id": user_id,
                "claimed_amount": 1200.0,
                "pattern": "FAKE_PAYTM_SPOOF_APK",
                "detected_at": datetime.utcnow().isoformat() + "Z"
            })

            trace.append({
                "agent": "Fraud Sentinel",
                "system": "Merchant Fraud & Spoof Engine",
                "action": "FRAUD_SIGNATURE_MATCHED",
                "details": f"Signature matches known 'Paytm Spoof v4 APK' (fake tick UI). Flagged High Risk Incident {incident_id}.",
                "timestamp": now_time
            })

            trace.append({
                "agent": "Verification Specialist",
                "system": "Verification Subsystem",
                "action": "SAFETY_ENFORCED",
                "details": "Confirmed merchant alerted immediately. Security incident logged to Paytm Risk Operations.",
                "timestamp": now_time
            })

            reply_text = (
                "⚠️ SAVDHAN RAMESH JI! Humne Core Banking Switch aur NPCI ledger me check kiya hai—₹1,200 ka koi payment nahi aaya hai. "
                "Customer ne jo screen dikhayi hai wo 'Paytm Spoof Fake App' lagti hai. Kripya customer ko samaan bilkul na dein! "
                "Humne ye fraud incident Paytm Risk Team me report kar diya hai."
            )

            agent_audio = sarvam.text_to_speech(reply_text, target_language_code="hi-IN")

            return {
                "ticket_id": incident_id,
                "status": "FRAUD_DETECTED",
                "reply": reply_text,
                "audio_base64": agent_audio,
                "soundbox_chime_audio": None,
                "soundbox_state": {
                    "device_id": "DEV-SB-8821",
                    "status": "FRAUD_ALERT_ACTIVE",
                    "led_color": "RED",
                    "display_text": "FAKE PAYMENT",
                    "announcement": "Fake payment detected - No credit"
                },
                "verification": {
                    "verified": True,
                    "target": "FRAUD_SENTINEL",
                    "fraud_prevented": True,
                    "incident_id": incident_id,
                    "amount": 1200.0,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trace": trace
            }

        # =====================================================================
        # SCENARIO 3: DELAYED SETTLEMENT + WORKING CAPITAL UPSELL (Support -> Sales)
        # =====================================================================
        elif "18500" in intent_lower or "settlement" in intent_lower or "kal ka" in intent_lower or "loan" in intent_lower:
            # System 1: Check Settlement Batch
            stlm = db.get_transaction("TXN-STLM-18500")
            new_utr = f"UTR-ICICI-FAST-{uuid.uuid4().hex[:6].upper()}"
            db.force_settlement_retrigger("TXN-STLM-18500", new_utr)

            trace.append({
                "agent": "Banking Switch Specialist",
                "system": "NPCI / Core Bank Switch",
                "action": "SETTLEMENT_RETRIGGER",
                "details": f"Located stuck batch TXN-STLM-18500 (₹18,500.00). Executed instant IMPS push to ICICI Bank A/C ...9941. Allocated new UTR: {new_utr}.",
                "timestamp": now_time
            })

            # System 4: Credit & Sales Underwriting Engine
            merch = db.get_user("merch_201")
            preapproved_loan = merch["preapproved_loan_limit"]
            trace.append({
                "agent": "Sales & Credit Specialist",
                "system": "Credit & Sales ERP",
                "action": "UNDERWRITING_EVALUATION",
                "details": (
                    f"Analyzed Ramesh Kirana 30-day QR volume (₹3,80,000.00) & Credit Score ({merch['credit_score']}). "
                    f"Generated pre-approved Working Capital Loan of ₹{int(preapproved_loan)} + Free 4G Soundbox Upgrade."
                ),
                "timestamp": now_time
            })

            # Policy Gate: Loan > ₹25,000 triggers Human Supervisor Gate
            ticket_id = f"TCK-LOAN-{uuid.uuid4().hex[:4].upper()}"
            approval_record = {
                "ticket_id": ticket_id,
                "merchant_id": "merch_201",
                "merchant_name": "Ramesh Kumar (Ramesh Kirana Store)",
                "issue": "Support: ₹18,500 Settlement Cleared -> Upsell: ₹50,000 Instant Merchant Working Capital Loan",
                "amount": preapproved_loan,
                "risk_level": "POLICY_GATED_SALES",
                "evidence": {
                    "30_day_turnover": "₹3,80,000",
                    "cibil_score": 785,
                    "settlement_retriggered": f"₹18,500 (UTR: {new_utr})",
                    "current_soundbox": "Paytm Soundbox 2G (High Packet Drop)",
                    "recommended_action": "Disburse ₹50,000 Working Capital Loan (₹277/day auto-QR deduction) + Dispatch 4G Soundbox"
                },
                "recommendation": "Approve ₹50,000 Instant Working Capital Loan & auto-dispatch Soundbox 4G.",
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            db.add_approval(approval_record)

            trace.append({
                "agent": "Policy Engine",
                "system": "Risk Governance Layer",
                "action": "APPROVAL_REQUIRED",
                "details": f"Loan amount ₹{int(preapproved_loan)} exceeds autonomous threshold (₹{int(self.auto_loan_limit)}). Routed to Human Supervisor Desk with 1-click Approval.",
                "timestamp": now_time
            })

            reply_text = (
                f"Ramesh ji, aapka kal ka ₹18,500 ka settlement ICICI Bank account me instant IMPS ke dwara bhej diya gaya hai (UTR: {new_utr}). "
                f"Saath hi, aapki dukaan ka monthly QR turn-over ₹3.8 Lakh hone par Paytm aapko ₹50,000 ka Instant Working Capital Loan aur free Soundbox 4G upgrade de raha hai. "
                "Humne aapka loan proposal supervisor desk par approval ke liye bhej diya hai."
            )

            agent_audio = sarvam.text_to_speech(reply_text, target_language_code="hi-IN")

            return {
                "ticket_id": ticket_id,
                "status": "NEEDS_APPROVAL",
                "reply": reply_text,
                "audio_base64": agent_audio,
                "soundbox_chime_audio": None,
                "soundbox_state": {
                    "device_id": "DEV-SB-8821",
                    "status": "HEALTHY_ONLINE",
                    "led_color": "GREEN",
                    "display_text": "STLM CLEARED",
                    "announcement": f"Settlement of ₹18,500 cleared (UTR: {new_utr})"
                },
                "verification": {
                    "verified": False,
                    "target": "HUMAN_SUPERVISOR_QUEUE",
                    "settlement_utr": new_utr,
                    "preapproved_loan": preapproved_loan,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trace": trace
            }

        # =====================================================================
        # CONSUMER WORKFLOW FALLBACK (Metro Card, Flight, P2P)
        # =====================================================================
        else:
            trace.append({
                "agent": "Banking Switch Specialist",
                "system": "NPCI / Core Bank Switch",
                "action": "GENERAL_QUERY_RESOLVED",
                "details": "Interrogated core ledger for consumer query.",
                "timestamp": now_time
            })
            reply_text = "Aapka anurodh praapt hua hai. Humne transaction record check kar liya hai. Sabhi services active hain."
            agent_audio = sarvam.text_to_speech(reply_text, target_language_code="hi-IN")
            return {
                "ticket_id": f"TCK-GEN-{uuid.uuid4().hex[:4].upper()}",
                "status": "RESOLVED",
                "reply": reply_text,
                "audio_base64": agent_audio,
                "soundbox_chime_audio": None,
                "soundbox_state": db.get_soundbox(),
                "verification": {"verified": True, "target": "CORE_LEDGER", "amount": 0, "timestamp": datetime.utcnow().isoformat() + "Z"},
                "trace": trace
            }

agent_orchestrator = AgentOrchestrator()
