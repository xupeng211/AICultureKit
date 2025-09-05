# 代码风格与架构规范

## 🎯 **核心原则**
- **修改优先** - 在已有文件内修改，而不是随意新建文件
- **模块化设计** - 每个文件功能单一，不要写"巨石文件"
- **中文注释** - 所有生成的代码必须带简明的中文注释

---

## 📝 **命名规范**

### Python 命名约定
```python
# 变量和函数: snake_case
user_name = "张三"
def get_user_info():
    pass

# 类名: PascalCase
class UserService:
    pass

# 常量: UPPER_CASE
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# 私有方法: _开头
def _validate_data():
    pass

# 特殊方法: __开头结尾__
def __init__(self):
    pass
```

### 文件和目录命名
```bash
# 目录名: 小写字母 + 下划线
user_management/
data_analysis/

# Python文件: 小写字母 + 下划线
user_service.py
data_processor.py

# 配置文件: 小写字母 + 点号
requirements.txt
setup.cfg
```

---

## 🏗️ **目录结构规范**

### 项目根目录
```
src/                    # 所有源代码
├── core/              # 核心业务逻辑
├── services/          # 服务层，处理业务逻辑
├── utils/             # 通用工具函数
└── main.py            # 应用入口

tests/                 # 所有测试代码
├── unit/              # 单元测试
├── integration/       # 集成测试
└── fixtures/          # 测试数据

scripts/               # 辅助脚本工具
├── setup_project.py   # 项目初始化
├── quality_checker.py # 代码质量检查
└── ci_monitor.py      # CI监控工具

docs/                  # 项目文档
rules/                 # 开发规范文档
backup/                # 自动备份文件
logs/                  # 日志输出
```

### 禁止的目录结构
```bash
❌ 随意创建的目录
├── temp/
├── test123/
├── my_code/
└── utils2/

❌ 嵌套过深的目录
└── src/core/services/user/data/models/
```

---

## 💻 **代码风格规范**

### 导入语句顺序
```python
# 1. 标准库导入
import os
import sys
from pathlib import Path

# 2. 第三方库导入
import requests
from fastapi import FastAPI

# 3. 本地模块导入
from src.core import config
from src.services.user_service import UserService
```

### 函数定义规范
```python
def process_user_data(
    user_id: int, 
    data: Dict[str, Any], 
    validate: bool = True
) -> Optional[Dict[str, Any]]:
    """
    处理用户数据 - 验证、清洗、转换用户输入数据
    
    Args:
        user_id: 用户ID，用于数据关联和日志记录
        data: 原始用户数据字典，包含所有待处理字段
        validate: 是否执行数据验证，默认开启以确保数据质量
        
    Returns:
        处理后的数据字典，失败时返回None
        
    Raises:
        ValidationError: 当数据验证失败时抛出
        ProcessingError: 当数据处理过程出错时抛出
    """
    # 实现逻辑...
    pass
```

### 类定义规范
```python
class UserService:
    """
    用户服务类 - 负责用户相关的业务逻辑处理
    
    主要功能：
    - 用户信息的增删改查
    - 用户权限验证和管理
    - 用户数据的缓存策略
    """
    
    def __init__(self, config: Config):
        """
        初始化用户服务 - 设置数据库连接和缓存配置
        
        Args:
            config: 配置对象，包含数据库和缓存相关设置
        """
        self.config = config
        self._db = None  # 延迟初始化数据库连接
        
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息 - 优先从缓存读取，缓存未命中时查询数据库"""
        pass
```

---

## 📋 **注释规范**

### 中文注释要求
```python
# ✅ 好的注释 - 解释WHY和WHAT
def calculate_user_score(activities: List[Activity]) -> float:
    """
    计算用户活跃度得分 - 基于用户活动历史评估参与度
    
    使用加权平均算法，近期活动权重更高，确保得分能反映用户当前状态
    """
    # 按时间倒序排列，越近的活动权重越大
    sorted_activities = sorted(activities, key=lambda x: x.timestamp, reverse=True)
    
    total_score = 0.0
    weight_sum = 0.0
    
    for i, activity in enumerate(sorted_activities):
        # 权重递减策略：最新活动权重1.0，每往前权重减少0.1
        weight = max(0.1, 1.0 - i * 0.1)
        total_score += activity.score * weight
        weight_sum += weight
        
    # 避免除零错误，同时确保有意义的默认值
    return total_score / weight_sum if weight_sum > 0 else 0.0

# ❌ 不好的注释 - 仅仅翻译代码
def calculate_user_score(activities):
    # 排序活动列表
    sorted_activities = sorted(activities, key=lambda x: x.timestamp, reverse=True)
    # 初始化总分数
    total_score = 0.0
```

### 复杂逻辑注释
```python
def optimize_database_query(query: str, params: dict) -> str:
    """优化数据库查询语句 - 自动添加索引提示和分页限制"""
    
    # 检测潜在的N+1查询问题，自动添加JOIN优化
    if "SELECT" in query and query.count("SELECT") > 1:
        # 复杂的子查询检测逻辑...
        pass
    
    # 为大表查询自动添加LIMIT，防止意外的全表扫描
    if any(table in query for table in ["users", "orders", "logs"]):
        if "LIMIT" not in query.upper():
            query += " LIMIT 10000"  # 安全的默认限制
            
    return query
```

---

## 🛠️ **工具配置**

### Black 格式化配置
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | .venv
  | build
)/
'''
```

### Flake8 检查配置
```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,migrations,.venv
per-file-ignores =
    __init__.py:F401
```

### MyPy 类型检查
```ini
# setup.cfg
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

## 🔧 **依赖管理规范**

### requirements.txt 管理
```bash
# 生产依赖
fastapi==0.104.1        # Web框架
uvicorn[standard]==0.24.0  # ASGI服务器
pydantic==2.5.0         # 数据验证

# 开发依赖分离到 requirements-dev.txt
pytest==7.4.4
black==23.12.1
flake8==6.1.0
```

### 新增依赖流程
1. **评估必要性** - 确认是否真的需要新依赖
2. **选择稳定版本** - 避免使用alpha/beta版本
3. **更新requirements** - 立即更新对应的requirements文件
4. **测试兼容性** - 运行 `pip check` 检查依赖冲突
5. **提交记录** - commit中说明添加依赖的原因

---

## ⚡ **性能与安全考虑**

### 代码性能规范
```python
# ✅ 高效的列表处理
user_ids = [user.id for user in active_users if user.is_verified]

# ❌ 低效的循环操作
user_ids = []
for user in active_users:
    if user.is_verified:
        user_ids.append(user.id)

# ✅ 使用生成器节省内存
def process_large_dataset(data_source):
    for item in data_source:
        yield transform_item(item)

# ❌ 一次性加载所有数据到内存
def process_large_dataset(data_source):
    return [transform_item(item) for item in data_source]
```

### 安全编码规范
```python
# ✅ 安全的SQL查询
def get_user_by_id(user_id: int) -> Optional[User]:
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# ❌ SQL注入风险
def get_user_by_id(user_id: str) -> Optional[User]:
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

---

*遵循这些规范能确保代码质量、可读性和维护性。如有疑问请查阅 [rules/README.md](README.md) 获取完整开发指南。* 