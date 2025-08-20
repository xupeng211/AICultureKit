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