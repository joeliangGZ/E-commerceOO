from abc import ABC, abstractmethod
from typing import List, Dict, Callable
from ..models.user import User, MemberLevel
from ..models.promotion import Promotion

class FilterStrategy(ABC):
    @abstractmethod
    def filter(self, users: List[User], condition: Dict) -> List[User]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

class PreferenceFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "preference"

    @property
    def description(self) -> str:
        return "基于购物偏好筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        required_preferences = condition.get("preferences", [])
        match_all = condition.get("match_all", False)
        
        if not required_preferences:
            return users
        
        result = []
        for user in users:
            user_prefs = set(p.lower() for p in user.shopping_preferences)
            required_prefs = set(p.lower() for p in required_preferences)
            
            if match_all:
                if required_prefs.issubset(user_prefs):
                    result.append(user)
            else:
                if required_prefs & user_prefs:
                    result.append(user)
        return result

class PurchaseFrequencyFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "purchase_frequency"

    @property
    def description(self) -> str:
        return "基于购买频率筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        min_frequency = condition.get("min", 0)
        max_frequency = condition.get("max", float('inf'))
        return [
            user for user in users
            if min_frequency <= user.purchase_frequency <= max_frequency
        ]

class MemberLevelFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "member_level"

    @property
    def description(self) -> str:
        return "基于会员等级筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        allowed_levels = condition.get("levels", [])
        if not allowed_levels:
            return users
        
        allowed_level_values = [level.value for level in allowed_levels]
        return [
            user for user in users
            if user.member_level.value in allowed_level_values
        ]

class ConsumptionFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "consumption"

    @property
    def description(self) -> str:
        return "基于累计消费金额筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        min_amount = condition.get("min", 0)
        max_amount = condition.get("max", float('inf'))
        return [
            user for user in users
            if min_amount <= user.total_consumption <= max_amount
        ]

class PurchaseCountFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "purchase_count"

    @property
    def description(self) -> str:
        return "基于购买次数筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        min_count = condition.get("min", 0)
        max_count = condition.get("max", float('inf'))
        return [
            user for user in users
            if min_count <= user.purchase_count <= max_count
        ]

class LastPurchaseFilterStrategy(FilterStrategy):
    @property
    def name(self) -> str:
        return "last_purchase"

    @property
    def description(self) -> str:
        return "基于最后购买时间筛选"

    def filter(self, users: List[User], condition: Dict) -> List[User]:
        from datetime import datetime, timedelta
        days = condition.get("days", 30)
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            user for user in users
            if user.last_purchase_date and user.last_purchase_date >= cutoff_date
        ]

class FilterCombiner:
    def __init__(self):
        self._strategies: Dict[str, FilterStrategy] = {}

    def register_strategy(self, strategy: FilterStrategy) -> None:
        self._strategies[strategy.name] = strategy

    def remove_strategy(self, strategy_name: str) -> bool:
        if strategy_name in self._strategies:
            del self._strategies[strategy_name]
            return True
        return False

    def apply_filters(self, users: List[User], filter_conditions: Dict, operator: str = "AND") -> List[User]:
        if not filter_conditions:
            return users
        
        result = users.copy()
        for strategy_name, condition in filter_conditions.items():
            if strategy_name not in self._strategies:
                continue
            
            strategy = self._strategies[strategy_name]
            filtered = strategy.filter(result, condition)
            
            if operator == "AND":
                result = filtered
            elif operator == "OR":
                result = list({user.user_id: user for user in result + filtered}.values())
        
        return result

    def get_strategies_info(self) -> List[Dict]:
        return [
            {
                "name": strategy.name,
                "description": strategy.description
            }
            for strategy in self._strategies.values()
        ]

class UserFilterService:
    def __init__(self):
        self.filter_combiner = FilterCombiner()
        self._init_default_strategies()

    def _init_default_strategies(self) -> None:
        self.filter_combiner.register_strategy(PreferenceFilterStrategy())
        self.filter_combiner.register_strategy(PurchaseFrequencyFilterStrategy())
        self.filter_combiner.register_strategy(MemberLevelFilterStrategy())
        self.filter_combiner.register_strategy(ConsumptionFilterStrategy())
        self.filter_combiner.register_strategy(PurchaseCountFilterStrategy())
        self.filter_combiner.register_strategy(LastPurchaseFilterStrategy())

    def filter_users_for_promotion(self, users: List[User], promotion: Promotion) -> List[User]:
        filter_conditions = promotion.filter_conditions
        operator = filter_conditions.pop("operator", "AND")
        
        if promotion.theme_tags:
            filter_conditions["preference"] = {
                "preferences": promotion.theme_tags,
                "match_all": False
            }
        
        return self.filter_combiner.apply_filters(users, filter_conditions, operator)

    def custom_filter_users(self, users: List[User], filter_conditions: Dict, operator: str = "AND") -> List[User]:
        return self.filter_combiner.apply_filters(users, filter_conditions, operator)

    def get_available_filters(self) -> List[Dict]:
        return self.filter_combiner.get_strategies_info()

    def filter_users_by_theme(self, users: List[User], theme_tags: List[str], match_all: bool = False) -> List[User]:
        condition = {
            "preference": {
                "preferences": theme_tags,
                "match_all": match_all
            }
        }
        return self.filter_combiner.apply_filters(users, condition)
