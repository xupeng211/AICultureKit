# 代码风格与架构规范 (coding.md)

## 🎯 核心原则

### 1. **代码即文档**
- 代码应该自解释，减少注释依赖
- 使用有意义的变量名和函数名
- 优先编写清晰的代码，而不是聪明的代码

### 2. **一致性优于个人偏好**
- 严格遵循项目既定规范
- 使用自动化工具确保一致性
- 团队规范高于个人习惯

### 3. **渐进式优化**
- 先实现功能，再优化性能
- 避免过早优化
- 基于实际需求进行架构决策

---

## 🔧 Python代码风格

### 格式化工具
```bash
# 自动格式化
make format

# 等价于
black src/ tests/ scripts/ --line-length=88
isort src/ tests/ scripts/
```

### 代码风格检查
```bash
# 风格检查
make lint

# 等价于
flake8 src/ tests/ scripts/
```

### 类型注解
```python
# ✅ 好的示例
def calculate_score(
    user_id: int, 
    weights: Dict[str, float],
    threshold: float = 0.8
) -> Tuple[float, bool]:
    """计算用户评分。
    
    Args:
        user_id: 用户ID
        weights: 权重字典
        threshold: 阈值，默认0.8
        
    Returns:
        评分和是否通过的元组
    """
    score = sum(weights.values()) / len(weights)
    passed = score >= threshold
    return score, passed

# ❌ 避免的写法
def calc(user, w, t=0.8):
    s = sum(w.values()) / len(w)
    return s, s >= t
```

### 文档字符串规范
```python
def complex_function(
    param1: str,
    param2: List[Dict[str, Any]],
    param3: Optional[int] = None
) -> Dict[str, Any]:
    """
    函数的简短描述（一行）。
    
    详细描述可以多行，解释函数的具体行为、
    使用场景和注意事项。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述，可以是复杂类型
        param3: 可选参数3的描述，默认为None
        
    Returns:
        返回值的描述，说明字典包含的键值
        
    Raises:
        ValueError: 当param1为空时抛出
        TypeError: 当param2格式不正确时抛出
        
    Example:
        >>> result = complex_function("test", [{"key": "value"}])
        >>> print(result["status"])
        "success"
    """
    pass
```

---

## 🏗️ 架构规范

### 目录结构
```
src/
├── __init__.py
├── core/              # 核心业务逻辑
│   ├── __init__.py
│   ├── models.py      # 数据模型
│   ├── services.py    # 业务服务
│   └── exceptions.py  # 自定义异常
├── utils/             # 工具函数
│   ├── __init__.py
│   ├── helpers.py     # 通用助手函数
│   ├── validators.py  # 验证器
│   └── formatters.py  # 格式化工具
├── config/            # 配置管理
│   ├── __init__.py
│   ├── settings.py    # 设置文件
│   └── constants.py   # 常量定义
└── interfaces/        # 外部接口
    ├── __init__.py
    ├── api.py         # API接口
    └── cli.py         # 命令行接口
```

### 模块设计原则

#### 1. **单一职责原则**
```python
# ✅ 好的示例：单一职责
class UserValidator:
    """专门负责用户数据验证"""
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pass
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度"""
        pass

class UserService:
    """专门负责用户业务逻辑"""
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """创建用户"""
        pass
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> User:
        """更新用户"""
        pass

# ❌ 避免的写法：职责混乱
class UserManager:
    """既验证又操作又格式化，职责不清"""
    
    def validate_and_create_and_format_user(self, data):
        pass
```

#### 2. **依赖注入原则**
```python
# ✅ 好的示例：依赖注入
class EmailService:
    def __init__(self, smtp_client: SMTPClient):
        self.smtp_client = smtp_client
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        return self.smtp_client.send(to, subject, body)

class UserService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    def register_user(self, user_data: Dict[str, Any]) -> User:
        user = User(**user_data)
        self.email_service.send_email(
            user.email, 
            "Welcome", 
            "Welcome to our platform!"
        )
        return user

# ❌ 避免的写法：硬编码依赖
class UserService:
    def register_user(self, user_data):
        user = User(**user_data)
        # 硬编码的SMTP配置
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.send(user.email, "Welcome", "Welcome!")
        return user
```

