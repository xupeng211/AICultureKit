from typing import Any

"""
文化原则强制执行器

自动检查和强制执行开发文化原则，确保所有代码都符合标准。
"""

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .accessibility_culture import AccessibilityCultureManager
from .ai_culture_principles import AICulturePrinciples, PrincipleCategory
from .data_governance_culture import DataGovernanceManager
from .observability_culture import ObservabilityManager
from .performance_culture import MemoryLeakDetector, PerformanceBenchmarkManager
from .i18n import _
import json


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

    def __init__(self, project_path: str = ".") -> None:
        """内部方法： init"""
        self.project_path = Path(project_path)
        self.principles = AICulturePrinciples()
        self.violations: List[Violation] = []

        # 初始化新的文化模块
        self.performance_manager = PerformanceBenchmarkManager(self.project_path)
        self.memory_detector = MemoryLeakDetector()
        self.observability_manager = ObservabilityManager("aiculture", "1.0.0")
        self.data_governance = DataGovernanceManager(self.project_path)
        self.accessibility_manager = AccessibilityCultureManager(self.project_path)

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

        # 检查性能文化
        self._check_performance_culture()

        # 检查可观测性
        self._check_observability()

        # 检查数据治理
        self._check_data_governance()

        # 检查可访问性
        self._check_accessibility()

        return self._generate_report()

    def _check_project_structure(self) -> Any:
        """检查项目结构是否符合标准"""
        required_files = [
            "README.md",
            ".gitignore",
            "requirements.txt",  # 或 pyproject.toml
            ".pre-commit-config.yaml",
        ]

        for file_name in required_files:
            if not (self.project_path / file_name).exists():
                self.violations.append(
                    Violation(
                        principle="project_structure",
                        severity="error",
                        file_path=file_name,
                        line_number=0,
                        description=f"缺少必要文件: {file_name}",
                        suggestion=f"创建 {file_name} 文件",
                    )
                )

        # 检查测试目录
        if not (self.project_path / "tests").exists():
            self.violations.append(
                Violation(
                    principle="testing",
                    severity="warning",
                    file_path="tests/",
                    line_number=0,
                    description="缺少测试目录",
                    suggestion="创建 tests/ 目录并添加测试用例",
                )
            )

    def _check_code_quality(self) -> Any:
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

    def _check_solid_principles(self, file_path: Path, content: str) -> Any:
        """检查SOLID原则"""
        try:
            tree = ast.parse(content)

            # 检查单一职责原则
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 10:  # 简单的启发式规则
                        self.violations.append(
                            Violation(
                                principle="solid_srp",
                                severity="warning",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"类 {node.name} 可能违反单一职责原则 (方法数: {len(methods)})",
                                suggestion="考虑将类拆分为更小的、职责单一的类",
                            )
                        )

        except SyntaxError:
            pass  # 跳过语法错误的文件

    def _check_dry_principle(self, file_path: Path, content: str) -> Any:
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
                self.violations.append(
                    Violation(
                        principle="dry",
                        severity="warning",
                        file_path=str(file_path),
                        line_number=occurrences[0],
                        description=f"检测到重复代码: '{line[:50]}...'",
                        suggestion="考虑将重复代码提取为函数或常量",
                    )
                )

    def _check_kiss_principle(self, file_path: Path, content: str) -> Any:
        """检查KISS原则"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数复杂度
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:  # 圈复杂度阈值
                        self.violations.append(
                            Violation(
                                principle="kiss",
                                severity="warning",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"函数 {node.name} 复杂度过高 (复杂度: {complexity})",
                                suggestion="考虑将函数拆分为更小的函数",
                            )
                        )

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

    def _check_security(self) -> Any:
        """检查安全问题"""
        try:
            # 使用bandit进行安全检查
            result = subprocess.run(
                ["bandit", "-r", str(self.project_path), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=30,  # 添加超时防止卡死
            )

            if result.returncode == 0:
                import json

                bandit_results = json.loads(result.stdout)

                for issue in bandit_results.get('results', []):
                    self.violations.append(
                        Violation(
                            principle="security",
                            severity=issue['issue_severity'].lower(),
                            file_path=issue['filename'],
                            line_number=issue['line_number'],
                            description=issue['issue_text'],
                            suggestion=f"查看bandit文档: {issue['test_id']}",
                        )
                    )

        except FileNotFoundError:
            # bandit未安装
            pass
        except subprocess.TimeoutExpired:
            # bandit执行超时
            pass
        except Exception:
            # 其他错误
            pass

    def _check_test_coverage(self) -> Any:
        """检查测试覆盖率"""
        try:
            # 运行pytest获取覆盖率
            result = subprocess.run(
                ["pytest", "--cov=.", "--cov-report=json", "--quiet"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            coverage_file = self.project_path / "coverage.json"
            if coverage_file.exists():

                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data['totals']['percent_covered']
                if total_coverage < 80:
                    self.violations.append(
                        Violation(
                            principle="testing",
                            severity="warning",
                            file_path="overall",
                            line_number=0,
                            description=f"测试覆盖率不足: {total_coverage:.1f}%",
                            suggestion="添加更多测试用例以达到80%覆盖率",
                        )
                    )

        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    def _check_documentation(self) -> Any:
        """检查文档完整性"""
        readme_path = self.project_path / "README.md"

        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            required_sections = [
                "installation",
                "install",
                "安装",
                "usage",
                "使用",
                "example",
                "示例",
            ]

            content_lower = content.lower()
            missing_sections = []

            for section in required_sections:
                if section not in content_lower:
                    missing_sections.append(section)

            if len(missing_sections) == len(required_sections):
                self.violations.append(
                    Violation(
                        principle="documentation",
                        severity="warning",
                        file_path="README.md",
                        line_number=0,
                        description="README.md缺少安装和使用说明",
                        suggestion="添加安装指南和使用示例",
                    )
                )

    def _generate_report(self) -> Dict[str, Any]:
        """生成检查报告"""
        errors = [v for v in self.violations if v.severity == "error"]
        warnings = [v for v in self.violations if v.severity == "warning"]

        # 按原则分组
        by_principle = {}
        for violation in self.violations:
            if violation.principle not in by_principle:
                by_principle[violation.principle] = []
            by_principle[violation.principle].append(violation)

        # 计算质量分数
        score = max(0, 100 - len(errors) * 15 - len(warnings) * 5)

        return {
            "score": score,
            "total_violations": len(self.violations),
            "errors": len(errors),
            "warnings": len(warnings),
            "by_principle": by_principle,
            "violations": [
                {
                    "principle": v.principle,
                    "severity": v.severity,
                    "file": v.file_path,
                    "line": v.line_number,
                    "description": v.description,
                    "suggestion": v.suggestion,
                }
                for v in self.violations
            ],
        }

    def generate_fix_suggestions(self) -> List[str]:
        """生成修复建议"""
        suggestions = []

        # 按严重程度排序
        sorted_violations = sorted(
            self.violations, key=lambda x: 0 if x.severity == "error" else 1
        )

        for violation in sorted_violations:
            suggestions.append(
                f"📁 {violation.file_path}:{violation.line_number}\n"
                f"🔴 {violation.principle.upper()}: {violation.description}\n"
                f"💡 建议: {violation.suggestion}\n"
            )

        return suggestions

    def _add_violation(
        self,
        principle: str,
        severity: str,
        message: str,
        file_path: str = "",
        line_number: int = 0,
        suggestion: str = "",
    ) -> None:
        """添加违规记录"""
        violation = Violation(
            principle=principle,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            description=message,
            suggestion=suggestion,
        )
        self.violations.append(violation)

    def _scan_python_files(self) -> Any:
        """扫描Python文件"""
        for py_file in self.project_path.rglob("*.py"):
            # 跳过虚拟环境和隐藏目录
            if any(
                part.startswith(".") or part in ["venv", "__pycache__", "build", "dist"]
                for part in py_file.parts
            ):
                continue
            yield py_file

    def _check_file_structure(self) -> None:
        """检查文件结构"""
        required_files = [
            "README.md",
            "requirements.txt",
            ".gitignore",
            "setup.py",
        ]

        for required_file in required_files:
            file_path = self.project_path / required_file
            if not file_path.exists():
                self._add_violation(
                    principle="project_structure",
                    severity="warning",
                    message=f"文件结构: 缺少 {required_file}",
                    suggestion=f"创建 {required_file} 文件",
                )

    def _generate_report(self) -> Dict[str, Any]:
        """生成报告"""
        error_count = sum(1 for v in self.violations if v.severity == "error")
        warning_count = sum(1 for v in self.violations if v.severity == "warning")
        score = self._calculate_score(error_count, warning_count)

        # 按原则分组违规
        by_principle = {}
        for violation in self.violations:
            if violation.principle not in by_principle:
                by_principle[violation.principle] = []
            by_principle[violation.principle].append(violation)

        return {
            "score": score,
            "errors": error_count,
            "warnings": warning_count,
            "total_violations": len(self.violations),
            "violations": self.violations,
            "by_principle": by_principle,
        }

    def _calculate_score(self, errors: int, warnings: int) -> int:
        """计算质量分数"""
        base_score = 100
        # 错误扣20分，警告扣5分
        score = base_score - (errors * 20) - (warnings * 5)
        return max(0, score)

    def _check_code_quality(self) -> None:
        """检查代码质量"""

        # 运行flake8检查
        try:
            result = subprocess.run(
                ["flake8", str(self.project_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                self._add_violation(
                    principle="code_quality",
                    severity="warning",
                    message="代码质量检查发现问题",
                    suggestion="运行 flake8 查看详细信息",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # flake8未安装或超时，跳过检查
            pass

    def _check_performance_culture(self) -> None:
        """检查性能文化"""
        try:
            # 检查是否有性能基准
            benchmarks_file = (
                self.project_path / ".aiculture" / "performance_benchmarks.json"
            )
            if not benchmarks_file.exists():
                self._add_violation(
                    principle="performance_culture",
                    severity="warning",
                    message="缺少性能基准测试",
                    suggestion="使用PerformanceBenchmarkManager创建性能基准",
                )

            # 启动内存监控检查
            leak_result = self.memory_detector.detect_leaks()
            if leak_result.get('status') == 'leak_detected':
                for warning in leak_result.get('warnings', []):
                    self._add_violation(
                        principle="performance_culture",
                        severity="error",
                        message=f"内存泄漏检测: {warning}",
                        suggestion="检查内存使用模式并修复泄漏",
                    )
        except Exception as e:
            print(f"性能文化检查错误: {e}")

    def _check_observability(self) -> None:
        """检查可观测性"""
        try:
            # 检查日志配置
            log_files = list(self.project_path.rglob("*.log"))
            if (
                not log_files
                and not (self.project_path / ".aiculture" / "observability").exists()
            ):
                self._add_violation(
                    principle="observability",
                    severity="warning",
                    message="缺少结构化日志配置",
                    suggestion="使用ObservabilityManager配置日志、指标和追踪",
                )

            # 检查是否有监控配置
            monitoring_configs = ["prometheus.yml", "grafana.json", "jaeger.yml"]

            has_monitoring = any(
                (self.project_path / config).exists() for config in monitoring_configs
            )

            if not has_monitoring:
                self._add_violation(
                    principle="observability",
                    severity="info",
                    message="建议添加监控配置",
                    suggestion="配置Prometheus、Grafana或其他监控工具",
                )
        except Exception as e:
            print(f"可观测性检查错误: {e}")

    def _check_data_governance(self) -> None:
        """检查数据治理"""
        try:
            # 扫描隐私问题
            privacy_scan = self.data_governance.scan_project_for_privacy_issues()

            if privacy_scan['total_findings'] > 0:
                high_risk = len(privacy_scan['by_severity']['high'])
                if high_risk > 0:
                    self._add_violation(
                        principle="data_governance",
                        severity="error",
                        message=f"发现 {high_risk} 个高风险隐私问题",
                        suggestion="移除代码中的硬编码个人信息",
                    )

                medium_risk = len(privacy_scan['by_severity']['medium'])
                if medium_risk > 0:
                    self._add_violation(
                        principle="data_governance",
                        severity="warning",
                        message=f"发现 {medium_risk} 个中等风险隐私问题",
                        suggestion="为敏感字段添加适当的保护措施",
                    )

            # 检查数据清单
            if not self.data_governance.data_inventory:
                self._add_violation(
                    principle="data_governance",
                    severity="info",
                    message="缺少数据清单",
                    suggestion="建立数据分类和清单管理",
                )
        except Exception as e:
            print(f"数据治理检查错误: {e}")

    def _check_accessibility(self) -> None:
        """检查可访问性"""
        try:
            # 扫描可访问性问题
            accessibility_report = (
                self.accessibility_manager.generate_comprehensive_report()
            )

            total_issues = accessibility_report['total_issues']
            if total_issues > 0:
                accessibility_issues = accessibility_report['accessibility'][
                    'by_severity'
                ]

                if accessibility_issues['error']:
                    self._add_violation(
                        principle="accessibility",
                        severity="error",
                        message=f"发现 {len(accessibility_issues['error'])} 个可访问性错误",
                        suggestion="修复WCAG合规性问题",
                    )

                if accessibility_issues['warning']:
                    self._add_violation(
                        principle="accessibility",
                        severity="warning",
                        message=f"发现 {len(accessibility_issues['warning'])} 个可访问性警告",
                        suggestion="改善用户界面的可访问性",
                    )

                # 检查国际化
                i18n_issues = accessibility_report['internationalization'][
                    'total_issues'
                ]
                if i18n_issues > 0:
                    self._add_violation(
                        principle="accessibility",
                        severity="warning",
                        message=f"发现 {i18n_issues} 个国际化问题",
                        suggestion="使用国际化函数替换硬编码文本",
                    )
        except Exception as e:
            print(f"可访问性检查错误: {e}")


def enforce_culture_in_project(project_path: str = ".") -> Dict[str, Any]:
    """在项目中强制执行文化原则"""
    enforcer = CultureEnforcer(project_path)
    return enforcer.enforce_all()
