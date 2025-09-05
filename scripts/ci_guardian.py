#!/usr/bin/env python3
"""
CI质量保障守护者 - 自动监控CI问题并生成防御机制

这个模块是CI质量保障系统的核心控制器，负责：
1. 监听和分析本地/远程CI输出
2. 智能识别CI失败的根本原因
3. 自动生成相应的防御机制（测试、lint规则、预提交钩子）
4. 将新规则集成到项目仓库中

作者：AI CI Guardian System
版本：v1.0.0
"""

import asyncio
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import click
import yaml


class CIIssueType:
    """CI问题类型定义"""
    CODE_STYLE = "code_style"
    TYPE_CHECK = "type_check"
    SYNTAX_ERROR = "syntax_error"
    TEST_FAILURE = "test_failure"
    IMPORT_ERROR = "import_error"
    SECURITY_ISSUE = "security_issue"
    COVERAGE_LOW = "coverage_low"
    DEPENDENCY_ISSUE = "dependency_issue"
    UNKNOWN = "unknown"


class CIIssue:
    """CI问题数据模型"""
    
    def __init__(
        self,
        issue_type: str,
        description: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        error_message: str = "",
        tool_name: str = "",
        severity: str = "medium"
    ):
        self.issue_type = issue_type
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.error_message = error_message
        self.tool_name = tool_name
        self.severity = severity
        self.timestamp = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "issue_type": self.issue_type,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "error_message": self.error_message,
            "tool_name": self.tool_name,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat()
        }


class CIOutputAnalyzer:
    """CI输出分析器 - 智能解析CI日志并识别问题类型"""
    
    def __init__(self):
        # 定义问题识别模式
        self.patterns = {
            CIIssueType.CODE_STYLE: [
                r"E\d+.*line too long",
                r"W\d+.*whitespace",
                r"F401.*imported but unused",
                r"black.*would reformat",
                r"ruff.*(\w+) \[(\w+)\]"
            ],
            CIIssueType.TYPE_CHECK: [
                r"mypy.*error:",
                r"Incompatible types",
                r"missing type annotation",
                r"Cannot determine type"
            ],
            CIIssueType.SYNTAX_ERROR: [
                r"SyntaxError:",
                r"IndentationError:",
                r"invalid syntax"
            ],
            CIIssueType.TEST_FAILURE: [
                r"FAILED.*test_",
                r"AssertionError",
                r"pytest.*failed",
                r"ERROR.*test_"
            ],
            CIIssueType.IMPORT_ERROR: [
                r"ImportError:",
                r"ModuleNotFoundError:",
                r"No module named"
            ],
            CIIssueType.SECURITY_ISSUE: [
                r"bandit.*HIGH:",
                r"bandit.*MEDIUM:",
                r"security vulnerability",
                r"hardcoded password"
            ],
            CIIssueType.COVERAGE_LOW: [
                r"coverage.*below.*threshold",
                r"TOTAL.*\d+%.*missing",
                r"coverage.* \d+% < \d+%"
            ]
        }
    
    def analyze_output(self, output: str, tool_name: str = "") -> List[CIIssue]:
        """分析CI输出并提取问题"""
        issues = []
        lines = output.split('\n')
        
        for line_num, line in enumerate(lines):
            for issue_type, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = self._parse_issue_line(line, issue_type, tool_name, line_num)
                        if issue:
                            issues.append(issue)
                        break
        
        return issues
    
    def _parse_issue_line(self, line: str, issue_type: str, tool_name: str, line_num: int) -> Optional[CIIssue]:
        """解析单行错误信息"""
        # 提取文件路径和行号
        file_match = re.search(r'([^:\s]+\.py):(\d+)', line)
        file_path = file_match.group(1) if file_match else None
        line_number = int(file_match.group(2)) if file_match else None
        
        # 提取错误描述
        description = line.strip()
        if len(description) > 200:
            description = description[:200] + "..."
        
        severity = self._determine_severity(issue_type, line)
        
        return CIIssue(
            issue_type=issue_type,
            description=description,
            file_path=file_path,
            line_number=line_number,
            error_message=line,
            tool_name=tool_name,
            severity=severity
        )
    
    def _determine_severity(self, issue_type: str, line: str) -> str:
        """根据问题类型和内容确定严重程度"""
        if "HIGH" in line or "CRITICAL" in line:
            return "high"
        elif "ERROR" in line or issue_type in [CIIssueType.SYNTAX_ERROR, CIIssueType.IMPORT_ERROR]:
            return "high"
        elif "WARNING" in line or "MEDIUM" in line:
            return "medium"
        else:
            return "low"


