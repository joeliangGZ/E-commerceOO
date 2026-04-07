from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional
from ..models.user import User
from ..models.product import Product
from ..models.promotion import Promotion
from .member_service import MemberService

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

class MemberLevelDiscountStrategy(DiscountStrategy):
    def __init__(self, member_service: MemberService):
        self.member_service = member_service

    @property
    def name(self) -> str:
        return "member_level"

    @property
    def description(self) -> str:
        return "基于会员等级的基础折扣"

    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        return self.member_service.calculate_user_discount(user.user_id)

class ConsumptionAmountDiscountStrategy(DiscountStrategy):
    @property
    def name(self) -> str:
        return "consumption_amount"

    @property
    def description(self) -> str:
        return "基于累计消费金额的额外折扣"

    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        total = user.total_consumption
        if total >= 50000:
            return 0.85
        elif total >= 30000:
            return 0.88
        elif total >= 10000:
            return 0.92
        elif total >= 5000:
            return 0.95
        return 1.0

class ShoppingPreferenceDiscountStrategy(DiscountStrategy):
    @property
    def name(self) -> str:
        return "shopping_preference"

    @property
    def description(self) -> str:
        return "基于购物偏好的品类折扣"

    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        for preference in user.shopping_preferences:
            if product.matches_preference(preference):
                return 0.9
        return 1.0

class PurchaseFrequencyDiscountStrategy(DiscountStrategy):
    @property
    def name(self) -> str:
        return "purchase_frequency"

    @property
    def description(self) -> str:
        return "基于购买频率的忠诚度折扣"

    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        frequency = user.purchase_frequency
        if frequency >= 4:
            return 0.85
        elif frequency >= 2:
            return 0.9
        elif frequency >= 1:
            return 0.95
        return 1.0

class PromotionDiscountStrategy(DiscountStrategy):
    @property
    def name(self) -> str:
        return "promotion"

    @property
    def description(self) -> str:
        return "促销活动折扣"

    def calculate(self, user: User, product: Product, context: Dict = None) -> float:
        if not context or "promotion" not in context:
            return 1.0
        promotion: Promotion = context["promotion"]
        if not promotion.can_participate(user.user_id):
            return 1.0
        return promotion.discount_rules.get("global_discount", 1.0)

class DiscountCalculator:
    def __init__(self):
        self._strategies: Dict[str, DiscountStrategy] = {}
        self._weights: Dict[str, float] = {
            "member_level": 0.4,
            "consumption_amount": 0.3,
            "shopping_preference": 0.15,
            "purchase_frequency": 0.15
        }
        self._min_discount = 0.5
        self._max_discount = 1.0

    def register_strategy(self, strategy: DiscountStrategy) -> None:
        self._strategies[strategy.name] = strategy

    def remove_strategy(self, strategy_name: str) -> bool:
        if strategy_name in self._strategies:
            del self._strategies[strategy_name]
            if strategy_name in self._weights:
                del self._weights[strategy_name]
            return True
        return False

    def update_strategy_weight(self, strategy_name: str, weight: float) -> bool:
        if strategy_name in self._strategies and 0 <= weight <= 1:
            self._weights[strategy_name] = weight
            return True
        return False

    def set_discount_limits(self, min_discount: float, max_discount: float) -> None:
        self._min_discount = max(0.1, min(min_discount, max_discount))
        self._max_discount = min(1.0, max(min_discount, max_discount))

    def calculate_final_discount(self, user: User, product: Product, context: Dict = None) -> float:
        if not self._strategies:
            return 1.0
        
        total_weight = sum(self._weights.values())
        if total_weight == 0:
            return 1.0

        weighted_sum = 0.0
        for name, strategy in self._strategies.items():
            discount = strategy.calculate(user, product, context)
            weight = self._weights.get(name, 0)
            weighted_sum += discount * (weight / total_weight)

        final_discount = max(self._min_discount, min(self._max_discount, weighted_sum))
        return round(final_discount, 2)

    def get_strategies_info(self) -> List[Dict]:
        return [
            {
                "name": strategy.name,
                "description": strategy.description,
                "weight": self._weights.get(strategy.name, 0)
            }
            for strategy in self._strategies.values()
        ]

class DiscountService:
    def __init__(self, member_service: MemberService):
        self.calculator = DiscountCalculator()
        self._init_default_strategies(member_service)

    def _init_default_strategies(self, member_service: MemberService) -> None:
        self.calculator.register_strategy(MemberLevelDiscountStrategy(member_service))
        self.calculator.register_strategy(ConsumptionAmountDiscountStrategy())
        self.calculator.register_strategy(ShoppingPreferenceDiscountStrategy())
        self.calculator.register_strategy(PurchaseFrequencyDiscountStrategy())
        self.calculator.register_strategy(PromotionDiscountStrategy())

    def calculate_product_discount(self, user: User, product: Product, promotion: Promotion = None) -> float:
        context = {"promotion": promotion} if promotion else None
        return self.calculator.calculate_final_discount(user, product, context)

    def calculate_order_discount(self, user: User, products: List[Product], promotion: Promotion = None) -> Dict:
        total_original = 0.0
        total_discounted = 0.0
        product_discounts = []

        for product in products:
            discount = self.calculate_product_discount(user, product, promotion)
            original_price = product.price
            discounted_price = round(original_price * discount, 2)
            total_original += original_price
            total_discounted += discounted_price
            product_discounts.append({
                "product_id": product.product_id,
                "name": product.name,
                "original_price": original_price,
                "discount": discount,
                "discounted_price": discounted_price
            })

        overall_discount = round(total_discounted / total_original, 2) if total_original > 0 else 1.0
        return {
            "total_original": round(total_original, 2),
            "total_discounted": round(total_discounted, 2),
            "overall_discount": overall_discount,
            "product_discounts": product_discounts
        }

    def update_discount_weights(self, weights: Dict[str, float]) -> bool:
        success = True
        for name, weight in weights.items():
            if not self.calculator.update_strategy_weight(name, weight):
                success = False
        return success

    def update_discount_limits(self, min_discount: float, max_discount: float) -> None:
        self.calculator.set_discount_limits(min_discount, max_discount)

    def get_discount_config(self) -> Dict:
        return {
            "strategies": self.calculator.get_strategies_info(),
            "min_discount": self.calculator._min_discount,
            "max_discount": self.calculator._max_discount
        }
