from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from .user import MemberLevel

@dataclass
class MemberLevelConfig:
    level: MemberLevel
    min_consumption: float
    base_discount: float
    description: str = ""
    benefits: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_config(self, min_consumption: float = None, base_discount: float = None, description: str = None, benefits: Dict = None) -> None:
        if min_consumption is not None:
            self.min_consumption = min_consumption
        if base_discount is not None:
            self.base_discount = base_discount
        if description is not None:
            self.description = description
        if benefits is not None:
            self.benefits.update(benefits)
        self.updated_at = datetime.now()

@dataclass
class MemberLevelManager:
    _configs: Dict[MemberLevel, MemberLevelConfig] = field(default_factory=dict)

    def __post_init__(self):
        self._init_default_configs()

    def _init_default_configs(self):
        self._configs[MemberLevel.REGULAR] = MemberLevelConfig(
            level=MemberLevel.REGULAR,
            min_consumption=0.0,
            base_discount=1.0,
            description="普通会员，注册即可获得",
            benefits={"points_rate": 1.0}
        )
        self._configs[MemberLevel.SILVER] = MemberLevelConfig(
            level=MemberLevel.SILVER,
            min_consumption=1000.0,
            base_discount=0.95,
            description="白银会员，累计消费满1000元",
            benefits={"points_rate": 1.2, "free_shipping": True}
        )
        self._configs[MemberLevel.GOLD] = MemberLevelConfig(
            level=MemberLevel.GOLD,
            min_consumption=5000.0,
            base_discount=0.9,
            description="黄金会员，累计消费满5000元",
            benefits={"points_rate": 1.5, "free_shipping": True, "birthday_gift": True}
        )
        self._configs[MemberLevel.DIAMOND] = MemberLevelConfig(
            level=MemberLevel.DIAMOND,
            min_consumption=20000.0,
            base_discount=0.8,
            description="钻石会员，累计消费满20000元",
            benefits={"points_rate": 2.0, "free_shipping": True, "birthday_gift": True, "exclusive_service": True}
        )

    def get_config(self, level: MemberLevel) -> MemberLevelConfig:
        return self._configs.get(level)

    def get_level_by_consumption(self, total_consumption: float) -> MemberLevel:
        levels = sorted(self._configs.values(), key=lambda x: x.min_consumption, reverse=True)
        for config in levels:
            if total_consumption >= config.min_consumption:
                return config.level
        return MemberLevel.REGULAR

    def update_level_config(self, level: MemberLevel, **kwargs) -> None:
        if level in self._configs:
            self._configs[level].update_config(**kwargs)

    def get_all_levels(self) -> Dict[MemberLevel, MemberLevelConfig]:
        return self._configs.copy()
