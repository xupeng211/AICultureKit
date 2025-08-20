# AICultureKit 开发文化指南

## 🎯 核心理念

本项目致力于建立一套标准化的AI协作开发文化，确保无论是人工开发还是AI辅助开发，都能产出高质量、可维护的代码。

## 📐 设计原则

### 1. YAGNI - You Aren't Gonna Need It

**核心思想**: 不要为未来可能的需求编写代码

**实践要求**:
- ✅ 只实现当前明确的业务需求
- ✅ 避免"以防万一"的预留设计
- ✅ 功能需求变更时再进行扩展
- ❌ 不要预测未来的需求变化
- ❌ 避免过度的抽象层设计

**代码示例**:
```python
# ❌ 过度设计
class ConfigManager:
    def __init__(self):
        self.file_configs = {}
        self.db_configs = {}
        self.remote_configs = {}  # 当前不需要
        self.cache_configs = {}   # 当前不需要

# ✅ YAGNI原则
class ConfigManager:
    def __init__(self):
        self.configs = {}  # 只实现当前需要的功能
```

### 2. KISS - Keep It Simple, Stupid

**核心思想**: 简单的解决方案优于复杂的

**实践要求**:
- ✅ 选择最直接的实现方式
- ✅ 代码易读易懂
- ✅ 减少认知负载
- ❌ 避免炫技式编程
- ❌ 避免过度使用设计模式

**代码示例**:
```python
# ❌ 过度复杂
def process_users(users):
    return list(map(lambda u: {**u, 'processed': True}
                   if u.get('active') else u,
                   filter(lambda x: x is not None, users)))

# ✅ KISS原则
def process_users(users):
    result = []
    for user in users:
        if user is None:
            continue
        if user.get('active'):
            user['processed'] = True
        result.append(user)
    return result
```

### 3. SOLID 原则

#### Single Responsibility Principle (单一职责)
每个类或函数只有一个变更的理由

```python
# ❌ 职责混乱
class UserService:
    def create_user(self, data):
        # 验证数据
        # 保存到数据库
        # 发送邮件
        # 记录日志
        pass

# ✅ 单一职责
class UserService:
    def __init__(self, validator, repository, email_service, logger):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.logger = logger

    def create_user(self, data):
        self.validator.validate(data)
        user = self.repository.save(data)
        self.email_service.send_welcome_email(user)
        self.logger.log_user_created(user)
        return user
```

#### Open/Closed Principle (开闭原则)
对扩展开放，对修改关闭

```python
# ✅ 开闭原则
from abc import ABC, abstractmethod

class NotificationSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailSender(NotificationSender):
    def send(self, message: str) -> None:
        # 发送邮件逻辑
        pass

class SMSSender(NotificationSender):
    def send(self, message: str) -> None:
        # 发送短信逻辑
        pass
```

## 🐍 Python 代码规范

### 格式化工具

**Black 配置**:
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

**isort 配置**:
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

### 类型提示

所有公共函数必须有类型提示：

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[Dict[str, Any]],
    filters: Optional[List[str]] = None
) -> Dict[str, int]:
    """处理数据并返回统计信息."""
    if filters is None:
        filters = []

    # 实现逻辑
    return {"processed": len(data), "filtered": len(filters)}
```

### 文档字符串

使用Google风格的docstring：

```python
def calculate_score(
    base_score: int,
    multiplier: float,
    bonus: Optional[int] = None
) -> float:
    """计算最终得分.

    根据基础分数、倍数和奖励分计算最终得分。

    Args:
        base_score: 基础分数
        multiplier: 倍数系数
        bonus: 可选的奖励分数

    Returns:
        计算后的最终得分

    Raises:
        ValueError: 当base_score为负数时

    Examples:
        >>> calculate_score(100, 1.5)
        150.0
        >>> calculate_score(100, 1.5, 20)
        170.0
    """
    if base_score < 0:
        raise ValueError("base_score不能为负数")

    result = base_score * multiplier
    if bonus:
        result += bonus
    return result
```

## 🧪 测试文化

### 测试驱动开发 (TDD)

遵循红-绿-重构循环：

1. **红**: 写一个失败的测试
2. **绿**: 写最少的代码让测试通过
3. **重构**: 改进代码质量

### 测试覆盖率

- **目标**: 代码覆盖率 > 80%
- **关键**: 覆盖所有重要的业务逻辑
- **工具**: pytest + pytest-cov

```python
def test_calculate_score_basic():
    """测试基础得分计算."""
    result = calculate_score(100, 1.5)
    assert result == 150.0

