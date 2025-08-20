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
```

## 2. 创建AI助手指导文档

```markdown:AI_ASSISTANT_GUIDELINES.md
# AI助手开发指导原则 🤖

> 本文档为所有参与此项目的AI助手提供标准化的开发指导原则

## 🎯 核心使命

作为AI开发助手，你的核心使命是：
1. **严格遵循大厂级开发标准**
2. **确保代码质量和可维护性**
3. **促进团队协作和知识共享**
4. **推动最佳实践的落地执行**

## 📋 必须遵循的开发原则

### 🏗️ 代码质量原则

#### SOLID原则 (强制执行)
- **单一职责原则**: 每个类、函数只做一件事
- **开放封闭原则**: 对扩展开放，对修改封闭
- **里氏替换原则**: 子类可以替换父类
- **接口隔离原则**: 接口要小而专注
- **依赖倒置原则**: 依赖抽象而非具体实现

**AI执行指令**:
```
在编写任何代码前，问自己：
1. 这个类/函数是否只有一个改变的理由？
2. 我是否可以在不修改现有代码的情况下扩展功能？
3. 我是否使用了合适的抽象层？
```

#### DRY原则 (强制执行)
- 发现重复代码立即重构
- 创建工具函数消除重复逻辑
- 使用配置文件而非硬编码

**AI执行指令**:
```
<code_block_to_apply_changes_from>
```

#### KISS原则 (强制执行)
- 保持解决方案简单直接
- 避免过度工程化
- 优先选择可读性高的方案

### 🏛️ 架构设计原则

#### 微服务架构
- 按业务域拆分服务
- 服务间松耦合
- 独立部署和扩展
- API优先设计

**AI执行指令**:
```
设计服务时考虑：
1. 这个服务的业务边界是什么？
2. 它是否可以独立运行和部署？
3. API设计是否RESTful且一致？
```

#### 可扩展性设计
- 水平扩展优于垂直扩展
- 状态外部化
- 异步处理非关键任务

### 🔒 安全原则

#### 数据安全 (严格执行)
- **永远不信任用户输入**
- 使用参数化查询
- 实施输入验证和输出编码
- 敏感数据加密存储

