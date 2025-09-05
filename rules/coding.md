# 代码风格与架构规范

## 🎯 **核心原则**
- **修改优先** - 不要随意创建新文件，优先修改已有文件
- **模块化设计** - 每个文件功能单一，不要写"巨石文件"
- **详细中文注释** - 所有生成的代码必须带详细的中文注释，解释设计意图与逻辑
- **结构化输出** - 输出内容尽量用表格、目录结构、命令清单等结构化格式

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

### 详细中文注释要求
> **核心原则：**所有生成的代码必须带详细的中文注释，解释设计意图、业务逻辑和实现细节

### 注释层次结构
```python
"""
📁 模块级注释 - 文件顶部说明模块的整体功能和职责
user_service.py - 用户服务模块，负责用户数据管理和业务逻辑处理

主要功能:
- 用户注册、登录、注销管理
- 用户权限验证和角色分配  
- 用户数据的缓存和同步
- 用户行为日志记录和分析

依赖模块:
- core.database: 数据库连接和操作
- utils.crypto: 密码加密和验证
- services.auth: 身份认证服务
"""

class UserService:
    """
    🏗️ 类级注释 - 说明类的设计目的、主要职责和使用场景
    
    用户服务类 - 核心用户管理业务逻辑的封装
    
    设计理念:
    - 单一职责原则：只处理用户相关业务
    - 依赖注入：通过构造函数注入外部依赖
    - 缓存优化：热点数据优先从缓存读取
    
    典型使用场景:
    >>> user_service = UserService(config, db_connection)
    >>> user = user_service.get_user_by_id(12345)
    >>> user_service.update_user_profile(user.id, new_data)
    """
    
         def calculate_user_score(self, activities: List[Activity]) -> float:
        """
        🔧 方法级注释 - 详细说明方法的业务逻辑和技术实现
        
        计算用户活跃度得分 - 基于用户活动历史评估参与度
        
        业务逻辑:
        - 使用加权平均算法，近期活动权重更高
        - 确保得分能反映用户当前活跃状态  
        - 支持不同类型活动的差异化评分
        
        算法细节:
        - 时间权重递减：最新活动权重1.0，往前每个位置减少0.1
        - 最小权重保护：权重不低于0.1，避免历史数据完全失效
        - 异常处理：空活动列表返回0分，防止除零错误
        
        Args:
            activities: 用户活动列表，按业务发生顺序排列，包含时间戳和得分
            
        Returns:
            float: 加权平均后的用户活跃度得分，范围0.0-100.0
            
        Raises:
            ValueError: 当活动列表包含无效数据时抛出
            
        Examples:
            >>> activities = [Activity(score=85, timestamp=now), Activity(score=70, timestamp=yesterday)]  
            >>> score = service.calculate_user_score(activities)
            >>> print(f"用户活跃度: {score:.1f}")
        """
        # 🔍 数据预处理 - 按时间倒序排列，确保最新活动在前面
        # 这样可以让权重递减算法正确工作，最新活动获得最高权重
        sorted_activities = sorted(activities, key=lambda x: x.timestamp, reverse=True)
        
        # 💯 积分计算变量初始化
        total_score = 0.0    # 累计加权得分总和
        weight_sum = 0.0     # 累计权重总和，用于最终平均计算
        
        # 🔄 遍历活动列表，应用权重递减策略计算加权得分
        for i, activity in enumerate(sorted_activities):
            # ⚖️ 权重递减策略：最新活动权重1.0，每往前权重减少0.1
            # 使用max确保权重不低于0.1，避免历史数据完全失效
            weight = max(0.1, 1.0 - i * 0.1)
            
            # 📊 累计加权得分和权重
            total_score += activity.score * weight
            weight_sum += weight
            
        # 🛡️ 异常保护 - 避免除零错误，同时确保有意义的默认值
        # weight_sum为0说明没有有效活动，返回0分是合理的默认行为
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

## 📊 **输出格式规范**

### 表格格式要求
```markdown
# ✅ 推荐的表格格式
| 功能模块 | 状态 | 说明 | 负责人 |
|---------|------|------|--------|
| 用户管理 | ✅ 完成 | 基础功能已实现 | 张三 |
| 权限系统 | 🔄 开发中 | 预计本周完成 | 李四 |
| 数据统计 | ⏳ 待开始 | 依赖用户管理模块 | 王五 |

# 状态图标规范
✅ 已完成  🔄 进行中  ⏳ 待开始  ❌ 失败  ⚠️ 警告
```

### 目录结构格式
```bash
# ✅ 标准的目录结构展示
项目名称/
├── src/                    # 源代码目录
│   ├── core/              # 核心业务模块 
│   │   ├── __init__.py    # 模块初始化文件
│   │   ├── config.py      # 配置管理类
│   │   └── exceptions.py  # 自定义异常类
│   ├── services/          # 服务层实现
│   └── utils/             # 工具函数集合
├── tests/                 # 测试代码目录
├── docs/                  # 项目文档
└── requirements.txt       # 依赖清单文件
```

### 命令清单格式  
```bash
# ✅ 结构化的命令列表
## 环境准备命令
make init          # 初始化项目环境
make install       # 安装项目依赖  
make dev           # 启动开发环境

## 代码质量命令  
make format        # 代码格式化处理
make lint          # 代码风格检查
make test          # 运行单元测试
make coverage      # 生成覆盖率报告

## 部署发布命令
make prepush       # 预推送质检流程
make build         # 构建项目包
make deploy        # 部署到生产环境
```

### 检查结果格式
```markdown
# ✅ 标准的检查结果展示
| 检查项目 | 结果 | 详细信息 |
|---------|------|----------|  
| 代码格式检查 | ✅ 通过 | 所有文件格式规范 |
| 类型检查 | ✅ 通过 | 无类型错误 |
| 单元测试 | ❌ 失败 | 3个测试用例失败 |
| 覆盖率检查 | ⚠️ 警告 | 覆盖率69.4% < 80% |
| 安全扫描 | ✅ 通过 | 无安全漏洞 |
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

---

## ✅ **规则遵循检查清单**

| 检查项目 | 要求 | 检查方式 |
|---------|------|----------|
| **文件管理** | 不要随意创建新文件，优先修改已有文件 | 📁 确认是否真的需要新文件，能否在现有文件中扩展 |
| **中文注释** | 所有生成代码必须带详细中文注释 | 📝 检查是否有模块、类、方法、关键逻辑的详细说明 |
| **输出格式** | 使用表格、目录结构、命令清单格式 | 📊 确认输出内容是否采用结构化格式展示 |
| **代码风格** | 遵循PEP8和项目规范 | 🔧 运行 `make format` 和 `make lint` 检查 |
| **类型注解** | 所有函数参数和返回值有类型注解 | 🔍 运行 `make typecheck` 验证 |
| **测试覆盖** | 新增代码必须有对应测试 | 🧪 运行 `make coverage` 确保覆盖率达标 |

---

*遵循这些规范能确保代码质量、可读性和维护性。所有规则已集成到 `make prepush` 流程中进行自动检查。* 