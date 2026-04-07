from typing import List, Optional, Dict
from datetime import datetime
from ..models.user import User, MemberLevel
from ..models.member import MemberLevelManager, MemberLevelConfig

class MemberService:
    def __init__(self):
        self.level_manager = MemberLevelManager()
        self._users: Dict[str, User] = {}

    def register_user(self, user_id: str, username: str, email: str, phone: str) -> User:
        if user_id in self._users:
            raise ValueError(f"用户ID {user_id} 已存在")
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            phone=phone
        )
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_all_users(self) -> List[User]:
        return list(self._users.values())

    def update_user_consumption(self, user_id: str, amount: float) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        user.update_consumption(amount)
        self._update_member_level(user)
        return user

    def _update_member_level(self, user: User) -> None:
        new_level = self.level_manager.get_level_by_consumption(user.total_consumption)
        if new_level != user.member_level:
            user.member_level = new_level
            user.updated_at = datetime.now()

    def update_member_level_manually(self, user_id: str, new_level: MemberLevel) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        user.member_level = new_level
        user.updated_at = datetime.now()
        return user

    def get_member_level_config(self, level: MemberLevel) -> Optional[MemberLevelConfig]:
        return self.level_manager.get_config(level)

    def get_all_level_configs(self) -> Dict[MemberLevel, MemberLevelConfig]:
        return self.level_manager.get_all_levels()

    def update_level_config(self, level: MemberLevel, **kwargs) -> bool:
        try:
            self.level_manager.update_level_config(level, **kwargs)
            return True
        except Exception:
            return False

    def calculate_user_discount(self, user_id: str) -> float:
        user = self.get_user(user_id)
        if not user:
            return 1.0
        config = self.get_member_level_config(user.member_level)
        return config.base_discount if config else 1.0

    def get_users_by_level(self, level: MemberLevel) -> List[User]:
        return [user for user in self._users.values() if user.member_level == level]

    def get_member_statistics(self) -> Dict:
        stats = {
            "total_users": len(self._users),
            "level_distribution": {}
        }
        for level in MemberLevel:
            count = len(self.get_users_by_level(level))
            stats["level_distribution"][level.value] = count
        return stats