**AI执行指令**:
```python
# 好的做法
def get_user(user_id: int) -> User:
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# 坏的做法  
def get_user(user_id: str) -> User:
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

#### 认证授权
- 实施多因素认证
- 基于角色的访问控制
- JWT令牌管理

### 🧪 测试原则

#### 测试金字塔 (强制执行)
- 单元测试 (70%)
- 集成测试 (20%) 
- E2E测试 (10%)
- 代码覆盖率 ≥ 80%

**AI执行指令**:
```
为每个函数编写测试时：
1. 测试正常路径
2. 测试边界条件
3. 测试异常情况
4. 使用有意义的测试名称
```

#### TDD/BDD实践
- 先写测试再写实现
- 测试驱动设计决策
- 行为驱动开发

### 🔄 CI/CD原则

#### 持续集成 (强制执行)
- 每次提交触发自动化构建
- 所有检查通过才能合并
- 强制代码审查

**工作流检查清单**:
- [ ] 代码格式化检查 (black, prettier)
- [ ] 静态分析 (flake8, eslint, mypy)
- [ ] 安全扫描 (bandit, safety)
- [ ] 单元测试覆盖率
- [ ] 集成测试
- [ ] 文档更新

#### 持续部署
- 自动化部署流程
- 蓝绿部署策略
- 快速回滚机制

### ⚡ 性能原则

#### 响应时间要求
- API响应 < 200ms
- 页面加载 < 3s
- 数据库查询优化

**AI执行指令**:
```
优化性能时考虑：
1. 是否可以添加缓存？
2. 数据库查询是否已优化？
3. 是否可以异步处理？
4. 资源是否按需加载？
```

#### 可扩展性
- 水平扩展设计
- 负载均衡
- 缓存策略

### 📚 文档原则

#### 必要文档 (强制执行)
- README.md (快速开始指南)
- API文档 (Swagger/OpenAPI)
- 架构决策记录 (ADR)
- 变更日志 (CHANGELOG.md)

**AI执行指令**:
```
编写文档时：
1. 用户能否在5分钟内运行项目？
2. API文档是否包含完整示例？
3. 重要决策是否有记录？
```

## 🛠️ 强制使用的工具

### Python项目
```yaml
formatter: black
linter: [flake8, mypy]
import_sorter: isort
security: bandit
testing: pytest
coverage: pytest-cov
pre_commit: pre-commit
```

### JavaScript/TypeScript项目
```yaml
formatter: prettier
linter: eslint
type_checker: typescript
testing: jest
bundler: webpack/vite
```

### 通用工具
```yaml
version_control: git
ci_cd: github-actions
containerization: docker
documentation: sphinx/mkdocs
monitoring: prometheus
```

## 🤖 AI助手行为规范

### 代码编写行为
1. **先分析需求**，确保理解业务逻辑
2. **设计优于实现**，先考虑架构再编码
3. **测试驱动**，先写测试用例
4. **重构友好**，编写易于修改的代码
5. **文档同步**，代码和文档同时更新

### 代码审查行为
1. **检查原则合规性**，确保遵循所有开发原则
2. **性能和安全审查**，识别潜在问题
3. **可读性评估**，确保代码易于理解
4. **测试覆盖率**，验证测试的完整性

### 问题解决行为
1. **根本原因分析**，不仅解决表面问题
2. **最佳实践应用**，采用行业标准解决方案
3. **知识分享**，记录解决过程和经验
4. **持续改进**，从问题中学习并优化流程

## 🚫 绝对禁止的行为

### 代码质量
- ❌ 提交未经测试的代码
- ❌ 硬编码配置信息
- ❌ 忽略代码审查意见
- ❌ 跳过代码格式化

### 安全相关
- ❌ 提交包含密钥的代码
- ❌ 跳过输入验证
- ❌ 使用不安全的库版本
- ❌ 明文存储敏感信息

### 协作规范
- ❌ 直接推送到主分支
- ❌ 不写提交信息
- ❌ 不更新文档
- ❌ 忽略CI/CD检查失败

## 📊 质量检查清单

每次代码提交前，AI助手必须确认：

### 代码质量检查
- [ ] 遵循SOLID原则
- [ ] 无重复代码 (DRY)
- [ ] 代码简洁易读 (KISS)
- [ ] 有意义的命名
- [ ] 适当的注释

### 安全检查
- [ ] 输入验证完整
- [ ] 无SQL注入风险
- [ ] 敏感数据已加密
- [ ] 认证授权正确
- [ ] 无硬编码密钥

### 测试检查
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 测试用例完整
- [ ] 边界条件测试
- [ ] 异常处理测试
- [ ] 集成测试通过

### 文档检查
- [ ] README更新
- [ ] API文档完整
- [ ] 代码注释充分
- [ ] 变更日志更新
- [ ] 示例代码正确

### CI/CD检查
- [ ] 所有自动化检查通过
- [ ] 代码审查完成
- [ ] 部署脚本测试
- [ ] 回滚方案准备
- [ ] 监控配置更新

## 🎓 持续学习要求

AI助手应该：
1. **跟踪技术趋势**，了解最新最佳实践
2. **学习团队反馈**，从代码审查中改进
3. **分析生产问题**，避免重复错误
4. **优化开发流程**，提高团队效率

## 📞 升级处理

遇到以下情况时，AI助手应该寻求人工指导：
1. **原则冲突**：不同原则之间存在矛盾
2. **架构决策**：重大技术选型需要讨论
3. **安全问题**：发现严重安全漏洞
4. **性能瓶颈**：优化方案需要权衡
5. **业务逻辑**：需要澄清业务需求

---

**记住：质量不是检查出来的，而是构建出来的。每一行代码都应该达到生产级标准。**

*最后更新: 2024年1月*
*版本: 1.0*
*维护者: AICultureKit Team*
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