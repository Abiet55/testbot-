from typing import Dict, List, Any
from datetime import datetime

class Storage:
    def __init__(self):
        self.orders: Dict[str, Dict] = {}
        self.feedback: List[Dict] = []
        self.user_sessions: Dict[int, Dict] = {}

    def create_order(self, user_id: int, service: str) -> str:
        order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        self.orders[order_id] = {
            "user_id": user_id,
            "service": service,
            "status": "pending",
            "payment_status": None,
            "payment_method": None,
            "created_at": datetime.now()
        }
        return order_id

    def get_order(self, order_id: str) -> Dict:
        return self.orders.get(order_id, {})

    def update_order_status(self, order_id: str, status: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            return True
        return False

    def update_payment_method(self, order_id: str, payment_method: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]["payment_method"] = payment_method
            self.orders[order_id]["payment_status"] = "pending"
            return True
        return False

    def get_user_orders(self, user_id: int) -> Dict[str, Dict]:
        return {k: v for k, v in self.orders.items() if v["user_id"] == user_id}

    def get_user_pending_orders(self, user_id: int) -> Dict[str, Dict]:
        return {k: v for k, v in self.orders.items() if v["user_id"] == user_id and v["status"] == "pending"}

    def add_feedback(self, user_id: int, feedback_text: str) -> int:
        feedback_id = len(self.feedback)
        self.feedback.append({
            "id": feedback_id,
            "user_id": user_id,
            "text": feedback_text,
            "status": "pending",
            "created_at": datetime.now()
        })
        return feedback_id

    def get_pending_feedback(self) -> List[Dict]:
        return [f for f in self.feedback if f["status"] == "pending"]

    def update_feedback_status(self, feedback_id: int, status: str) -> bool:
        if 0 <= feedback_id < len(self.feedback):
            self.feedback[feedback_id]["status"] = status
            return True
        return False

    def set_user_session(self, user_id: int, key: str, value: Any) -> None:
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id][key] = value

    def get_user_session(self, user_id: int, key: str) -> Any:
        return self.user_sessions.get(user_id, {}).get(key)

    def clear_user_session(self, user_id: int) -> None:
        self.user_sessions.pop(user_id, None)