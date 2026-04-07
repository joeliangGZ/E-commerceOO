from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class PromotionStatus(Enum):
    DRAFT = "草稿"
    ACTIVE = "活跃"
    PAUSED = "暂停"
    ENDED = "已结束"

@dataclass
class Promotion:
    promotion_id: str
    name: str
    description: str
    theme_tags: List[str] = field(default_factory=list)
    start_time: datetime = None
    end_time: datetime = None
    status: PromotionStatus = PromotionStatus.DRAFT
    discount_rules: Dict = field(default_factory=dict)
    filter_conditions: Dict = field(default_factory=dict)
    target_user_ids: List[str] = field(default_factory=list)
    max_participants: Optional[int] = None
    current_participants: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    extra_info: Dict = field(default_factory=dict)

    def is_active(self) -> bool:
        now = datetime.now()
        return self.status == PromotionStatus.ACTIVE and \
               (self.start_time is None or now >= self.start_time) and \
               (self.end_time is None or now <= self.end_time)

    def can_participate(self, user_id: str) -> bool:
        if not self.is_active():
            return False
        if self.max_participants and self.current_participants >= self.max_participants:
            return False
        if self.target_user_ids and user_id not in self.target_user_ids:
            return False
        return True

    def add_theme_tag(self, tag: str) -> None:
        if tag not in self.theme_tags:
            self.theme_tags.append(tag)
            self.updated_at = datetime.now()

    def remove_theme_tag(self, tag: str) -> None:
        if tag in self.theme_tags:
            self.theme_tags.remove(tag)
            self.updated_at = datetime.now()

    def update_discount_rules(self, rules: Dict) -> None:
        self.discount_rules.update(rules)
        self.updated_at = datetime.now()

    def update_filter_conditions(self, conditions: Dict) -> None:
        self.filter_conditions.update(conditions)
        self.updated_at = datetime.now()

    def start(self) -> None:
        self.status = PromotionStatus.ACTIVE
        self.updated_at = datetime.now()

    def pause(self) -> None:
        self.status = PromotionStatus.PAUSED
        self.updated_at = datetime.now()

    def end(self) -> None:
        self.status = PromotionStatus.ENDED
        self.updated_at = datetime.now()
