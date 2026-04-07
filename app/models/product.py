from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Product:
    product_id: str
    name: str
    description: str
    price: float
    original_price: float
    category: str
    tags: List[str] = field(default_factory=list)
    stock: int = 0
    sales_count: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    extra_info: Dict = field(default_factory=dict)

    def update_price(self, new_price: float) -> None:
        self.original_price = self.price
        self.price = new_price
        self.updated_at = datetime.now()

    def update_stock(self, quantity: int) -> None:
        self.stock = max(0, self.stock + quantity)
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def matches_preference(self, preference: str) -> bool:
        return preference.lower() in self.category.lower() or \
               any(preference.lower() in tag.lower() for tag in self.tags) or \
               preference.lower() in self.name.lower()