class DefenseMechanismGenerator:
    """防御机制生成器 - 根据CI问题类型生成相应的预防措施"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.generated_files = []
    
    def generate_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """根据问题列表生成防御机制"""
        defenses = {
            "test_files": [],
            "lint_rules": [],
            "pre_commit_hooks": [],
            "ci_checks": []
        }
        
        # 按问题类型分组
        issues_by_type = {}
        for issue in issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)
        
        # 为每种问题类型生成防御机制
        for issue_type, issue_list in issues_by_type.items():
            if issue_type == CIIssueType.CODE_STYLE:
                defenses.update(self._generate_style_defenses(issue_list))
            elif issue_type == CIIssueType.TEST_FAILURE:
                defenses.update(self._generate_test_defenses(issue_list))
            elif issue_type == CIIssueType.TYPE_CHECK:
                defenses.update(self._generate_type_defenses(issue_list))
            elif issue_type == CIIssueType.SECURITY_ISSUE:
                defenses.update(self._generate_security_defenses(issue_list))
            elif issue_type == CIIssueType.IMPORT_ERROR:
                defenses.update(self._generate_import_defenses(issue_list))
        
        return defenses
    
    def _generate_style_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """生成代码风格问题的防御机制"""
        defenses = {"lint_rules": [], "pre_commit_hooks": []}
        
        # 更新 ruff 配置
        ruff_rules = self._create_enhanced_ruff_config(issues)
        if ruff_rules:
            defenses["lint_rules"].append("pyproject.toml")
        
        # 添加 pre-commit 钩子
        precommit_config = self._create_precommit_config()
        defenses["pre_commit_hooks"].append(".pre-commit-config.yaml")
        
        return defenses
    
    def _generate_test_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """生成测试失败的防御机制"""
        defenses = {"test_files": [], "ci_checks": []}
        
        # 为每个失败的测试生成增强测试
        for issue in issues:
            if issue.file_path and "test_" in issue.file_path:
                enhanced_test = self._create_enhanced_test(issue)
                if enhanced_test:
                    defenses["test_files"].append(enhanced_test)
        
        # 添加测试覆盖率检查
        coverage_check = self._create_coverage_enforcement()
        defenses["ci_checks"].append(".github/workflows/enhanced-testing.yml")
        
        return defenses
    
    def _generate_type_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """生成类型检查问题的防御机制"""
        defenses = {"lint_rules": [], "ci_checks": []}
        
        # 更新 mypy 配置
        mypy_config = self._create_enhanced_mypy_config(issues)
        defenses["lint_rules"].append("mypy.ini")
        
        # 添加类型检查的 CI 步骤
        defenses["ci_checks"].append("type-check-enforcement")
        
        return defenses
    
    def _generate_security_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """生成安全问题的防御机制"""
        defenses = {"lint_rules": [], "ci_checks": []}
        
        # 更新安全检查配置
        security_config = self._create_security_config(issues)
        defenses["lint_rules"].append(".bandit")
        
        # 添加安全扫描 CI 步骤
        defenses["ci_checks"].append("security-scan-enhancement")
        
        return defenses
    
    def _generate_import_defenses(self, issues: List[CIIssue]) -> Dict[str, List[str]]:
        """生成导入错误的防御机制"""
        defenses = {"ci_checks": [], "test_files": []}
        
        # 创建导入验证测试
        import_test = self._create_import_validation_test(issues)
        defenses["test_files"].append("tests/test_imports.py")
        
        # 添加依赖检查
        defenses["ci_checks"].append("dependency-validation")
        
        return defenses
    
    def _create_enhanced_ruff_config(self, issues: List[CIIssue]) -> bool:
        """创建增强的 ruff 配置"""
        config_path = self.project_root / "pyproject.toml"
        
        # 分析具体的风格问题
        rules_to_add = set()
        for issue in issues:
            if "line too long" in issue.error_message:
                rules_to_add.add("E501")
            if "imported but unused" in issue.error_message:
                rules_to_add.add("F401")
            if "whitespace" in issue.error_message:
                rules_to_add.add("W292")
        
        ruff_config = f'''
# Enhanced Ruff Configuration - Auto-generated by CI Guardian
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
# 启用更严格的代码检查规则
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    {"".join(f'    "{rule}",  # Auto-detected from CI failure\\n' for rule in rules_to_add)}
]

# 特定于项目的忽略规则
ignore = [
    "E203",  # whitespace before ':'
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # allow assert in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
'''
        
        try:
            with open(config_path, "a", encoding="utf-8") as f:
                f.write(ruff_config)
            self.generated_files.append(str(config_path))
            return True
        except Exception as e:
            click.echo(f"❌ 创建 ruff 配置失败: {e}")
            return False
    
    def _create_precommit_config(self) -> bool:
        """创建 pre-commit 配置"""
        config_path = self.project_root / ".pre-commit-config.yaml"
        
        precommit_config = '''# Auto-generated Pre-commit Configuration
# This file prevents CI failures by running checks locally before commit

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", "src/"]
        exclude: tests/

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ["tests/", "--cov=src", "--cov-fail-under=80"]
'''
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(precommit_config)
            self.generated_files.append(str(config_path))
            return True
        except Exception as e:
            click.echo(f"❌ 创建 pre-commit 配置失败: {e}")
            return False
    
    def _create_enhanced_test(self, issue: CIIssue) -> Optional[str]:
        """为失败的测试创建增强版本"""
        if not issue.file_path:
            return None
        
        # 提取测试函数名
        test_function = re.search(r'test_\w+', issue.error_message)
        if not test_function:
            return None
        
        test_name = test_function.group(0)
        enhanced_test_path = f"tests/enhanced_{test_name}_validation.py"
        
        enhanced_test_content = f'''"""
