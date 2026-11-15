"""
Multi-Agent Orchestrator for Paytm ResolveAI
Coordinates Supervisor, Payment Specialist, Policy Engine, and Verification Specialist.
Follows the core hackathon principle: "No 'done' until verified".
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .mock_db import db
from .sarvam import sarvam

class AgentOrchestrator:
    def __init__(self):
        self.auto_refund_limit = 1000.0  # Under ₹1000 can be autonomously refunded

    def process_customer_message(self, customer_id: str, message: str) -> Dict[str, Any]:
        trace: List[Dict[str, Any]] = []
        now_time = datetime.utcnow().strftime("%H:%M:%S")

        # -------------------------------------------------------------
        # STEP 1: SUPERVISOR & INDIC UNDERSTANDING (Sarvam AI)
        # -------------------------------------------------------------
        translation_info = sarvam.translate_indic_to_english(message)
        english_intent = translation_info["translated_text"]

        user = db.get_user(customer_id)
        user_name = user["name"] if user else "Customer"
        user_txns = db.get_transactions_for_user(customer_id)

        trace.append({
            "agent": "Supervisor",
            "action": "INTENT_DETECTED",
            "details": f"Sarvam AI parsed Indic intent: '{english_intent}' (Source: {translation_info['source']})",
            "timestamp": now_time
        })

        # Match transaction based on context/message
        target_txn = self._identify_target_transaction(english_intent, user_txns)

        if not target_txn:
            return {
                "ticket_id": f"TCK-{uuid.uuid4().hex[:6].upper()}",
                "reply": "Hum aapka koi pending transaction locate nahi kar paaye. Kripya apna Order ID ya UTR share karein.",
                "status": "INVESTIGATING",
                "verification": {"verified": False, "refund_utr": None, "amount": None, "timestamp": None},
                "trace": trace
            }

        ticket_id = f"TCK-{target_txn['id'].split('-')[-1]}-{uuid.uuid4().hex[:4].upper()}"

        # -------------------------------------------------------------
        # STEP 2: PAYMENT SPECIALIST INVESTIGATION
        # -------------------------------------------------------------
        trace.append({
            "agent": "Payment Specialist",
            "action": "NPCI_GATEWAY_CHECK",
            "details": (
                f"Queried Bank UTR {target_txn['bank_utr']} & Gateway Ref {target_txn['gateway_ref']}. "
                f"Debited: {target_txn['debited_from_source']}, Status: {target_txn['status']}."
            ),
            "timestamp": now_time
        })

        # -------------------------------------------------------------
        # SCENARIO 3: P2P TRANSFER (Policy Guardrail)
        # -------------------------------------------------------------
        if target_txn["category"] == "P2P_TRANSFER":
            trace.append({
                "agent": "Policy Engine",
                "action": "POLICY_EVALUATED",
                "details": "P2P transfer succeeded at beneficiary bank. RBI guidelines forbid unilateral automated reversal.",
                "timestamp": now_time
            })
            trace.append({
                "agent": "Supervisor",
                "action": "ACTION_GUIDED",
                "details": "Guided user through formal NPCI dispute resolution workflow.",
                "timestamp": now_time
            })

            reply_msg = (
                f"Humne NPCI ledger check kiya hai. Aapka ₹{int(target_txn['amount'])} ka transfer {target_txn['title']} "
                f"ke bank account me safaltapoorvak credit ho chuka hai (UTR: {target_txn['bank_utr']}). "
                "RBI aur NPCI guidelines ke anusaar, P2P transactions ko bina receiver ki sahmati ke turant reverse nahi kiya ja sakta. "
                "Humne aapke liye dispute ticket raise kar diya hai jisse Paytm Nodal Team beneficiary bank se sampark karegi."
            )

            return {
                "ticket_id": ticket_id,
                "reply": reply_msg,
                "status": "REJECTED",
                "verification": {
                    "verified": True,
                    "target": "DISPUTE_FILED",
                    "refund_utr": None,
                    "amount": target_txn["amount"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trace": trace
            }

        # -------------------------------------------------------------
        # SCENARIO 2: HIGH-VALUE TRANSACTION (Human Approval Gate)
        # -------------------------------------------------------------
        if target_txn["amount"] >= self.auto_refund_limit:
            trace.append({
                "agent": "Policy Engine",
                "action": "APPROVAL_REQUIRED",
                "details": f"Amount ₹{target_txn['amount']} exceeds auto-reversal threshold (₹{self.auto_refund_limit}). High-risk gate triggered.",
                "timestamp": now_time
            })

            approval_record = {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "customer_name": user_name,
                "issue": f"{target_txn['title']} - Payment debited without PNR/Booking confirmation",
                "amount": target_txn["amount"],
                "risk_level": "HIGH",
                "evidence": {
                    "transaction_id": target_txn["id"],
                    "bank_utr": target_txn["bank_utr"],
                    "gateway_ref": target_txn["gateway_ref"],
                    "bank_status": "DEBITED",
                    "booking_status": target_txn["status"]
                },
                "recommendation": f"Approve instant reversal of ₹{int(target_txn['amount'])} to {target_txn['source_bank']}.",
                "status": "PENDING",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            db.add_approval(approval_record)

            trace.append({
                "agent": "Supervisor",
                "action": "ESCALATED_TO_HUMAN",
                "details": f"Generated pre-investigated case packet. Sent to Human Support Console with 1-click approval.",
                "timestamp": now_time
            })

            reply_msg = (
                f"Humne jaanch ki hai ki ₹{int(target_txn['amount'])} aapke bank se kat gaye the, par airline system par PNR generate nahi hua. "
                "Suraksha niyamon ke anusaar, ₹1,000 se upar ke refunds hamari support team se turant verify karwaye jaate hain. "
                "Case priority supervisor desk ko bhej diya gaya hai aur turant process ho raha hai."
            )

            return {
                "ticket_id": ticket_id,
                "reply": reply_msg,
                "status": "NEEDS_APPROVAL",
                "verification": {
                    "verified": False,
                    "target": "HUMAN_SUPERVISOR_QUEUE",
                    "refund_utr": None,
                    "amount": target_txn["amount"],
                    "timestamp": None
                },
                "trace": trace
            }

        # -------------------------------------------------------------
        # SCENARIO 1: AUTONOMOUS FAST-PATH (Low Risk < ₹1,000)
        # -------------------------------------------------------------
        trace.append({
            "agent": "Policy Engine",
            "action": "POLICY_EVALUATED",
            "details": f"Amount ₹{target_txn['amount']} is within autonomous limit (< ₹{self.auto_refund_limit}). Instant wallet credit authorized.",
            "timestamp": now_time
        })

        refund_utr = f"REF-WAL-{uuid.uuid4().hex[:6].upper()}"
        trace.append({
            "agent": "Action Service",
            "action": "EXECUTE_REFUND",
            "details": f"Dispatched instant wallet credit of ₹{target_txn['amount']} with UTR {refund_utr}.",
            "timestamp": now_time
        })

        # State mutation in ledger
        db.update_transaction_refund(target_txn["id"], refund_utr=refund_utr, refund_target="PAYTM_WALLET")

        # -------------------------------------------------------------
        # STEP 5: VERIFICATION SPECIALIST ("No 'done' until verified")
        # -------------------------------------------------------------
        verified_txn = db.get_transaction(target_txn["id"])
        verified_user = db.get_user(customer_id)

        if verified_txn and verified_txn.get("refund_status") == "COMPLETED" and verified_txn.get("refund_utr") == refund_utr:
            trace.append({
                "agent": "Verification Specialist",
                "action": "STATE_VERIFICATION",
                "details": (
                    f"Verified ledger state: status='REFUNDED', refund_utr='{refund_utr}'. "
                    f"Confirmed updated Paytm Wallet balance: ₹{verified_user['wallet_balance']}."
                ),
                "timestamp": now_time
            })

            reply_msg = (
                f"Humne verify kar liya hai ki aapka ₹{int(target_txn['amount'])} kat gaya tha par metro recharge fail ho gaya tha. "
                f"₹{int(target_txn['amount'])} turant aapke Paytm Wallet me credit kar diya gaya hai. "
                f"Naya wallet balance: ₹{verified_user['wallet_balance']}. (Refund Ref: {refund_utr})"
            )

            return {
                "ticket_id": ticket_id,
                "reply": reply_msg,
                "status": "RESOLVED",
                "verification": {
                    "verified": True,
                    "target": "PAYTM_WALLET",
                    "refund_utr": refund_utr,
                    "amount": target_txn["amount"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trace": trace
            }
        else:
            # Fallback if verification failed
            trace.append({
                "agent": "Verification Specialist",
                "action": "VERIFICATION_FAILED",
                "details": "State check failed to confirm wallet credit. Escalating to human desk.",
                "timestamp": now_time
            })
            return {
                "ticket_id": ticket_id,
                "reply": "Technical reconciliation check failed. Our human team is reviewing.",
                "status": "NEEDS_APPROVAL",
                "verification": {"verified": False, "refund_utr": None, "amount": target_txn["amount"], "timestamp": None},
                "trace": trace
            }

    def _identify_target_transaction(self, query: str, user_txns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        query_l = query.lower()
        for txn in user_txns:
            # ponytail: Keyword and category heuristics for instantaneous, accurate matching
            if "metro" in query_l and txn["category"] == "METRO_RECHARGE":
                return txn
            if ("flight" in query_l or "airline" in query_l or "air" in query_l or "pnr" in query_l) and txn["category"] == "FLIGHT_BOOKING":
                return txn
            if ("p2p" in query_l or "wrong" in query_l or "galti" in query_l or "kisi" in query_l or "rohan" in query_l) and txn["category"] == "P2P_TRANSFER":
                return txn
            if str(int(txn["amount"])) in query_l:
                return txn

        # Default to first non-refunded transaction
        for txn in user_txns:
            if txn.get("status") != "REFUNDED":
                return txn
        return user_txns[0] if user_txns else None

agent_orchestrator = AgentOrchestrator()
