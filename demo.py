#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商会员与促销系统演示脚本
"""

from datetime import datetime
from app.models.user import MemberLevel
from app.models.product import Product
from app.models.promotion import Promotion, PromotionStatus
from app.services.member_service import MemberService
from app.services.discount_service import DiscountService
from app.services.user_filter_service import UserFilterService
from app.services.config_service import RuleConfigService

def demo():
    print("=" * 60)
    print("电商会员与促销管理系统演示")
    print("=" * 60)

    # 初始化服务
    member_service = MemberService()
    discount_service = DiscountService(member_service)
    user_filter_service = UserFilterService()
    config_service = RuleConfigService(discount_service, user_filter_service, member_service)

    print("\n1. 注册测试用户")
    print("-" * 40)
    user1 = member_service.register_user("u001", "张三", "zhangsan@example.com", "13800138001")
    user2 = member_service.register_user("u002", "李四", "lisi@example.com", "13800138002")
    user3 = member_service.register_user("u003", "王五", "wangwu@example.com", "13800138003")
    user4 = member_service.register_user("u004", "赵六", "zhaoliu@example.com", "13800138004")
    
    # 设置用户消费数据
    member_service.update_user_consumption("u001", 1500)  # 白银会员
    member_service.update_user_consumption("u002", 6000)  # 黄金会员
    member_service.update_user_consumption("u003", 25000) # 钻石会员
    member_service.update_user_consumption("u004", 500)   # 普通会员

    # 设置购物偏好
    user1.add_preference("电子产品")
    user2.add_preference("服装")
    user2.add_preference("电子产品")
    user3.add_preference("家居")
    user3.add_preference("电子产品")
    user4.add_preference("图书")

    # 设置购买频率
    user1.purchase_frequency = 1.2
    user2.purchase_frequency = 2.5
    user3.purchase_frequency = 4.8
    user4.purchase_frequency = 0.5

    for user in [user1, user2, user3, user4]:
        print(f"用户: {user.username}, 等级: {user.member_level.value}, 累计消费: {user.total_consumption}元, 偏好: {user.shopping_preferences}")

    print("\n2. 创建测试商品")
    print("-" * 40)
    product1 = Product("p001", "智能手机", "最新款5G智能手机", 5999, 5999, "电子产品", ["手机", "数码"])
    product2 = Product("p002", "休闲牛仔裤", "纯棉修身牛仔裤", 299, 299, "服装", ["裤子", "休闲"])
    product3 = Product("p003", "无线耳机", "降噪蓝牙耳机", 1299, 1299, "电子产品", ["耳机", "数码"])
    product4 = Product("p004", "Python编程", "Python从入门到精通", 89, 89, "图书", ["编程", "技术"])

    for product in [product1, product2, product3, product4]:
        print(f"商品: {product.name}, 分类: {product.category}, 价格: {product.price}元")

    print("\n3. 测试动态折扣计算")
    print("-" * 40)
    for user in [user1, user2, user3, user4]:
        discount = discount_service.calculate_product_discount(user, product1)
        discounted_price = round(product1.price * discount, 2)
        print(f"用户 {user.username} 购买 {product1.name} 的折扣: {discount:.2f}, 折后价: {discounted_price}元")

    print("\n4. 测试订单折扣计算")
    print("-" * 40)
    products = [product1, product3]
    for user in [user1, user2, user3]:
        order_discount = discount_service.calculate_order_discount(user, products)
        print(f"用户 {user.username} 购买多个商品:")
        print(f"  原价总计: {order_discount['total_original']}元")
        print(f"  折扣后总计: {order_discount['total_discounted']}元")
        print(f"  整体折扣: {order_discount['overall_discount']:.2f}")

    print("\n5. 测试会员等级自动升级")
    print("-" * 40)
    print(f"用户 {user4.username} 当前等级: {user4.member_level.value}")
    member_service.update_user_consumption("u004", 20000)
    print(f"消费20000元后等级: {user4.member_level.value}")

    print("\n6. 测试用户智能筛选")
    print("-" * 40)
    all_users = member_service.get_all_users()
    print("筛选偏好包含'电子产品'的用户:")
    filtered_users = user_filter_service.filter_users_by_theme(all_users, ["电子产品"])
    for user in filtered_users:
        print(f"  - {user.username}, 偏好: {user.shopping_preferences}")

    print("\n筛选黄金及以上等级且购买频率>=2的用户:")
    filter_conditions = {
        "member_level": {"levels": [MemberLevel.GOLD, MemberLevel.DIAMOND]},
        "purchase_frequency": {"min": 2}
    }
    filtered_users = user_filter_service.custom_filter_users(all_users, filter_conditions)
    for user in filtered_users:
        print(f"  - {user.username}, 等级: {user.member_level.value}, 购买频率: {user.purchase_frequency}")

    print("\n7. 测试动态配置修改")
    print("-" * 40)
    print("当前折扣权重配置:")
    config = config_service.get_discount_config()
    for strategy in config["strategies"]:
        print(f"  {strategy['description']}: 权重={strategy['weight']}")

    print("\n修改折扣权重，提高消费金额权重至0.4:")
    new_weights = {
        "member_level": 0.3,
        "consumption_amount": 0.4,
        "shopping_preference": 0.15,
        "purchase_frequency": 0.15
    }
    config_service.update_discount_weights(new_weights)
    
    print("修改后的权重配置:")
    config = config_service.get_discount_config()
    for strategy in config["strategies"]:
        print(f"  {strategy['description']}: 权重={strategy['weight']}")

    discount = discount_service.calculate_product_discount(user3, product1)
    print(f"钻石会员 {user3.username} 购买手机的新折扣: {discount:.2f}")

    print("\n8. 测试促销活动功能")
    print("-" * 40)
    promotion = Promotion(
        promotion_id="act001",
        name="618电子产品特惠",
        description="618期间电子产品专属优惠",
        theme_tags=["电子产品", "数码"],
        status=PromotionStatus.ACTIVE,
        discount_rules={"global_discount": 0.85}
    )

    print(f"活动: {promotion.name}")
    print(f"主题标签: {promotion.theme_tags}")
    
    print("\n筛选活动目标用户:")
    target_users = user_filter_service.filter_users_for_promotion(all_users, promotion)
    for user in target_users:
        discount = discount_service.calculate_product_discount(user, product1, promotion)
        discounted_price = round(product1.price * discount, 2)
        print(f"  - {user.username}, 活动折扣价: {discounted_price}元")

    print("\n" + "=" * 60)
    print("演示完成！所有核心功能正常工作。")
    print("=" * 60)

if __name__ == "__main__":
    demo()