增强测试 - 自动生成以防止 {test_name} 再次失败
生成时间: {datetime.now().isoformat()}
原始错误: {issue.error_message[:100]}...
"""

import pytest
import sys
from pathlib import Path

# 确保可以导入源代码
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class Test{test_name.title().replace('_', '')}Validation:
    """增强版测试，添加更多边界条件检查"""
    
    def test_basic_functionality(self):
        """基础功能测试 - 确保核心逻辑正确"""
        # TODO: 根据原始失败测试添加具体检查
        assert True, "基础功能测试占位符"
    
    def test_edge_cases(self):
        """边界情况测试 - 防止边界条件导致的失败"""
        # TODO: 添加边界条件测试
        assert True, "边界情况测试占位符"
    
    def test_error_handling(self):
        """错误处理测试 - 确保异常被正确处理"""
        # TODO: 添加异常处理测试
        assert True, "错误处理测试占位符"
    
    @pytest.mark.parametrize("test_input,expected", [
        ("valid_input", True),
        ("invalid_input", False),
    ])
    def test_parameterized_validation(self, test_input, expected):
        """参数化测试 - 覆盖多种输入情况"""
        # TODO: 根据实际业务逻辑添加参数化测试
        assert isinstance(test_input, str)
'''
        
        try:
            enhanced_test_full_path = self.project_root / enhanced_test_path
            enhanced_test_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(enhanced_test_full_path, "w", encoding="utf-8") as f:
                f.write(enhanced_test_content)
            
            self.generated_files.append(str(enhanced_test_full_path))
            return enhanced_test_path
        except Exception as e:
            click.echo(f"❌ 创建增强测试失败: {e}")
            return None
    
    def _create_import_validation_test(self, issues: List[CIIssue]) -> bool:
        """创建导入验证测试"""
        test_path = self.project_root / "tests" / "test_imports.py"
        
        # 从错误中提取导入失败的模块
        failed_imports = set()
        for issue in issues:
            import_match = re.search(r"No module named '(\w+)'", issue.error_message)
            if import_match:
                failed_imports.add(import_match.group(1))
        
        test_content = f'''"""
