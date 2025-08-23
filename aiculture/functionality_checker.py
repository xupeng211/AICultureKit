#!/usr/bin/env python3
"""
🎯 功能完整性检查器 - P0级别检查

这个模块负责检查项目的功能完整性，确保所有功能都能真正工作，
防止出现"代码结构完美但功能缺失"的致命问题。
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FunctionalityViolation:
    """功能完整性违规记录"""

    category: str
    severity: str  # "critical", "warning", "info"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    impact: Optional[str] = None  # 对用户的影响


class FunctionalityChecker:
    """功能完整性检查器 - 确保代码功能真正可用"""

    def __init__(self, project_path: Path) -> None:
        """初始化功能完整性检查器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.violations: List[FunctionalityViolation] = []

    def check_all_functionality(self) -> List[FunctionalityViolation]:
        """执行所有功能完整性检查

        Returns:
            发现的违规列表
        """
        self.violations.clear()

        print("🎯 开始功能完整性检查...")

        # P0检查：文件依赖完整性
        self._check_file_dependencies()

        # P0检查：CLI命令完整性
        self._check_cli_functionality()

        # P0检查：配置系统一致性
        self._check_configuration_consistency()

        # P0检查：模板系统完整性
        self._check_template_system()

        # P1检查：测试覆盖率
        self._check_test_coverage()

        # P1检查：端到端工作流
        self._check_end_to_end_workflows()

        # P1检查：依赖可用性
        self._check_dependency_availability()

        return self.violations

    def _add_violation(
        self,
        category: str,
        severity: str,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
        impact: Optional[str] = None,
    ) -> None:
        """添加违规记录"""
        self.violations.append(
            FunctionalityViolation(
                category=category,
                severity=severity,
                message=message,
                file_path=file_path,
                line_number=line_number,
                suggestion=suggestion,
                impact=impact,
            )
        )

    # P0检查：文件依赖完整性

    def _check_file_dependencies(self) -> None:
        """检查代码中引用的文件是否真实存在"""
        print("📁 检查文件依赖完整性...")

        python_files = list(self.project_path.rglob("*.py"))

        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                self._check_file_references_in_code(py_file, content)
            except (UnicodeDecodeError, PermissionError):
                continue

    def _check_file_references_in_code(self, py_file: Path, content: str) -> None:
        """检查代码中的文件引用"""
        lines = content.split("\n")

        # 检查路径字符串
        path_patterns = [
            r'["\']([^"\']*\.(?:yaml|yml|json|txt|md|py|sh))["\']',  # 配置文件
            r'Path\(["\']([^"\']+)["\']',  # Path()调用
            r'open\(["\']([^"\']+)["\']',  # open()调用
        ]

        for i, line in enumerate(lines, 1):
            for pattern in path_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    self._validate_file_reference(py_file, match, i)

    def _validate_file_reference(
        self, source_file: Path, file_ref: str, line_num: int
    ) -> None:
        """验证文件引用是否存在"""
        # 跳过明显的示例和变量
        if any(
            skip in file_ref.lower()
            for skip in ["example", "demo", "test", "temp", "$", "{"]
        ):
            return

        # 构建可能的文件路径
        possible_paths = [
            self.project_path / file_ref,
            source_file.parent / file_ref,
            self.project_path / "aiculture" / file_ref,
        ]

        # 检查是否存在
        exists = any(path.exists() for path in possible_paths)

        if not exists:
            self._add_violation(
                category="文件依赖完整性",
                severity="critical",
                message=f"引用的文件不存在: {file_ref}",
                file_path=str(source_file),
                line_number=line_num,
                suggestion=f"创建文件 {file_ref} 或修正路径引用",
                impact="功能无法正常工作，用户会遇到文件未找到错误",
            )

    # P0检查：CLI命令完整性

    def _check_cli_functionality(self) -> None:
        """检查CLI命令的功能完整性"""
        print("⚡ 检查CLI命令完整性...")

        cli_file = self.project_path / "aiculture" / "cli.py"
        if not cli_file.exists():
            self._add_violation(
                category="CLI完整性",
                severity="critical",
                message="CLI入口文件不存在",
                suggestion="创建aiculture/cli.py文件",
                impact="所有CLI命令都无法使用",
            )
            return

        try:
            content = cli_file.read_text(encoding="utf-8")
            self._analyze_cli_commands(cli_file, content)
        except Exception as e:
            self._add_violation(
                category="CLI完整性",
                severity="critical",
                message=f"CLI文件无法解析: {e}",
                file_path=str(cli_file),
                impact="CLI命令可能无法正常工作",
            )

    def _analyze_cli_commands(self, cli_file: Path, content: str) -> None:
        """分析CLI命令的实现完整性"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否为click命令
                    if self._is_click_command(node):
                        self._validate_cli_command_implementation(cli_file, node)

        except SyntaxError as e:
            self._add_violation(
                category="CLI完整性",
                severity="critical",
                message=f"CLI文件语法错误: {e}",
                file_path=str(cli_file),
                impact="CLI命令无法执行",
            )

    def _is_click_command(self, node: ast.FunctionDef) -> bool:
        """检查函数是否为click命令"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if getattr(decorator.attr, "", "") in ["command", "group"]:
                    return True
            elif isinstance(decorator, ast.Call):
                if hasattr(decorator.func, "attr") and decorator.func.attr in [
                    "command",
                    "group",
                ]:
                    return True
        return False

    def _validate_cli_command_implementation(
        self, cli_file: Path, node: ast.FunctionDef
    ) -> None:
        """验证CLI命令的实现是否完整"""
        func_name = node.name

        # 检查是否有实际实现（不只是pass或TODO）
        has_implementation = False
        has_todo = False

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Pass):
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if "TODO" in str(stmt.value.value):
                    has_todo = True
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # 跳过嵌套函数
            else:
                has_implementation = True

        if not has_implementation or has_todo:
            self._add_violation(
                category="CLI完整性",
                severity="critical",
                message=f"CLI命令 '{func_name}' 缺少实际实现",
                file_path=str(cli_file),
                line_number=node.lineno,
                suggestion=f"为命令 '{func_name}' 添加完整的功能实现",
                impact=f"用户无法使用 '{func_name}' 命令",
            )

    # P0检查：配置系统一致性

    def _check_configuration_consistency(self) -> None:
        """检查配置系统的一致性"""
        print("⚙️ 检查配置系统一致性...")

        # 查找配置相关文件
        config_files = list(self.project_path.glob("**/*.yaml")) + list(
            self.project_path.glob("**/*.yml")
        )
        python_files = [
            f for f in self.project_path.rglob("*.py") if "config" in f.name.lower()
        ]

        if not config_files and python_files:
            self._add_violation(
                category="配置一致性",
                severity="warning",
                message="存在配置代码但缺少配置文件",
                suggestion="创建对应的配置文件或移除配置代码",
                impact="配置功能可能无法正常工作",
            )

        # 检查配置类与配置文件的一致性
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
            self._check_config_class_consistency(py_file)

    def _check_config_class_consistency(self, config_file: Path) -> None:
        """检查配置类的方法签名与实际使用的一致性"""
        try:
            content = config_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # 查找配置类
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and "config" in node.name.lower():
                    self._analyze_config_class_methods(config_file, node)

        except (UnicodeDecodeError, SyntaxError):
            pass

    def _analyze_config_class_methods(
        self, file_path: Path, class_node: ast.ClassDef
    ) -> None:
        """分析配置类方法的返回类型一致性"""
        class_name = class_node.name

        for method in class_node.body:
            if isinstance(method, ast.FunctionDef):
                # 检查方法是否有明确的返回类型注解
                if method.returns is None and method.name not in [
                    "__init__",
                    "__str__",
                    "__repr__",
                ]:
                    self._add_violation(
                        category="配置一致性",
                        severity="warning",
                        message=f"配置类 {class_name}.{method.name}() 缺少返回类型注解",
                        file_path=str(file_path),
                        line_number=method.lineno,
                        suggestion="添加明确的返回类型注解",
                        impact="可能导致使用方期望与实际返回值不符",
                    )

    # P0检查：模板系统完整性

    def _check_template_system(self) -> None:
        """检查项目模板系统的完整性"""
        print("📋 检查模板系统完整性...")

        # 检查templates目录
        templates_dir = self.project_path / "aiculture" / "templates"
        if not templates_dir.exists():
            self._add_violation(
                category="模板系统",
                severity="critical",
                message="templates目录不存在",
                suggestion="创建aiculture/templates目录并添加项目模板",
                impact="create命令无法工作，用户无法创建新项目",
            )
            return

        # 检查模板内容
        template_types = list(templates_dir.iterdir()) if templates_dir.exists() else []

        if not template_types:
            self._add_violation(
                category="模板系统",
                severity="critical",
                message="templates目录为空",
                suggestion="添加Python、JavaScript等项目模板",
                impact="用户无法创建任何类型的项目",
            )
        else:
            # 检查每个模板的完整性
            for template_dir in template_types:
                if template_dir.is_dir():
                    self._validate_template_completeness(template_dir)

    def _validate_template_completeness(self, template_dir: Path) -> None:
        """验证单个模板的完整性"""
        template_name = template_dir.name

        # 检查基本文件
        required_files = {
            "python": ["pyproject.toml", "requirements.txt", "README.md"],
            "javascript": ["package.json", "README.md"],
            "default": ["README.md"],
        }

        expected_files = required_files.get(template_name, required_files["default"])

        for required_file in expected_files:
            file_path = template_dir / required_file
            if not file_path.exists():
                self._add_violation(
                    category="模板系统",
                    severity="warning",
                    message=f"模板 '{template_name}' 缺少必要文件: {required_file}",
                    suggestion=f"在模板中添加 {required_file} 文件",
                    impact=f"使用此模板创建的项目将缺少 {required_file}",
                )

    # P1检查：测试覆盖率

    def _check_test_coverage(self) -> None:
        """检查测试覆盖率情况"""
        print("🧪 检查测试覆盖率...")

        # 查找测试文件
        test_files = (
            list(self.project_path.rglob("test_*.py"))
            + list(self.project_path.rglob("*_test.py"))
            + list(self.project_path.glob("tests/**/*.py"))
        )

        # 查找源代码文件
        source_files = [
            f
            for f in self.project_path.rglob("*.py")
            if "aiculture" in str(f) and not self._should_skip_file(f)
        ]

        if not test_files and source_files:
            self._add_violation(
                category="测试覆盖率",
                severity="critical",
                message="项目缺少测试文件",
                suggestion="创建tests目录并添加单元测试",
                impact="无法验证代码功能正确性，可能存在未发现的错误",
            )
            return

        # 简单的覆盖率估算
        if test_files and source_files:
            test_count = len(test_files)
            source_count = len(source_files)
            estimated_coverage = min(100, (test_count / source_count) * 100)

            if estimated_coverage < 30:
                self._add_violation(
                    category="测试覆盖率",
                    severity="warning",
                    message=f"测试覆盖率可能较低 (估算: {estimated_coverage:.1f}%)",
                    suggestion="增加更多测试文件，目标覆盖率80%+",
                    impact="可能存在未测试的代码路径",
                )

    # P1检查：端到端工作流

    def _check_end_to_end_workflows(self) -> None:
        """检查关键工作流的端到端完整性"""
        print("🔗 检查端到端工作流...")

        # 检查CLI是否可以导入
        try:
            cli_path = self.project_path / "aiculture" / "cli.py"
            if cli_path.exists():
                # 尝试静态分析CLI是否有语法错误
                content = cli_path.read_text()
                ast.parse(content)  # 如果有语法错误会抛异常
        except SyntaxError as e:
            self._add_violation(
                category="端到端工作流",
                severity="critical",
                message=f"CLI文件有语法错误，无法执行: {e}",
                file_path=str(cli_path),
                impact="所有CLI命令都无法使用",
            )
        except Exception:
            pass  # 其他错误先忽略

    # P1检查：依赖可用性

    def _check_dependency_availability(self) -> None:
        """检查项目依赖的可用性"""
        print("📦 检查依赖可用性...")

        requirements_files = [
            self.project_path / "requirements.txt",
            self.project_path / "requirements-dev.txt",
        ]

        for req_file in requirements_files:
            if req_file.exists():
                self._validate_requirements_file(req_file)

    def _validate_requirements_file(self, req_file: Path) -> None:
        """验证requirements文件的格式和依赖可用性"""
        try:
            content = req_file.read_text()
            lines = [
                line.strip()
                for line in content.split("\n")
                if line.strip() and not line.startswith("#")
            ]

            for line in lines:
                if "==" not in line and ">=" not in line and line.count(".") > 0:
                    # 检查是否为有效的包名格式
                    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", line.split()[0]):
                        self._add_violation(
                            category="依赖可用性",
                            severity="warning",
                            message=f"依赖格式可能有误: {line}",
                            file_path=str(req_file),
                            suggestion="检查依赖名称和版本格式",
                            impact="pip install可能失败",
                        )

        except Exception:
            self._add_violation(
                category="依赖可用性",
                severity="warning",
                message=f"requirements文件格式可能有问题: {req_file.name}",
                file_path=str(req_file),
                impact="依赖安装可能失败",
            )

    # 辅助方法

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过检查的文件"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            ".pytest_cache",
            "node_modules",
            ".aiculture/cache",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def generate_report(self) -> Dict[str, Any]:
        """生成功能完整性检查报告"""
        total_violations = len(self.violations)
        critical_count = len([v for v in self.violations if v.severity == "critical"])
        warning_count = len([v for v in self.violations if v.severity == "warning"])
        info_count = len([v for v in self.violations if v.severity == "info"])

        # 按分类统计
        categories = {}
        for violation in self.violations:
            if violation.category not in categories:
                categories[violation.category] = []
            categories[violation.category].append(
                {
                    "severity": violation.severity,
                    "message": violation.message,
                    "file_path": violation.file_path,
                    "line_number": violation.line_number,
                    "suggestion": violation.suggestion,
                    "impact": violation.impact,
                }
            )

        # 计算功能完整性分数
        functionality_score = max(
            0, 100 - (critical_count * 25 + warning_count * 10 + info_count * 2)
        )

        return {
            "summary": {
                "total_violations": total_violations,
                "critical": critical_count,
                "warning": warning_count,
                "info": info_count,
                "functionality_score": functionality_score,
            },
            "categories": categories,
            "critical_issues": [
                {
                    "category": v.category,
                    "message": v.message,
                    "impact": v.impact,
                    "suggestion": v.suggestion,
                }
                for v in self.violations
                if v.severity == "critical"
            ],
        }
