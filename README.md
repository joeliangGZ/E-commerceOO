# 电商会员与促销Web管理系统

一个采用Python面向对象开发的电商会员管理与个性化促销系统，运用策略模式实现灵活的折扣规则配置和用户筛选逻辑。

## ✨ 功能特性

### 核心功能
1. **四级会员制度**
   - 内置普通/白银/黄金/钻石四个固定会员等级
   - 根据用户累计消费金额自动升降级
   - 支持管理员手动调整会员等级
   - 每个等级独立配置消费阈值、基础折扣和专属权益

2. **动态折扣计算引擎**（策略模式实现）
   - 会员等级折扣策略
   - 累计消费金额折扣策略
   - 购物偏好匹配折扣策略
   - 购买频率折扣策略
   - 促销活动叠加折扣策略
   - 多维度折扣因子加权计算最终折扣
   - 支持灵活新增/修改/删除折扣策略

3. **智能用户筛选系统**
   - 购物偏好筛选
   - 购买频率筛选
   - 会员等级筛选
   - 消费金额筛选
   - 购买次数筛选
   - 最后购买时间筛选
   - 支持多条件组合筛选（AND/OR逻辑）
   - 自动匹配活动主题目标用户

4. **动态规则配置**
   - 折扣权重实时调整，即时生效
   - 会员等级参数灵活配置
   - 筛选规则可视化配置
   - 配置参数自动验证
   - 支持配置持久化和热加载

## 📦 依赖说明

### 核心依赖
**无任何第三方库依赖！** 仅需要Python 3.7+ 标准库即可运行所有核心功能。

### 可选依赖（开发Web界面时需要）
```bash
# 安装Web开发相关依赖
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 运行功能演示
```bash
python demo.py
```
演示脚本会展示所有核心功能的使用效果：
- 会员注册与等级自动升级
- 动态折扣计算
- 智能用户筛选
- 动态配置修改
- 促销活动功能

### 2. 基础使用示例
```python
from app.services.member_service import MemberService
from app.services.discount_service import DiscountService
from app.models.product import Product

# 初始化服务
member_service = MemberService()
discount_service = DiscountService(member_service)

# 注册用户
user = member_service.register_user("u001", "张三", "zhangsan@example.com", "13800138001")

# 更新消费记录，自动升级会员等级
member_service.update_user_consumption("u001", 1500)

# 创建商品
product = Product("p001", "智能手机", "5G手机", 5999, 5999, "电子产品", ["数码"])

# 计算用户专属折扣
discount = discount_service.calculate_product_discount(user, product)
print(f"折扣: {discount}, 折后价: {product.price * discount}")
```

## 📁 项目结构
```
E-commerceOO/
├── app/
│   ├── models/                  # 数据模型层
│   │   ├── user.py              # 用户模型和会员等级枚举
│   │   ├── member.py            # 会员等级配置和管理器
│   │   ├── product.py           # 商品模型
│   │   └── promotion.py         # 促销活动模型
│   └── services/                # 业务服务层
│       ├── member_service.py    # 会员管理服务
│       ├── discount_service.py  # 折扣计算引擎（策略模式）
│       ├── user_filter_service.py # 用户筛选服务（策略模式）
│       └── config_service.py    # 动态配置管理服务
├── demo.py                      # 功能演示脚本
├── requirements.txt             # 依赖说明
├── .gitignore                   # Git忽略配置
└── README.md                    # 项目说明文档
```

## 🎯 设计特点

- **面向对象设计**：各功能模块独立封装，低耦合高内聚
- **策略模式**：折扣计算和用户筛选均采用策略模式，支持灵活扩展
- **配置驱动**：所有规则支持动态配置，修改后即时生效
- **无侵入式**：核心功能不依赖任何第三方框架，可轻松集成到现有系统
- **可扩展**：预留了丰富的扩展接口，便于后续开发Web管理界面

## 🔧 后续扩展

### 开发Web管理界面
可以基于Flask、Django等Web框架开发管理员后台，实现以下功能：
1. 会员管理页面：查看和编辑会员信息
2. 折扣规则配置页面：可视化配置各折扣策略的权重和参数
3. 活动管理页面：创建、编辑促销活动和筛选条件
4. 数据统计页面：展示会员分布、折扣使用情况等数据

### 数据持久化
当前版本使用内存存储，可根据需要接入MySQL、MongoDB等数据库，实现数据持久化。

### API接口开发
可以基于FastAPI等框架开发RESTful API接口，供前端和其他系统调用。

## 📝 许可证

MIT License