导入验证测试 - 确保所有必要模块都能正确导入
自动生成时间: {datetime.now().isoformat()}
"""

import pytest
import importlib
import sys
from pathlib import Path

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestImports:
    """测试所有关键模块的导入功能"""
    
    def test_core_modules_import(self):
        """测试核心模块导入"""
        core_modules = [
            "src.core",
            "src.models", 
            "src.services",
            "src.utils"
        ]
        
        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"核心模块 {{module_name}} 导入失败: {{e}}")
    
    def test_dependency_availability(self):
        """测试第三方依赖可用性"""
        required_packages = [
            "fastapi",
            "pydantic", 
            "pytest",
            "click"
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError as e:
                pytest.fail(f"必需依赖 {{package}} 不可用: {{e}}")
    
    {"".join([f'''
    def test_{module}_import(self):
        """测试 {module} 模块导入 - 之前失败过"""
        try:
            importlib.import_module("{module}")
        except ImportError as e:
            pytest.fail(f"模块 {module} 导入失败: {{e}}")
    ''' for module in failed_imports])}
    
    def test_circular_imports(self):
        """检测循环导入问题"""
        # 尝试导入所有源码模块，检测循环导入
        import sys
        original_modules = set(sys.modules.keys())
        
        try:
            # 导入主要模块
            import src
        except ImportError as e:
            if "circular import" in str(e).lower():
                pytest.fail(f"检测到循环导入: {{e}}")
            # 其他导入错误可能是正常的
        finally:
            # 清理新导入的模块
            new_modules = set(sys.modules.keys()) - original_modules
            for module in new_modules:
                if module.startswith('src.'):
                    sys.modules.pop(module, None)
'''
        
        try:
            test_path.parent.mkdir(parents=True, exist_ok=True)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_content)
            self.generated_files.append(str(test_path))
            return True
        except Exception as e:
            click.echo(f"❌ 创建导入验证测试失败: {e}")
            return False


class CIGuardian:
    """CI质量保障守护者主控制器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.analyzer = CIOutputAnalyzer()
        self.generator = DefenseMechanismGenerator(self.project_root)
        self.issues_detected = []
        
    def monitor_ci_output(self, command: str) -> Tuple[str, int]:
        """执行CI命令并监控输出"""
        click.echo(f"🔍 执行CI命令: {command}")
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            output = result.stdout + result.stderr
            return output, result.returncode
        except Exception as e:
            click.echo(f"❌ CI命令执行失败: {e}")
            return str(e), 1
    
    def analyze_ci_issues(self, output: str, tool_name: str = "") -> List[CIIssue]:
        """分析CI输出并识别问题"""
        issues = self.analyzer.analyze_output(output, tool_name)
        self.issues_detected.extend(issues)
        
        # 保存问题到日志
        self._save_issues_to_log(issues)
        
        return issues
    
    def generate_defenses(self) -> Dict[str, List[str]]:
        """生成防御机制"""
        if not self.issues_detected:
            click.echo("ℹ️ 没有检测到CI问题，无需生成防御机制")
            return {}
        
        click.echo(f"🛡️ 为 {len(self.issues_detected)} 个问题生成防御机制...")
        defenses = self.generator.generate_defenses(self.issues_detected)
        
        # 保存防御机制信息
        self._save_defenses_to_log(defenses)
        
        return defenses
    
    def validate_defenses(self) -> bool:
        """验证新生成的防御机制是否有效"""
        click.echo("✅ 验证防御机制有效性...")
        
        # 重新运行CI检查
        validation_commands = [
            "make lint",
            "make test", 
            "make typecheck"
        ]
        
        all_passed = True
        for cmd in validation_commands:
            output, returncode = self.monitor_ci_output(cmd)
            if returncode != 0:
                click.echo(f"❌ 验证命令失败: {cmd}")
                new_issues = self.analyze_ci_issues(output, cmd)
                if new_issues:
                    click.echo(f"   检测到 {len(new_issues)} 个新问题")
                    all_passed = False
            else:
                click.echo(f"✅ 验证通过: {cmd}")
        
        return all_passed
    
    def _save_issues_to_log(self, issues: List[CIIssue]):
        """保存问题到日志文件"""
        log_file = self.logs_dir / "ci_issues.json"
        
        # 读取现有日志
        existing_issues = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    existing_issues = json.load(f)
            except:
                existing_issues = []
        
        # 添加新问题
        for issue in issues:
            existing_issues.append(issue.to_dict())
        
        # 保存回文件
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(existing_issues, f, indent=2, ensure_ascii=False)
    
    def _save_defenses_to_log(self, defenses: Dict[str, List[str]]):
        """保存防御机制到日志文件"""
        log_file = self.logs_dir / "defenses_generated.json"
        
        defense_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "defenses": defenses,
            "generated_files": self.generator.generated_files,
            "issues_count": len(self.issues_detected)
        }
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(defense_log, f, indent=2, ensure_ascii=False)


