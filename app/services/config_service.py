from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

@dataclass
class ConfigItem:
    key: str
    value: Any
    description: str = ""
    config_type: str = "general"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._configs: Dict[str, ConfigItem] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, item_data in data.items():
                        item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                        item_data['updated_at'] = datetime.fromisoformat(item_data['updated_at'])
                        self._configs[key] = ConfigItem(**item_data)
            except Exception:
                pass

    def _save_configs(self) -> None:
        data = {}
        for key, item in self._configs.items():
            item_dict = item.__dict__.copy()
            item_dict['created_at'] = item_dict['created_at'].isoformat()
            item_dict['updated_at'] = item_dict['updated_at'].isoformat()
            data[key] = item_dict
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        item = self._configs.get(key)
        return item.value if item and item.is_active else default

    def set(self, key: str, value: Any, description: str = "", config_type: str = "general") -> None:
        if key in self._configs:
            self._configs[key].value = value
            self._configs[key].description = description
            self._configs[key].config_type = config_type
            self._configs[key].updated_at = datetime.now()
        else:
            self._configs[key] = ConfigItem(
                key=key,
                value=value,
                description=description,
                config_type=config_type
            )
        self._save_configs()

    def delete(self, key: str) -> bool:
        if key in self._configs:
            del self._configs[key]
            self._save_configs()
            return True
        return False

    def get_by_type(self, config_type: str) -> Dict[str, Any]:
        return {
            key: item.value
            for key, item in self._configs.items()
            if item.config_type == config_type and item.is_active
        }

    def get_all_configs(self) -> List[Dict]:
        return [
            {
                "key": item.key,
                "value": item.value,
                "description": item.description,
                "type": item.config_type,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            }
            for item in self._configs.values()
        ]

    def toggle_config(self, key: str, is_active: bool) -> bool:
        if key in self._configs:
            self._configs[key].is_active = is_active
            self._configs[key].updated_at = datetime.now()
            self._save_configs()
            return True
        return False

class RuleConfigService:
    def __init__(self, discount_service, user_filter_service, member_service):
        self.config_manager = ConfigManager()
        self.discount_service = discount_service
        self.user_filter_service = user_filter_service
        self.member_service = member_service
        self._load_initial_configs()

    def _load_initial_configs(self) -> None:
        if not self.config_manager.get("discount_weights"):
            default_weights = {
                "member_level": 0.4,
                "consumption_amount": 0.3,
                "shopping_preference": 0.15,
                "purchase_frequency": 0.15
            }
            self.update_discount_weights(default_weights)

        if not self.config_manager.get("discount_limits"):
            self.update_discount_limits(0.5, 1.0)

    def validate_discount_weights(self, weights: Dict[str, float]) -> bool:
        available_strategies = {s["name"] for s in self.discount_service.get_discount_config()["strategies"]}
        for name, weight in weights.items():
            if name not in available_strategies:
                return False
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                return False
        return True

    def validate_discount_limits(self, min_discount: float, max_discount: float) -> bool:
        return (isinstance(min_discount, (int, float)) and 
                isinstance(max_discount, (int, float)) and
                0 < min_discount <= max_discount <= 1)

    def update_discount_weights(self, weights: Dict[str, float]) -> bool:
        if not self.validate_discount_weights(weights):
            return False
        
        if self.discount_service.update_discount_weights(weights):
            self.config_manager.set(
                "discount_weights",
                weights,
                description="折扣策略权重配置",
                config_type="discount"
            )
            return True
        return False

    def update_discount_limits(self, min_discount: float, max_discount: float) -> bool:
        if not self.validate_discount_limits(min_discount, max_discount):
            return False
        
        self.discount_service.update_discount_limits(min_discount, max_discount)
        self.config_manager.set(
            "discount_limits",
            {"min": min_discount, "max": max_discount},
            description="折扣上下限配置",
            config_type="discount"
        )
        return True

    def update_member_level_config(self, level, **kwargs) -> bool:
        try:
            if self.member_service.update_level_config(level, **kwargs):
                config_key = f"member_level_{level.name.lower()}_config"
                current_config = self.member_service.get_member_level_config(level)
                self.config_manager.set(
                    config_key,
                    {
                        "min_consumption": current_config.min_consumption,
                        "base_discount": current_config.base_discount,
                        "description": current_config.description,
                        "benefits": current_config.benefits
                    },
                    description=f"{level.value} 等级配置",
                    config_type="member"
                )
                return True
            return False
        except Exception:
            return False

    def get_discount_config(self) -> Dict:
        config = self.discount_service.get_discount_config()
        config["saved_weights"] = self.config_manager.get("discount_weights", {})
        config["saved_limits"] = self.config_manager.get("discount_limits", {})
        return config

    def get_member_level_configs(self) -> Dict:
        configs = self.member_service.get_all_level_configs()
        result = {}
        for level, config in configs.items():
            result[level.name] = {
                "name": level.value,
                "min_consumption": config.min_consumption,
                "base_discount": config.base_discount,
                "description": config.description,
                "benefits": config.benefits
            }
        return result

    def get_filter_strategies(self) -> List[Dict]:
        return self.user_filter_service.get_available_filters()

    def reload_configs(self) -> None:
        discount_weights = self.config_manager.get("discount_weights")
        if discount_weights:
            self.discount_service.update_discount_weights(discount_weights)

        discount_limits = self.config_manager.get("discount_limits")
        if discount_limits:
            self.discount_service.update_discount_limits(
                discount_limits["min"],
                discount_limits["max"]
            )

    def get_all_configs(self) -> Dict:
        return {
            "discount": self.get_discount_config(),
            "member_levels": self.get_member_level_configs(),
            "filter_strategies": self.get_filter_strategies(),
            "raw_configs": self.config_manager.get_all_configs()
        }
