"""
Mock Paytm Multi-System Ledger & Subsystem Database.
Covers 4 Paytm Systems:
1. Core Banking / NPCI Switch
2. Soundbox IoT Telemetry Engine
3. Merchant Fraud & Spoof Engine
4. Merchant Credit & Sales ERP
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import copy

INITIAL_USERS = {
    "merch_201": {
        "id": "merch_201",
        "type": "MERCHANT",
        "name": "Ramesh Kumar",
        "business_name": "Ramesh Kirana Store, Pune",
        "phone": "+91 98220 11223",
        "merchant_vpa": "rameshkirana@paytm",
        "primary_bank": "ICICI Bank (A/C ...9941)",
        "settlement_balance": 18500.0,
        "monthly_turnover": 380000.0,
        "credit_score": 785,
        "preapproved_loan_limit": 50000.0,
        "soundbox_id": "DEV-SB-8821"
    },
    "cust_101": {
        "id": "cust_101",
        "type": "CONSUMER",
        "name": "Aarav Sharma",
        "phone": "+91 98101 23456",
        "wallet_balance": 140.0,
        "primary_bank": "HDFC Bank (A/C ...8819)",
        "upi_id": "aarav@paytm"
    },
    "cust_102": {
        "id": "cust_102",
        "type": "CONSUMER",
        "name": "Rahul Verma",
        "phone": "+91 98202 34567",
        "wallet_balance": 520.0,
        "primary_bank": "HDFC Bank (A/C ...4102)",
        "upi_id": "rahulv@paytm"
    }
}

INITIAL_SOUNDBOX = {
    "device_id": "DEV-SB-8821",
    "merchant_id": "merch_201",
    "model": "Paytm Soundbox 2G (Gen 2)",
    "status": "DESYNCED_BLINKING_RED",  # Red light due to 2G packet loss
    "led_color": "RED",  # RED, GREEN, or FLASHING_GREEN
    "battery_pct": 74,
    "signal_strength": "2G_WEAK (-102 dBm)",
    "firmware_version": "v2.4.1_b12",
    "last_ping_at": "2026-11-15T09:14:00Z",
    "display_text": "OFFLINE",
    "last_announcement": "Paytm par ₹50 praapt hue (08:45 AM)",
    "mqtt_packet_drop_count": 14,
    "last_action": "NONE"
}

INITIAL_TRANSACTIONS = [
    # Scenario 1: Customer paid ₹250, bank debited, but Soundbox missed MQTT packet
    {
        "id": "TXN-SB-250",
        "merchant_id": "merch_201",
        "customer_id": "cust_99",
        "category": "MERCHANT_QR_PAYMENT",
        "title": "UPI Payment from Kundan Patil",
        "amount": 250.0,
        "currency": "INR",
        "status": "SETTLED_ON_SWITCH",  # Money reached Paytm Switch successfully
        "soundbox_announced": False,    # Soundbox failed to announce due to 2G packet drop
        "bank_utr": "UTR-ICICI-884019",
        "gateway_ref": "NPCI-TXN-9940124",
        "created_at": "2026-11-15T09:14:22Z",
        "updated_at": "2026-11-15T09:14:25Z"
    },
    # Scenario 3: ₹18,500 daily settlement delayed at clearing house
    {
        "id": "TXN-STLM-18500",
        "merchant_id": "merch_201",
        "customer_id": "merch_201",
        "category": "SETTLEMENT_PAYOUT",
        "title": "Daily QR Settlement to ICICI Bank",
        "amount": 18500.0,
        "currency": "INR",
        "status": "BATCH_DELAYED_AT_NPCI",  # Delayed batch
        "bank_utr": "UTR-STLM-PENDING-01",
        "gateway_ref": "NPCI-BATCH-HLD-89",
        "created_at": "2026-11-15T06:00:00Z",
        "updated_at": "2026-11-15T09:00:00Z"
    },
    # Consumer reference transaction
    {
        "id": "TXN-METRO-101",
        "merchant_id": None,
        "customer_id": "cust_101",
        "category": "METRO_RECHARGE",
        "title": "Delhi Metro Smart Card Recharge",
        "amount": 200.0,
        "currency": "INR",
        "status": "FAILED_AT_GATEWAY",
        "bank_utr": "UTR-HDFC-998212",
        "gateway_ref": "DMRC-GW-FAIL-88",
        "created_at": "2026-11-15T10:45:00Z",
        "updated_at": "2026-11-15T10:45:10Z"
    }
]

INITIAL_FRAUD_DB = [
    {
        "known_spoof_pattern": "FAKE_PAYTM_SPOOF_APK",
        "description": "App generates client-side animated tick and sound without contacting bank switch",
        "flagged_utrs": ["FAKE-UTR-9999", "UTR-DUMMY-1234"]
    }
]

class MockDatabase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.users = copy.deepcopy(INITIAL_USERS)
        self.soundbox = copy.deepcopy(INITIAL_SOUNDBOX)
        self.transactions = copy.deepcopy(INITIAL_TRANSACTIONS)
        self.approvals: List[Dict[str, Any]] = []
        self.loans: List[Dict[str, Any]] = []
        self.hardware_orders: List[Dict[str, Any]] = []
        self.fraud_incidents: List[Dict[str, Any]] = []
        self.audit_logs: List[Dict[str, Any]] = []

    # --- Soundbox IoT Subsystem ---
    def get_soundbox(self) -> Dict[str, Any]:
        return self.soundbox

    def remote_force_ping_soundbox(self, amount: float, txn_id: str) -> Dict[str, Any]:
        """
        Simulates sending an MQTT force-push to the physical Soundbox.
        Updates LED to solid green, updates LCD display, and triggers audio chime.
        """
        self.soundbox["status"] = "HEALTHY_ONLINE"
        self.soundbox["led_color"] = "GREEN"
        self.soundbox["display_text"] = f"₹{int(amount)}.00"
        self.soundbox["last_announcement"] = f"Paytm par ₹{int(amount)} praapt hue (Force Pushed)"
        self.soundbox["last_ping_at"] = datetime.utcnow().isoformat() + "Z"
        self.soundbox["last_action"] = f"REMOTE_FORCE_PING_SUCCESS ({txn_id})"

        # Mark transaction as announced
        for t in self.transactions:
            if t["id"] == txn_id:
                t["soundbox_announced"] = True
                t["updated_at"] = datetime.utcnow().isoformat() + "Z"
        return self.soundbox

    # --- Core Banking / Settlement Subsystem ---
    def get_transactions(self) -> List[Dict[str, Any]]:
        return self.transactions

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if t["id"] == txn_id:
                return t
        return None

    def search_transaction_by_amount_or_time(self, amount: float) -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if abs(t["amount"] - amount) < 0.01:
                return t
        return None

    def force_settlement_retrigger(self, txn_id: str, new_utr: str) -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if t["id"] == txn_id:
                t["status"] = "SETTLED_TO_BANK"
                t["bank_utr"] = new_utr
                t["updated_at"] = datetime.utcnow().isoformat() + "Z"
                return t
        return None

    # --- Fraud Sentinel Subsystem ---
    def log_fraud_incident(self, incident: Dict[str, Any]):
        self.fraud_incidents.append(incident)

    def get_fraud_incidents(self) -> List[Dict[str, Any]]:
        return self.fraud_incidents

    # --- Credit & Sales Subsystem ---
    def disburse_loan(self, merchant_id: str, amount: float, tenure_months: int = 6) -> Dict[str, Any]:
        loan_record = {
            "loan_id": f"LOAN-PAYTM-{len(self.loans) + 1:04d}",
            "merchant_id": merchant_id,
            "amount": amount,
            "tenure_months": tenure_months,
            "interest_rate": "1.2% / month (Daily QR deduction)",
            "daily_deduction": round(amount / (tenure_months * 30), 2),
            "status": "DISBURSED",
            "disbursed_at": datetime.utcnow().isoformat() + "Z"
        }
        self.loans.append(loan_record)
        return loan_record

    def order_soundbox_upgrade(self, merchant_id: str, new_model: str = "Paytm Soundbox 4G with Dynamic QR") -> Dict[str, Any]:
        order = {
            "order_id": f"ORD-SB4G-{len(self.hardware_orders) + 1:04d}",
            "merchant_id": merchant_id,
            "product": new_model,
            "status": "DISPATCH_CONFIRMED",
            "eta_days": 2,
            "courier": "BlueDart Express",
            "tracking_no": "BD-PTM-991823"
        }
        self.hardware_orders.append(order)
        return order

    # --- User & Approval Management ---
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def add_approval(self, approval_data: Dict[str, Any]):
        self.approvals.append(approval_data)

    def get_approvals(self) -> List[Dict[str, Any]]:
        return self.approvals

    def get_approval(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        for a in self.approvals:
            if a["ticket_id"] == ticket_id:
                return a
        return None

    def resolve_approval(self, ticket_id: str, action: str, note: str) -> Optional[Dict[str, Any]]:
        for a in self.approvals:
            if a["ticket_id"] == ticket_id:
                a["status"] = "APPROVED" if action.upper() == "APPROVE" else "REJECTED"
                a["resolution_note"] = note
                a["resolved_at"] = datetime.utcnow().isoformat() + "Z"
                return a
        return None

# Singleton instance
db = MockDatabase()
