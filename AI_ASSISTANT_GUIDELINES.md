"""
AI开发文化原则配置和管理模块

定义和管理所有大厂级别的开发原则，确保AI工具在开发过程中遵循这些原则。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import yaml
from pathlib import Path

class PrincipleCategory(Enum):
    """原则分类"""
    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COLLABORATION = "collaboration"
    TESTING = "testing"
    CI_CD = "ci_cd"
    DOCUMENTATION = "documentation"

@dataclass
class DevelopmentPrinciple:
    """开发原则数据结构"""
    name: str
    category: PrincipleCategory
    description: str
    rules: List[str]
    ai_instructions: List[str]  # 给AI的具体指令
    enforcement_level: str = "strict"  # strict, warning, optional
    tools: List[str] = field(default_factory=list)
    examples: Dict[str, str] = field(default_factory=dict)

class AICulturePrinciples:
    """AI开发文化原则管理器"""

    def __init__(self):
        self.principles = self._load_all_principles()

    def _load_all_principles(self) -> Dict[str, DevelopmentPrinciple]:
        """加载所有开发原则"""
        principles = {}

        # SOLID原则
        principles["solid"] = DevelopmentPrinciple(
            name="SOLID原则",
            category=PrincipleCategory.CODE_QUALITY,
            description="面向对象设计的五大基本原则",
            rules=[
                "单一职责原则(SRP): 每个类只负责一个功能",
                "开放封闭原则(OCP): 对扩展开放，对修改封闭",
                "里氏替换原则(LSP): 子类应该能够替换父类",
                "接口隔离原则(ISP): 不强迫客户依赖不需要的接口",
                "依赖倒置原则(DIP): 依赖于抽象而不是具体实现"
            ],
            ai_instructions=[
                "设计类时确保每个类只有一个改变的理由",
                "使用接口和抽象类来定义契约",
                "优先使用组合而不是继承",
                "创建小而专注的接口",
                "依赖注入而不是硬编码依赖"
            ],
            tools=["mypy", "pylint", "flake8"],
            examples={
                "good": "class UserRepository(ABC): ...",
                "bad": "class UserManager: # 既管理用户又处理邮件"
            }
        )

        # DRY原则
        principles["dry"] = DevelopmentPrinciple(
            name="DRY原则",
            category=PrincipleCategory.CODE_QUALITY,
            description="Don't Repeat Yourself - 避免重复代码",
            rules=[
                "每个知识点在系统中都应该有一个单一的、无歧义的、权威的表示",
                "重复的代码应该抽取成函数、类或模块",
                "配置信息应该集中管理",
                "业务逻辑应该避免重复实现"
            ],
            ai_instructions=[
                "发现重复代码时立即重构",
                "创建工具函数和帮助类来消除重复",
                "使用配置文件而不是硬编码值",
                "优先使用现有的库和框架功能"
            ],
            tools=["duplicate-code-detection", "refactoring-tools"],
            examples={
                "good": "def validate_email(email: str) -> bool: ...",
                "bad": "if '@' in email and '.' in email: ..."
            }
        )

        # 微服务架构原则
        principles["microservices"] = DevelopmentPrinciple(
            name="微服务架构原则",
            category=PrincipleCategory.ARCHITECTURE,
            description="构建可扩展的分布式系统",
            rules=[
                "服务按业务领域拆分",
                "服务间松耦合高内聚",
                "每个服务独立部署和扩展",
                "服务间通过API通信",
                "数据库分离"
            ],
            ai_instructions=[
                "设计服务时考虑业务边界",
                "避免服务间直接数据库访问",
                "实现健康检查和监控端点",
                "设计幂等的API接口",
                "考虑服务降级和熔断机制"
            ],
            tools=["docker", "kubernetes", "api-gateway"],
            examples={
                "good": "user-service, order-service, payment-service",
                "bad": "monolithic-application"
            }
        )

        # 安全原则
        principles["security"] = DevelopmentPrinciple(
            name="安全开发原则",
            category=PrincipleCategory.SECURITY,
            description="确保应用程序安全",
            rules=[
                "最小权限原则",
                "输入验证和输出编码",
                "安全的认证和授权",
                "数据加密传输和存储",
                "定期安全审计"
            ],
            ai_instructions=[
                "永远不要信任用户输入",
                "使用参数化查询防止SQL注入",
                "实现CSRF和XSS防护",
                "使用HTTPS和强密码策略",
                "记录安全相关的操作日志"
            ],
            tools=["bandit", "safety", "owasp-zap"],
            examples={
                "good": "bcrypt.hashpw(password.encode('utf-8'), salt)",
                "bad": "password == user.password"
            }
        )

        # 测试原则
        principles["testing"] = DevelopmentPrinciple(
            name="测试驱动开发",
            category=PrincipleCategory.TESTING,
            description="确保代码质量和可维护性",
            rules=[
                "测试金字塔: 单元测试 > 集成测试 > E2E测试",
                "测试覆盖率至少80%",
                "编写可读性强的测试",
                "测试应该快速且独立",
                "先写测试再写实现"
            ],
            ai_instructions=[
                "为每个函数和类编写单元测试",
                "使用有意义的测试名称",
                "测试正常路径和异常路径",
                "使用mock对象隔离依赖",
                "保持测试的简单和专注"
            ],
            tools=["pytest", "coverage", "mock"],
            examples={
                "good": "def test_user_registration_with_valid_email(): ...",
                "bad": "def test1(): ..."
            }
        )

        # CI/CD原则
        principles["cicd"] = DevelopmentPrinciple(
            name="持续集成/持续部署",
            category=PrincipleCategory.CI_CD,
            description="自动化构建、测试和部署流程",
            rules=[
                "每次提交都触发自动化构建",
                "自动化测试必须通过才能合并",
                "代码审查是必须的",
                "部署应该是自动化和可重复的",
                "回滚机制要简单快速"
            ],
            ai_instructions=[
                "配置GitHub Actions或类似CI工具",
                "确保所有检查都通过才能部署",
                "实现蓝绿部署或滚动更新",
                "监控部署后的系统健康状态",
                "自动化数据库迁移和配置更新"
            ],
            tools=["github-actions", "docker", "kubernetes"],
            examples={
                "good": "自动化测试 -> 代码审查 -> 自动部署",
                "bad": "手动测试 -> 手动部署"
            }
        )

        # 性能优化原则
        principles["performance"] = DevelopmentPrinciple(
            name="性能优化原则",
            category=PrincipleCategory.PERFORMANCE,
            description="构建高性能的应用程序",
            rules=[
                "API响应时间 < 200ms",
                "数据库查询优化",
                "缓存策略设计",
                "资源懒加载",
                "监控和告警"
            ],
            ai_instructions=[
                "优化数据库查询和索引",
                "实现多层缓存策略",
                "使用异步处理非关键任务",
                "压缩和优化静态资源",
                "监控关键性能指标"
            ],
            tools=["redis", "nginx", "prometheus"],
            examples={
                "good": "SELECT * FROM users WHERE id = ? LIMIT 1",
                "bad": "SELECT * FROM users"
            }
        )

        # 文档原则
        principles["documentation"] = DevelopmentPrinciple(
            name="文档驱动开发",
            category=PrincipleCategory.DOCUMENTATION,
            description="维护高质量的项目文档",
            rules=[
                "README必须包含快速开始指南",
                "API文档要完整和最新",
                "代码注释要解释为什么而不是什么",
                "架构决策要有记录",
                "变更日志要及时更新"
            ],
            ai_instructions=[
                "为每个公共API编写文档字符串",
                "保持README的简洁和实用",
                "记录重要的设计决策",
                "提供代码示例和使用场景",
                "定期审查和更新文档"
            ],
            tools=["sphinx", "mkdocs", "swagger"],
            examples={
                "good": "def calculate_tax(amount: float) -> float:\n    \"\"\"计算税额，根据当前税率政策\"\"\"",
                "bad": "def calc(x): # 计算"
            }
        )

        return principles

    def get_principle(self, name: str) -> Optional[DevelopmentPrinciple]:
        """获取指定原则"""
        return self.principles.get(name)

    def get_by_category(self, category: PrincipleCategory) -> List[DevelopmentPrinciple]:
        """按分类获取原则"""
        return [p for p in self.principles.values() if p.category == category]

    def get_ai_instructions(self) -> Dict[str, List[str]]:
        """获取所有AI指令"""
        return {name: principle.ai_instructions
                for name, principle in self.principles.items()}

    def export_to_yaml(self, file_path: str) -> None:
        """导出原则到YAML文件"""
        data = {}
        for name, principle in self.principles.items():
            data[name] = {
                "name": principle.name,
                "category": principle.category.value,
                "description": principle.description,
                "rules": principle.rules,
                "ai_instructions": principle.ai_instructions,
                "enforcement_level": principle.enforcement_level,
                "tools": principle.tools,
                "examples": principle.examples
            }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def validate_project(self, project_path: str) -> Dict[str, Any]:
        """验证项目是否遵循原则"""
        violations = []
        recommendations = []

        project_dir = Path(project_path)

        # 检查基本文件
        if not (project_dir / "README.md").exists():
            violations.append("缺少README.md文件")

        if not (project_dir / ".gitignore").exists():
            violations.append("缺少.gitignore文件")

        # 检查Python项目结构
        if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
            if not (project_dir / "tests").exists():
                violations.append("Python项目缺少tests目录")

            if not (project_dir / ".pre-commit-config.yaml").exists():
                violations.append("缺少pre-commit配置")

        # 检查CI/CD
        if not (project_dir / ".github" / "workflows").exists():
            recommendations.append("建议添加GitHub Actions工作流")

        return {
            "violations": violations,
            "recommendations": recommendations,
            "score": max(0, 100 - len(violations) * 10 - len(recommendations) * 5)
        }

# 🤖 AI助手开发文化指导手册

## 📋 **概述**

作为AI编程助手，你需要始终遵循这些开发文化原则，确保生成的代码符合最高质量标准。
**重要：进入项目的第一时间，必须执行功能完整性检查！**

---

## 🚨 **第一优先级：功能完整性检查 (P0)**

### 🔍 **进入项目立即执行**

```bash
# 1. 立即执行功能完整性检查 (最高优先级)
python -c "
from aiculture.functionality_checker import FunctionalityChecker
from pathlib import Path

checker = FunctionalityChecker(Path('.'))
violations = checker.check_all_functionality()
critical = [v for v in violations if v.severity == 'critical']

if critical:
    print('🚨 发现严重功能问题，AI拒绝工作！')
    for issue in critical[:3]:
        print(f'❌ {issue.message}')
        print(f'💥 影响: {issue.impact}')
    print('请先修复功能完整性问题再继续开发。')
else:
    print('✅ 功能完整性检查通过')
"

# 2. 基础设施安全检查 (第二优先级)
python -m aiculture.cli infrastructure-check --path .
```

### ⚠️ **必须检查的功能完整性问题**

| 检查项目 | 严重程度 | 处理方式 |
|----------|----------|----------|
| **🎯 文件依赖完整性** | 🔥 Critical | 立即停止，要求修复 |
| **⚡ CLI命令完整性** | 🔥 Critical | 拒绝生成空壳命令 |
| **⚙️ 配置系统一致性** | 🔥 Critical | 确保设计与实现一致 |
| **📋 模板系统完整性** | 🔥 Critical | 验证模板真正可用 |
| **🧪 测试覆盖率** | 🔶 Warning | 要求补充测试 |
| **🔗 端到端工作流** | 🔶 Warning | 验证用户场景 |

### 📋 **功能完整性问题处理流程**

```
1. 🎯 功能完整性检查 (第一步)
   ├── 检查文件依赖是否存在
   ├── 验证CLI命令是否有实现
   ├── 确认配置系统一致性
   └── 验证模板和资源完整性

2. 🚨 发现严重问题时
   ├── Critical: 立即停止工作，拒绝生成任何代码
   ├── Warning: 警告并要求确认是否继续
   └── Info: 记录问题并在代码中标注

3. 🔧 问题修复建议
   ├── 提供具体的修复命令和步骤
   ├── 解释问题对用户的具体影响
   └── 验证修复后功能确实可用
```

---

## 🎯 **核心开发原则 (按新优先级)**

### 🔥 **P0 - 功能完整性原则 (绝对优先)**

#### 1. **文件依赖完整性**

```python
# ✅ 正确：确保引用的文件存在
def load_template(template_name: str):
    template_path = Path(f"templates/{template_name}")
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    return template_path.read_text()

# ❌ 错误：引用不存在的文件
def load_template(template_name: str):
    # 假设文件存在，不检查
    return Path(f"templates/{template_name}").read_text()  # 会失败！
```

#### 2. **CLI命令完整性**

```python
# ✅ 正确：CLI命令有完整实现
@click.command()
def create_project(name: str):
    """创建新项目"""
    try:
        # 验证模板存在
        template_dir = Path("templates/python")
        if not template_dir.exists():
            raise FileNotFoundError("Python模板不存在")

        # 执行实际创建逻辑
        project_path = Path(name)
        shutil.copytree(template_dir, project_path)
        click.echo(f"✅ 项目 {name} 创建成功")
        return True

    except Exception as e:
        click.echo(f"❌ 创建失败: {e}")
        return False

# ❌ 错误：空壳实现
@click.command()
def create_project(name: str):
    """创建新项目"""
    # TODO: 实现项目创建
    click.echo("项目创建功能开发中...")
    pass  # 用户什么都得不到！
```

#### 3. **配置系统一致性**

```python
# ✅ 正确：配置定义与使用一致
class CultureConfig:
    def __init__(self):
        self.config = {
            "culture": {
                "principles": ["solid", "dry", "kiss"],
                "tools": ["black", "flake8", "mypy"]
            }
        }

    def get_principle(self, name: str) -> List[str]:
        """返回指定原则的详细信息"""
        return self.config.get("culture", {}).get("principles", [])

# 使用方期望得到List[str]，确实得到List[str] ✅

# ❌ 错误：配置定义与使用不一致
class CultureConfig:
    def get_principle(self, name: str) -> List[str]:
        """声明返回List[str]"""
        return None  # 实际返回None！使用方会出错
```

#### 4. **模板系统完整性**

```python
# ✅ 正确：模板系统完整可用
def setup_project_template(project_type: str):
    """设置项目模板"""
    templates_dir = Path("aiculture/templates")
    template_path = templates_dir / project_type

    # 验证模板目录存在
    if not template_path.exists():
        raise ValueError(f"不支持的项目类型: {project_type}")

    # 验证模板包含必要文件
    required_files = ["pyproject.toml", "README.md", "requirements.txt"]
    missing_files = [f for f in required_files if not (template_path / f).exists()]

    if missing_files:
        raise ValueError(f"模板不完整，缺少文件: {missing_files}")

    return template_path

# ❌ 错误：假设模板存在
def setup_project_template(project_type: str):
    """设置项目模板"""
    # 直接返回路径，不验证存在性
    return Path(f"aiculture/templates/{project_type}")  # 可能不存在！
```

### 🏗️ **P0 - 基础设施原则 (第二优先级)**

#### 1. **环境隔离原则**

```python
# ✅ 正确：检查虚拟环境
import sys
if not hasattr(sys, 'real_prefix') and sys.prefix == sys.base_prefix:
    raise EnvironmentError("⚠️ 必须在虚拟环境中运行")

# ❌ 错误：在系统Python环境中开发
# 直接 pip install 到系统环境
```

#### 2. **配置外部化原则**

```python
# ✅ 正确：使用环境变量
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

# ❌ 错误：硬编码敏感信息
DATABASE_URL = "postgresql://user:password@localhost/mydb"
API_KEY = "sk-DEMO_API_KEY_PLACEHOLDER"  # 硬编码API密钥 (已脱敏)
```

#### 3. **依赖精确管理**

```python
# ✅ 正确：requirements.txt 精确版本
click==8.1.3
requests==2.28.2
pydantic==1.10.5

# ❌ 错误：版本范围过宽
click>=8.0.0
requests>=2.0.0
pydantic>=1.0.0
```

#### 4. **跨平台兼容性**

```python
# ✅ 正确：跨平台路径处理
from pathlib import Path
config_path = Path.home() / '.config' / 'myapp' / 'config.yaml'
data_dir = Path(__file__).parent / 'data'

# ❌ 错误：硬编码路径分隔符
config_path = "C:\\Users\\user\\.config\\myapp\\config.yaml"
data_dir = "/home/user/data"  # Unix specific
```

### 🔐 **P1 - 安全原则 (严格执行)**

#### 1. **输入验证**

```python
# ✅ 正确：严格输入验证
from pydantic import BaseModel, validator
class UserInput(BaseModel):
    email: str
    age: int

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# ❌ 错误：直接使用未验证输入
def process_user(user_data):
    email = user_data['email']  # 未验证
    query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL注入风险
```

#### 2. **密钥管理**

```python
# ✅ 正确：安全的密钥处理
import hashlib
import secrets
from cryptography.fernet import Fernet

# 生成安全的随机密钥
secret_key = secrets.token_urlsafe(32)
# 使用环境变量存储
encryption_key = os.getenv('ENCRYPTION_KEY')

# ❌ 错误：不安全的密钥处理
password = "123456"  # 弱密码
secret_key = "my_secret_key"  # 硬编码
hash_value = hashlib.md5(password.encode()).hexdigest()  # 弱哈希
```

### 📐 **P2 - SOLID原则**

#### 1. **单一职责原则 (SRP)**

```python
# ✅ 正确：单一职责
class UserValidator:
    def validate_user(self, user: dict) -> bool:
        return self._validate_email(user['email']) and self._validate_age(user['age'])

class UserRepository:
    def save_user(self, user: dict) -> None:
        # 只负责数据存储
        pass

class EmailNotifier:
    def send_welcome_email(self, email: str) -> None:
        # 只负责发送邮件
        pass

# ❌ 错误：职责混乱
class UserManager:
    def process_user(self, user: dict):
        # 验证用户
        if '@' not in user['email']:
            raise ValueError("Invalid email")

        # 保存到数据库
        db.save(user)

        # 发送邮件
        send_email(user['email'], "Welcome!")

        # 记录日志
        log.info(f"User {user['email']} processed")
```

#### 2. **依赖倒置原则 (DIP)**

```python
# ✅ 正确：依赖抽象
from abc import ABC, abstractmethod

class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, content: str) -> None:
        pass

class NotificationService:
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

class SMTPEmailSender(EmailSender):
    def send(self, to: str, content: str) -> None:
        # SMTP implementation
        pass

# ❌ 错误：依赖具体实现
class NotificationService:
    def __init__(self):
        self.smtp_client = smtplib.SMTP('localhost')  # 硬依赖
```

### 🧪 **P3 - 测试驱动开发**

```python
# ✅ 正确：测试驱动开发
import pytest
from myapp.calculator import Calculator

class TestCalculator:
    def test_add_positive_numbers(self):
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5

    def test_add_negative_numbers(self):
        calc = Calculator()
        result = calc.add(-2, -3)
        assert result == -5

    def test_divide_by_zero_raises_error(self):
        calc = Calculator()
        with pytest.raises(ZeroDivisionError):
            calc.divide(5, 0)

# ❌ 错误：没有测试
class Calculator:
    def add(self, a, b):
        return a + b  # 没有对应测试
```

---

## 🔍 **代码检查清单**

### 🚨 **进入项目必做检查 (按优先级)**

- [ ] **🎯 功能完整性检查**: 验证所有功能真正可用
- [ ] **⚡ CLI命令验证**: 确保命令有实际实现
- [ ] **📁 文件依赖检查**: 确认引用的文件存在
- [ ] **⚙️ 配置一致性**: 验证配置与代码匹配
- [ ] **🏗️ 基础设施检查**: 确认环境安全
- [ ] **🔐 安全扫描**: 检查常见安全漏洞

### 📋 **每次代码生成检查**

- [ ] **🎯 功能实现**: 确保代码有实际功能，不是空壳
- [ ] **🔗 依赖验证**: 确认所有引用的资源存在
- [ ] **🧪 测试覆盖**: 关键逻辑有对应测试
- [ ] **📐 SOLID原则**: 单一职责、依赖倒置
- [ ] **🔐 安全性**: 输入验证、错误处理
- [ ] **📝 文档**: 复杂逻辑有注释

### 🛠️ **修复优先级**

1. **🔥 Critical (立即停止工作)**
   - 功能缺失或空壳实现
   - 文件依赖不存在
   - 配置系统不一致
   - CLI命令无法执行

2. **⚠️ Warning (警告但可继续)**
   - 测试覆盖率不足
   - 端到端工作流问题
   - 环境配置问题

3. **💡 Info (建议改进)**
   - 文档不完整
   - 代码优化建议
   - 性能改进点

---

## 💬 **与用户沟通规范**

### 🚨 **发现严重功能问题时**

```
🚨 发现严重功能完整性问题！

❌ 问题：aiculture/templates目录不存在
🔥 影响：create命令完全无法工作，用户无法创建任何项目
💥 用户体验：用户运行命令后会遇到文件未找到错误

🔧 修复方案：
1. 创建templates目录：mkdir -p aiculture/templates
2. 添加Python模板：创建aiculture/templates/python/目录
3. 添加必要文件：pyproject.toml, README.md, requirements.txt
4. 验证模板可用：测试create命令成功运行

❌ 问题：CultureConfig.get_principle()返回None，但期望List[str]
🔥 影响：配置系统无法正常工作，所有依赖配置的功能失效
💥 用户体验：配置相关的CLI命令会崩溃

🔧 修复方案：
1. 修正方法返回类型：确保返回List[str]
2. 统一配置数据结构：定义明确的配置格式
3. 更新所有使用方：确保期望与实现一致
4. 添加配置验证测试：防止再次出现不一致

🚨 AI拒绝在功能不完整的环境中工作！
请先修复这些致命问题，确保基本功能可用后再继续开发。
```

### ✅ **功能检查通过时**

```
✅ 功能完整性检查通过！

🎯 核心功能验证：
   ✓ CLI命令完整可用
   ✓ 模板系统完整
   ✓ 配置系统一致
   ✓ 文件依赖完整

🏗️ 基础设施健康：
   ✓ 虚拟环境已激活
   ✓ Python版本: 3.11.9
   ✓ 依赖管理完整

🎉 环境安全且功能完整！现在可以进行高质量代码开发。

💡 有什么功能需要我帮助实现吗？
我会确保生成的代码：
• 功能完整且真正可用
• 符合所有开发文化标准
• 有完整的测试覆盖
• 遵循大厂级最佳实践
```

---

## 🚀 **总结**

作为AI助手，你的职责是：

1. **🎯 第一时间检查功能完整性** - 确保代码真正可用
2. **🚨 拒绝生成空壳代码** - 宁可不做也不做假
3. **🔗 验证端到端工作流** - 确保用户能达成目标
4. **🧪 强制测试覆盖** - 确保代码可靠性
5. **📐 遵循架构一致性** - 保证设计与实现匹配

**记住：功能完整性是底线，没有功能完整性就没有用户价值！** 🎯

```

## 3. 扩展核心功能，添加原则检查

```python:aiculture/culture_enforcer.py
"""
文化原则强制执行器