def test_calculate_score_with_bonus():
    """测试带奖励的得分计算."""
    result = calculate_score(100, 1.5, 20)
    assert result == 170.0

def test_calculate_score_negative_base():
    """测试负数基础分数抛出异常."""
    with pytest.raises(ValueError, match="base_score不能为负数"):
        calculate_score(-10, 1.5)
```

### 测试组织

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── fixtures/       # 测试固件
└── conftest.py     # pytest配置
```

## 🔒 安全最佳实践

### 1. 输入验证

```python
from typing import Any
import re

def validate_email(email: str) -> bool:
    """验证邮箱格式."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(user_input: Any) -> str:
    """清理用户输入."""
    if not isinstance(user_input, str):
        return str(user_input)

    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        user_input = user_input.replace(char, '')

    return user_input.strip()
```

### 2. 密钥管理

```python
import os
from typing import Optional

def get_secret(key: str, default: Optional[str] = None) -> str:
    """从环境变量获取密钥."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"必需的环境变量 {key} 未设置")
    return value

# 使用示例
DATABASE_URL = get_secret("DATABASE_URL")
API_KEY = get_secret("API_KEY")
```

### 3. 错误处理

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """服务层异常基类."""
    pass

class ValidationError(ServiceError):
    """验证异常."""
    pass

def safe_operation(data: dict) -> Optional[dict]:
    """安全的操作示例."""
    try:
        # 验证输入
        if not data or 'id' not in data:
            raise ValidationError("缺少必需的id字段")

        # 执行操作
        result = process_data(data)
        logger.info(f"操作成功完成, ID: {data['id']}")
        return result

    except ValidationError as e:
        logger.warning(f"验证失败: {e}")
        raise  # 重新抛出验证异常

    except Exception as e:
        logger.error(f"操作失败: {e}")
        return None  # 返回None表示操作失败
```

## 🤖 AI协作指南

### 1. 上下文管理

**为AI提供充分的上下文**:
- 项目的整体架构
- 当前任务的业务背景
- 相关的代码片段
- 错误信息和日志

### 2. 任务分解

**将复杂任务分解为小步骤**:
- 每个步骤都有明确的目标
- 步骤之间有清晰的依赖关系
- 每个步骤都可以独立测试

### 3. 迭代反馈

**建立反馈循环**:
- 实现一个小功能后立即测试
- 根据测试结果调整方向
- 持续改进代码质量

### 4. 文档驱动

**重要的设计决策要有文档**:
- 架构设计文档 (ADR)
- API接口文档
- 复杂算法的解释

## 🔧 工具链配置

### pre-commit 配置

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
```

### CI/CD 流程

1. **代码提交触发**
2. **环境准备**: Python多版本矩阵
3. **依赖安装**: pip install -r requirements-dev.txt
4. **代码质量检查**: Black, isort, flake8, mypy
5. **安全扫描**: Bandit, detect-secrets
6. **测试执行**: pytest + coverage
7. **构建验证**: python -m build
8. **部署准备**: 标签触发发布

## 📊 质量指标

### 代码质量指标

- **复杂度**: 圈复杂度 < 10
- **覆盖率**: 测试覆盖率 > 80%
- **重复度**: 重复代码 < 5%
- **维护性**: 维护性指数 > 70

### 性能指标

- **响应时间**: API响应 < 200ms
- **内存使用**: 内存增长 < 1MB/hour
- **错误率**: 错误率 < 0.1%

## 📝 提交规范

使用 Conventional Commits 格式：

```
<类型>[可选范围]: <描述>

[可选正文]

[可选脚注]
```

**类型说明**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他杂项

**示例**:
```
feat(auth): 添加JWT身份验证

实现了基于JWT的用户身份验证机制，包括：
- 登录接口
- 令牌验证中间件
- 用户权限检查

Closes #123
```

## 🚀 持续改进

### 定期回顾

- **每周**: 代码质量报告回顾
- **每月**: 开发流程优化讨论
- **每季度**: 技术栈升级评估

### 知识分享

- **技术分享**: 新技术、最佳实践分享
- **代码评审**: 重要代码的集体评审
- **文档更新**: 及时更新开发文档

### 工具升级

- **依赖更新**: 定期更新依赖包版本
- **工具升级**: 跟进开发工具的新版本
- **流程优化**: 根据团队反馈优化流程

---

这套开发文化是一个活文档，会随着项目的发展而不断演进。我们鼓励所有开发者（包括AI）积极参与文化建设，提出改进建议。