### 错误处理规范

#### 1. **自定义异常**
```python
# src/core/exceptions.py
class AICultureKitError(Exception):
    """项目基础异常类"""
    pass

class ValidationError(AICultureKitError):
    """数据验证错误"""
    pass

class ServiceError(AICultureKitError):
    """服务调用错误"""
    pass

class ConfigurationError(AICultureKitError):
    """配置错误"""
    pass
```

#### 2. **异常处理模式**
```python
# ✅ 好的示例
def process_user_data(user_data: Dict[str, Any]) -> User:
    """处理用户数据"""
    try:
        # 验证数据
        if not user_data.get('email'):
            raise ValidationError("邮箱不能为空")
        
        # 业务逻辑
        user = User(**user_data)
        user.save()
        
        return user
        
    except ValidationError:
        # 重新抛出验证错误
        raise
    except Exception as e:
        # 包装未知错误
        raise ServiceError(f"用户数据处理失败: {str(e)}") from e

# ❌ 避免的写法
def process_user_data(user_data):
    try:
        # 裸奔的代码
        user = User(**user_data)
        user.save()
        return user
    except:
        # 吞掉所有异常
        return None
```

---

## 📊 质量检查

### 代码复杂度控制
```bash
# 复杂度检查
make complexity

# 目标指标
# - 圈复杂度 <= 10
# - 函数长度 <= 50行
# - 类方法数 <= 20个
```

### 安全检查
```bash
# 安全漏洞扫描
make security

# 检查项目
# - SQL注入风险
# - 硬编码敏感信息
# - 不安全的随机数生成
# - 潜在的代码注入
```

### 类型检查
```bash
# 静态类型检查
make typecheck

# 要求：
# - 所有公共函数必须有类型注解
# - 返回值必须明确类型
# - 复杂类型使用Union、Optional等
```

---

## 🔄 代码审查清单

### 提交前自检
- [ ] `make format` - 代码格式正确
- [ ] `make lint` - 无风格警告
- [ ] `make typecheck` - 类型注解完整
- [ ] `make test` - 所有测试通过
- [ ] `make coverage` - 覆盖率达标
- [ ] `make security` - 无安全风险
- [ ] `make complexity` - 复杂度可控

### 代码审查要点
- [ ] **可读性**: 代码逻辑清晰，命名合理
- [ ] **可维护性**: 模块职责明确，耦合度低
- [ ] **可测试性**: 核心逻辑有测试覆盖
- [ ] **性能**: 无明显性能瓶颈
- [ ] **安全性**: 无潜在安全风险
- [ ] **一致性**: 符合项目整体风格

---

## 🎯 最佳实践示例

### 配置管理
```python
# src/config/settings.py
from typing import Optional
from pathlib import Path
import os

class Settings:
    """项目配置管理"""
    
    # 基础配置
    APP_NAME: str = "AICultureKit"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 数据库配置
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # API配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # 项目路径
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    def __init__(self):
        # 确保必要目录存在
        self.LOGS_DIR.mkdir(exist_ok=True)

# 全局设置实例
settings = Settings()
```

### 工具函数示例
```python
# src/utils/helpers.py
from typing import Any, Dict, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """安全加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"JSON文件加载失败: {file_path}, 错误: {e}")
        return None

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """格式化时间戳"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_required_keys(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """验证字典是否包含必需的键"""
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        logger.error(f"缺少必需的键: {missing_keys}")
        return False
    return True
```

---

## 📝 规范更新流程

1. **发现问题** → 在日常开发中记录规范缺失
2. **讨论方案** → 在团队中讨论最佳实践
3. **更新文档** → 修改本文件，补充新规范
4. **工具支持** → 在`Makefile`中添加相应检查
5. **全员同步** → 确保所有开发者了解新规范

**记住：代码规范不是约束，而是团队协作的基础！** 