自动检查和强制执行开发文化原则，确保所有代码都符合标准。
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .ai_culture_principles import AICulturePrinciples, PrincipleCategory


@dataclass
class Violation:
    """违规记录"""
    principle: str
    severity: str  # error, warning, info
    file_path: str
    line_number: int
    description: str
    suggestion: str


class CultureEnforcer:
    """文化原则强制执行器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.principles = AICulturePrinciples()
        self.violations: List[Violation] = []

    def enforce_all(self) -> Dict[str, Any]:
        """执行所有原则检查"""
        self.violations.clear()

        # 检查项目结构
        self._check_project_structure()

        # 检查代码质量
        self._check_code_quality()

        # 检查安全问题
        self._check_security()

        # 检查测试覆盖率
        self._check_test_coverage()

        # 检查文档完整性
        self._check_documentation()

        return self._generate_report()

    def _check_project_structure(self):
        """检查项目结构是否符合标准"""
        required_files = [
            "README.md",
            ".gitignore",
            "requirements.txt",  # 或 pyproject.toml
            ".pre-commit-config.yaml"
        ]

        for file_name in required_files:
            if not (self.project_path / file_name).exists():
                self.violations.append(Violation(
                    principle="project_structure",
                    severity="error",
                    file_path=file_name,
                    line_number=0,
                    description=f"缺少必要文件: {file_name}",
                    suggestion=f"创建 {file_name} 文件"
                ))

        # 检查测试目录
        if not (self.project_path / "tests").exists():
            self.violations.append(Violation(
                principle="testing",
                severity="warning",
                file_path="tests/",
                line_number=0,
                description="缺少测试目录",
                suggestion="创建 tests/ 目录并添加测试用例"
            ))

    def _check_code_quality(self):
        """检查代码质量原则"""
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            if "venv" in str(file_path) or ".git" in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查SOLID原则
                self._check_solid_principles(file_path, content)

                # 检查DRY原则
                self._check_dry_principle(file_path, content)

                # 检查KISS原则
                self._check_kiss_principle(file_path, content)

            except Exception as e:
                print(f"无法分析文件 {file_path}: {e}")

    def _check_solid_principles(self, file_path: Path, content: str):
        """检查SOLID原则"""
        try:
            tree = ast.parse(content)

            # 检查单一职责原则
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 10:  # 简单的启发式规则
                        self.violations.append(Violation(
                            principle="solid_srp",
                            severity="warning",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"类 {node.name} 可能违反单一职责原则 (方法数: {len(methods)})",
                            suggestion="考虑将类拆分为更小的、职责单一的类"
                        ))

        except SyntaxError:
            pass  # 跳过语法错误的文件

    def _check_dry_principle(self, file_path: Path, content: str):
        """检查DRY原则"""
        lines = content.split('\n')
        line_counts = {}

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 20:
                if line in line_counts:
                    line_counts[line].append(i)
                else:
                    line_counts[line] = [i]

        # 检查重复代码
        for line, occurrences in line_counts.items():
            if len(occurrences) >= 3:  # 出现3次以上认为是重复
                self.violations.append(Violation(
                    principle="dry",
                    severity="warning",
                    file_path=str(file_path),
                    line_number=occurrences[0],
                    description=f"检测到重复代码: '{line[:50]}...'",
                    suggestion="考虑将重复代码提取为函数或常量"
                ))

    def _check_kiss_principle(self, file_path: Path, content: str):
        """检查KISS原则"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数复杂度
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:  # 圈复杂度阈值
                        self.violations.append(Violation(
                            principle="kiss",
                            severity="warning",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"函数 {node.name} 复杂度过高 (复杂度: {complexity})",
                            suggestion="考虑将函数拆分为更小的函数"
                        ))

        except SyntaxError:
            pass

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数的圈复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_security(self):
        """检查安全问题"""
        try:
            # 使用bandit进行安全检查
            result = subprocess.run(
                ["bandit", "-r", str(self.project_path), "-f", "json"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                import json
                bandit_results = json.loads(result.stdout)

                for issue in bandit_results.get('results', []):
                    self.violations.append(Violation(
                        principle="security",
                        severity=issue['issue_severity'].lower(),
                        file_path=issue['filename'],
                        line_number=issue['line_number'],
                        description=issue['issue_text'],
                        suggestion=f
