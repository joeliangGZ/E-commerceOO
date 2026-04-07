from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class MemberLevel(Enum):
    REGULAR = "普通会员"
    SILVER = "白银会员"
    GOLD = "黄金会员"
    DIAMOND = "钻石会员"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    phone: str
    member_level: MemberLevel = MemberLevel.REGULAR
    total_consumption: float = 0.0
    purchase_count: int = 0
    last_purchase_date: Optional[datetime] = None
    shopping_preferences: List[str] = field(default_factory=list)
    purchase_frequency: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    extra_info: Dict = field(default_factory=dict)

    def update_consumption(self, amount: float) -> None:
        self.total_consumption += amount
        self.purchase_count += 1
        self.last_purchase_date = datetime.now()
        self._calculate_purchase_frequency()
        self.updated_at = datetime.now()

    def _calculate_purchase_frequency(self) -> None:
        if self.created_at and self.purchase_count > 0:
            days_since_creation = (datetime.now() - self.created_at).days
            if days_since_creation > 0:
                self.purchase_frequency = self.purchase_count / (days_since_creation / 30)

    def add_preference(self, category: str) -> None:
        if category not in self.shopping_preferences:
            self.shopping_preferences.append(category)
            self.updated_at = datetime.now()

    def remove_preference(self, category: str) -> None:
        if category in self.shopping_preferences:
            self.shopping_preferences.remove(category)
            self.updated_at = datetime.now()
