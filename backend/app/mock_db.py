"""
Mock Paytm & Core Banking Ledger Database.
In-memory state management with fast reset for demo reliability.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import copy

INITIAL_USERS = {
    "cust_101": {
        "id": "cust_101",
        "name": "Aarav Sharma",
        "phone": "+91 98101 23456",
        "email": "aarav.sharma@example.com",
        "wallet_balance": 140.0,
        "primary_bank": "HDFC Bank (A/C ...8819)",
        "upi_id": "aarav@paytm"
    },
    "cust_102": {
        "id": "cust_102",
        "name": "Rahul Verma",
        "phone": "+91 98202 34567",
        "email": "rahul.verma@example.com",
        "wallet_balance": 520.0,
        "primary_bank": "HDFC Bank (A/C ...4102)",
        "upi_id": "rahulv@paytm"
    },
    "cust_103": {
        "id": "cust_103",
        "name": "Priya Patel",
        "phone": "+91 98303 45678",
        "email": "priya.patel@example.com",
        "wallet_balance": 1250.0,
        "primary_bank": "State Bank of India (A/C ...1190)",
        "upi_id": "priyap@paytm"
    }
}

INITIAL_TRANSACTIONS = [
    {
        "id": "TXN-METRO-101",
        "customer_id": "cust_101",
        "category": "METRO_RECHARGE",
        "title": "Delhi Metro Smart Card Recharge",
        "amount": 200.0,
        "currency": "INR",
        "status": "FAILED_AT_GATEWAY",  # Money deducted from bank, DMRC card not recharged
        "debited_from_source": True,
        "source_bank": "HDFC Bank (A/C ...8819)",
        "bank_utr": "UTR-HDFC-998212",
        "gateway_ref": "DMRC-GW-FAIL-88",
        "refund_status": "NONE",
        "refund_utr": None,
        "created_at": "2026-11-15T10:45:00Z",
        "updated_at": "2026-11-15T10:45:10Z"
    },
    {
        "id": "TXN-AIR-4081",
        "customer_id": "cust_102",
        "category": "FLIGHT_BOOKING",
        "title": "Paytm Travel: IndiGo DEL -> BLR",
        "amount": 4800.0,
        "currency": "INR",
        "status": "PNR_NOT_GENERATED",  # Payment captured, airline API failed to generate PNR
        "debited_from_source": True,
        "source_bank": "HDFC Bank (A/C ...4102)",
        "bank_utr": "UTR-HDFC-991204",
        "gateway_ref": "INDIGO-API-ERR-503",
        "refund_status": "NONE",
        "refund_utr": None,
        "created_at": "2026-11-15T10:15:00Z",
        "updated_at": "2026-11-15T10:15:30Z"
    },
    {
        "id": "TXN-P2P-502",
        "customer_id": "cust_103",
        "category": "P2P_TRANSFER",
        "title": "UPI to Rohan Verma (9876543210)",
        "amount": 500.0,
        "currency": "INR",
        "status": "SUCCESS_AT_BENEFICIARY",  # Completed transfer to valid recipient
        "debited_from_source": True,
        "source_bank": "State Bank of India (A/C ...1190)",
        "bank_utr": "UTR-SBI-330129",
        "gateway_ref": "NPCI-SETTLED-SUCCESS",
        "refund_status": "NOT_APPLICABLE",
        "refund_utr": None,
        "created_at": "2026-11-15T09:30:00Z",
        "updated_at": "2026-11-15T09:30:05Z"
    }
]

class MockDatabase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.users = copy.deepcopy(INITIAL_USERS)
        self.transactions = copy.deepcopy(INITIAL_TRANSACTIONS)
        self.approvals: List[Dict[str, Any]] = []
        self.audit_logs: List[Dict[str, Any]] = []

    def get_user(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(customer_id)

    def get_transactions_for_user(self, customer_id: str) -> List[Dict[str, Any]]:
        return [t for t in self.transactions if t["customer_id"] == customer_id]

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if t["id"] == txn_id:
                return t
        return None

    def update_transaction_refund(self, txn_id: str, refund_utr: str, refund_target: str = "PAYTM_WALLET") -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if t["id"] == txn_id:
                t["status"] = "REFUNDED"
                t["refund_status"] = "COMPLETED"
                t["refund_utr"] = refund_utr
                t["refund_target"] = refund_target
                t["updated_at"] = datetime.utcnow().isoformat() + "Z"
                
                # Credit wallet if target is wallet
                if refund_target == "PAYTM_WALLET" and t["customer_id"] in self.users:
                    self.users[t["customer_id"]]["wallet_balance"] += t["amount"]
                return t
        return None

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