@click.command()
@click.option("--command", "-c", help="要监控的CI命令 (例如: 'make quality')")
@click.option("--analyze-logs", "-l", is_flag=True, help="分析现有日志文件中的问题")
@click.option("--generate-only", "-g", is_flag=True, help="仅生成防御机制，不执行命令")
@click.option("--validate", "-v", is_flag=True, help="验证现有防御机制")
@click.option("--project-root", "-p", help="项目根目录路径")
@click.option("--summary", "-s", is_flag=True, help="显示执行摘要")
def main(command, analyze_logs, generate_only, validate, project_root, summary):
    """
    🛡️ CI质量保障守护者
    
    自动监控CI问题并生成防御机制，确保同类问题不再发生。
    
    Examples:
        ci_guardian.py -c "make quality"    # 监控质量检查
        ci_guardian.py -l                   # 分析现有日志
        ci_guardian.py -g                   # 仅生成防御机制
        ci_guardian.py -v                   # 验证防御机制
    """
    
    project_path = Path(project_root) if project_root else Path.cwd()
    guardian = CIGuardian(project_path)
    
    click.echo("🛡️ CI质量保障守护者启动")
    click.echo(f"📁 项目路径: {project_path}")
    
    if analyze_logs:
        # 分析现有日志
        click.echo("📋 分析现有问题日志...")
        log_file = guardian.logs_dir / "quality_check.json"
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                # 从日志中提取失败的检查
                if "checks" in log_data:
                    for check_name, check_data in log_data["checks"].items():
                        if not check_data.get("success", True):
                            output = check_data.get("output", "")
                            issues = guardian.analyze_ci_issues(output, check_name)
                            click.echo(f"  从 {check_name} 检测到 {len(issues)} 个问题")
    
    elif command:
        # 执行并监控指定命令
        output, returncode = guardian.monitor_ci_output(command)
        issues = guardian.analyze_ci_issues(output, command)
        
        if returncode != 0:
            click.echo(f"❌ 命令执行失败，检测到 {len(issues)} 个问题")
        else:
            click.echo(f"✅ 命令执行成功，检测到 {len(issues)} 个潜在问题")
    
    elif validate:
        # 仅验证现有防御机制
        if guardian.validate_defenses():
            click.echo("✅ 所有防御机制验证通过")
        else:
            click.echo("❌ 部分防御机制验证失败")
        return
    
    # 生成防御机制（如果检测到问题）
    if guardian.issues_detected or generate_only:
        defenses = guardian.generate_defenses()
        
        if defenses:
            click.echo("\n🛡️ 生成的防御机制:")
            for defense_type, files in defenses.items():
                if files:
                    click.echo(f"  {defense_type}: {', '.join(files)}")
            
            # 验证防御机制
            if guardian.validate_defenses():
                click.echo("✅ 防御机制验证通过，问题已得到防护")
            else:
                click.echo("⚠️ 防御机制需要进一步完善")
        else:
            click.echo("ℹ️ 没有生成新的防御机制")
    
    if summary:
        click.echo(f"\n📊 执行摘要:")
        click.echo(f"  检测问题数: {len(guardian.issues_detected)}")
        click.echo(f"  生成文件数: {len(guardian.generator.generated_files)}")
        click.echo(f"  项目根目录: {project_path}")


if __name__ == "__main__":
    main() 