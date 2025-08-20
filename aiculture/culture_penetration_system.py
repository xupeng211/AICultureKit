"""
文化深度渗透系统 - 确保开发文化在项目中彻底渗透

提供：
1. 实时文化监控
2. 强制性质量门禁
3. AI开发文化助手
4. 开发过程文化仪表板
5. 文化游戏化激励系统
"""

import ast
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class CultureViolationSeverity(Enum):
    """文化违规严重程度"""

    BLOCKING = "blocking"  # 阻塞性违规，必须修复
    CRITICAL = "critical"  # 严重违规，强烈建议修复
    WARNING = "warning"  # 警告违规，建议修复
    INFO = "info"  # 信息违规，可选修复


class CultureGateStatus(Enum):
    """文化门禁状态"""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class CultureViolation:
    """文化违规记录"""

    principle: str
    severity: CultureViolationSeverity
    message: str
    file_path: str
    line_number: int
    suggestion: str
    auto_fixable: bool = False
    fix_command: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class CultureGate:
    """文化质量门禁"""

    name: str
    description: str
    blocking_rules: List[str]
    critical_threshold: int  # 严重违规的最大允许数量
    warning_threshold: int  # 警告违规的最大允许数量
    enabled: bool = True


class RealTimeCultureMonitor:
    """实时文化监控器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.monitoring = False
        self.monitor_thread = None
        self.violations: List[CultureViolation] = []
        self.callbacks: List[Callable] = []

        # 监控的文件扩展名
        self.monitored_extensions = {
            '.py',
            '.js',
            '.ts',
            '.jsx',
            '.tsx',
            '.html',
            '.css',
        }

        # 文件修改时间缓存
        self.file_mtimes = {}

    def add_violation_callback(self, callback: Callable[[CultureViolation], None]) -> None:
        """添加违规回调函数"""
        self.callbacks.append(callback)

    def start_monitoring(self, interval: int = 5) -> None:
        """开始实时监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True
        )
        self.monitor_thread.start()
        print(f"🔍 开始实时文化监控，检查间隔: {interval}秒")

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ 实时文化监控已停止")

    def _monitor_loop(self, interval: int) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                changed_files = self._detect_file_changes()
                if changed_files:
                    print(f"📝 检测到 {len(changed_files)} 个文件变更")
                    violations = self._check_changed_files(changed_files)

                    for violation in violations:
                        self._notify_violation(violation)

                time.sleep(interval)

            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(interval)

    def _detect_file_changes(self) -> List[Path]:
        """检测文件变更"""
        changed_files = []

        for file_path in self.project_path.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix not in self.monitored_extensions:
                continue

            # 跳过隐藏目录和虚拟环境
            if any(
                part.startswith('.') or part in ['venv', '__pycache__', 'node_modules']
                for part in file_path.parts
            ):
                continue

            try:
                current_mtime = file_path.stat().st_mtime
                cached_mtime = self.file_mtimes.get(str(file_path))

                if cached_mtime is None or current_mtime > cached_mtime:
                    self.file_mtimes[str(file_path)] = current_mtime
                    if cached_mtime is not None:  # 不是第一次检查
                        changed_files.append(file_path)

            except OSError:
                continue

        return changed_files

    def _check_changed_files(self, files: List[Path]) -> List[CultureViolation]:
        """检查变更文件的文化违规"""
        violations = []

        for file_path in files:
            file_violations = self._check_single_file(file_path)
            violations.extend(file_violations)

        return violations

    def _check_single_file(self, file_path: Path) -> List[CultureViolation]:
        """检查单个文件"""
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # 检查各种文化违规
            violations.extend(self._check_test_culture(file_path, content, lines))
            violations.extend(self._check_documentation_culture(file_path, content, lines))
            violations.extend(self._check_security_culture(file_path, content, lines))
            violations.extend(self._check_code_quality_culture(file_path, content, lines))

        except Exception as e:
            print(f"检查文件 {file_path} 时出错: {e}")

        return violations

    def _check_test_culture(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[CultureViolation]:
        """检查测试文化"""
        violations = []

        # 如果是新的Python模块，检查是否有对应的测试文件
        if file_path.suffix == '.py' and not str(file_path).startswith('test_'):
            test_file = file_path.parent / f"test_{file_path.name}"
            tests_dir_file = file_path.parent / "tests" / f"test_{file_path.name}"

            if not test_file.exists() and not tests_dir_file.exists():
                violations.append(
                    CultureViolation(
                        principle="testing",
                        severity=CultureViolationSeverity.CRITICAL,
                        message=f"新模块 {file_path.name} 缺少对应的测试文件",
                        file_path=str(file_path),
                        line_number=1,
                        suggestion=f"创建 {test_file} 或 {tests_dir_file}",
                        auto_fixable=True,
                        fix_command=f"touch {test_file}",
                    )
                )

        return violations

    def _check_documentation_culture(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[CultureViolation]:
        """检查文档文化"""
        violations = []

        if file_path.suffix == '.py':
            # 检查类和函数是否有文档字符串
            import ast

            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            violations.append(
                                CultureViolation(
                                    principle="documentation",
                                    severity=CultureViolationSeverity.WARNING,
                                    message=f"{type(node).__name__} '{node.name}' 缺少文档字符串",
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    suggestion="添加描述性的文档字符串",
                                    auto_fixable=True,
                                    fix_command="# 可以使用自动文档生成工具",
                                )
                            )
            except SyntaxError:
                pass

        return violations

    def _check_security_culture(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[CultureViolation]:
        """检查安全文化"""
        violations = []

        # 检查硬编码密码
        import re

        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern in password_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        CultureViolation(
                            principle="security",
                            severity=CultureViolationSeverity.BLOCKING,
                            message="发现硬编码的敏感信息",
                            file_path=str(file_path),
                            line_number=line_num,
                            suggestion="使用环境变量或配置文件存储敏感信息",
                            auto_fixable=False,
                        )
                    )

        return violations

    def _check_code_quality_culture(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[CultureViolation]:
        """检查代码质量文化"""
        violations = []

        # 检查函数长度
        if file_path.suffix == '.py':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            func_lines = node.end_lineno - node.lineno + 1
                            if func_lines > 50:
                                violations.append(
                                    CultureViolation(
                                        principle="code_quality",
                                        severity=CultureViolationSeverity.WARNING,
                                        message=f"函数 '{node.name}' 过长 ({func_lines} 行)",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        suggestion="考虑将大函数拆分为多个小函数",
                                        auto_fixable=False,
                                    )
                                )
            except SyntaxError:
                pass

        return violations

    def _notify_violation(self, violation: CultureViolation) -> None:
        """通知违规"""
        self.violations.append(violation)

        # 调用回调函数
        for callback in self.callbacks:
            try:
                callback(violation)
            except Exception as e:
                print(f"违规回调错误: {e}")


class CultureQualityGate:
    """文化质量门禁"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.gates = self._initialize_gates()

    def _initialize_gates(self) -> Dict[str, CultureGate]:
        """初始化质量门禁"""
        return {
            "commit_gate": CultureGate(
                name="提交门禁",
                description="代码提交前的文化检查",
                blocking_rules=["security", "syntax_error"],
                critical_threshold=0,  # 不允许严重违规
                warning_threshold=5,  # 最多5个警告
            ),
            "merge_gate": CultureGate(
                name="合并门禁",
                description="代码合并前的文化检查",
                blocking_rules=["security", "testing", "documentation"],
                critical_threshold=0,
                warning_threshold=3,
            ),
            "release_gate": CultureGate(
                name="发布门禁",
                description="版本发布前的文化检查",
                blocking_rules=["security", "testing", "documentation", "performance"],
                critical_threshold=0,
                warning_threshold=0,  # 发布时不允许任何违规
            ),
        }

    def check_gate(self, gate_name: str, violations: List[CultureViolation]) -> Dict[str, Any]:
        """检查质量门禁"""
        if gate_name not in self.gates:
            return {
                "status": CultureGateStatus.FAILED,
                "message": f"未知门禁: {gate_name}",
            }

        gate = self.gates[gate_name]
        if not gate.enabled:
            return {"status": CultureGateStatus.PASSED, "message": "门禁已禁用"}

        # 统计违规
        blocking_violations = []
        critical_violations = []
        warning_violations = []

        for violation in violations:
            if violation.principle in gate.blocking_rules:
                if violation.severity == CultureViolationSeverity.BLOCKING:
                    blocking_violations.append(violation)
                elif violation.severity == CultureViolationSeverity.CRITICAL:
                    critical_violations.append(violation)
                elif violation.severity == CultureViolationSeverity.WARNING:
                    warning_violations.append(violation)

        # 检查门禁条件
        if blocking_violations:
            return {
                "status": CultureGateStatus.FAILED,
                "message": f"发现 {len(blocking_violations)} 个阻塞性违规",
                "blocking_violations": blocking_violations,
                "suggestion": "必须修复所有阻塞性违规才能通过门禁",
            }

        if len(critical_violations) > gate.critical_threshold:
            return {
                "status": CultureGateStatus.FAILED,
                "message": f"严重违规数量 ({len(critical_violations)}) 超过阈值 ({gate.critical_threshold})",
                "critical_violations": critical_violations,
                "suggestion": "减少严重违规数量",
            }

        if len(warning_violations) > gate.warning_threshold:
            return {
                "status": CultureGateStatus.FAILED,
                "message": f"警告违规数量 ({len(warning_violations)}) 超过阈值 ({gate.warning_threshold})",
                "warning_violations": warning_violations,
                "suggestion": "减少警告违规数量",
            }

        return {
            "status": CultureGateStatus.PASSED,
            "message": "所有文化检查通过",
            "summary": {
                "critical_violations": len(critical_violations),
                "warning_violations": len(warning_violations),
                "total_violations": len(violations),
            },
        }


class AIDevCultureAssistant:
    """AI开发文化助手"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.culture_monitor = RealTimeCultureMonitor(project_path)
        self.quality_gate = CultureQualityGate(project_path)

        # 注册违规回调
        self.culture_monitor.add_violation_callback(self._on_violation_detected)

    def _on_violation_detected(self, violation: CultureViolation) -> None:
        """违规检测回调"""
        severity_emoji = {
            CultureViolationSeverity.BLOCKING: "🚫",
            CultureViolationSeverity.CRITICAL: "🔴",
            CultureViolationSeverity.WARNING: "🟡",
            CultureViolationSeverity.INFO: "🔵",
        }

        emoji = severity_emoji.get(violation.severity, "❓")

        print(
            """
{emoji} 文化违规检测
原则: {violation.principle}
严重程度: {violation.severity.value.upper()}
文件: {violation.file_path}:{violation.line_number}
问题: {violation.message}
建议: {violation.suggestion}
"""
        )

        # 如果可以自动修复，提供修复建议
        if violation.auto_fixable and violation.fix_command:
            print(f"💡 自动修复命令: {violation.fix_command}")

    def start_assistance(self) -> None:
        """启动AI开发文化助手"""
        print("🤖 AI开发文化助手已启动")
        self.culture_monitor.start_monitoring(interval=3)  # 更频繁的检查

    def stop_assistance(self) -> None:
        """停止AI开发文化助手"""
        self.culture_monitor.stop_monitoring()
        print("🤖 AI开发文化助手已停止")

    def check_before_commit(self) -> bool:
        """提交前检查"""
        print("🔍 执行提交前文化检查...")

        # 这里应该集成完整的文化检查
        from .culture_enforcer import CultureEnforcer

        enforcer = CultureEnforcer(str(self.project_path))
        result = enforcer.enforce_all()

        # 转换为违规对象
        violations = []
        for violation in enforcer.violations:
            culture_violation = CultureViolation(
                principle=violation.principle,
                severity=(
                    CultureViolationSeverity.WARNING
                    if violation.severity == "warning"
                    else CultureViolationSeverity.CRITICAL
                ),
                message=violation.description,
                file_path=violation.file_path,
                line_number=violation.line_number,
                suggestion=violation.suggestion,
            )
            violations.append(culture_violation)

        # 检查提交门禁
        gate_result = self.quality_gate.check_gate("commit_gate", violations)

        if gate_result["status"] == CultureGateStatus.PASSED:
            print("✅ 提交门禁检查通过")
            return True
        else:
            print(f"❌ 提交门禁检查失败: {gate_result['message']}")
            print(f"💡 建议: {gate_result.get('suggestion', '修复违规后重试')}")
            return False

    def generate_culture_report(self) -> Dict[str, Any]:
        """生成文化报告"""
        violations = self.culture_monitor.violations

        # 按原则分组
        by_principle = {}
        for violation in violations:
            if violation.principle not in by_principle:
                by_principle[violation.principle] = []
            by_principle[violation.principle].append(violation)

        # 按严重程度分组
        by_severity = {}
        for violation in violations:
            severity = violation.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(violation)

        return {
            "total_violations": len(violations),
            "by_principle": by_principle,
            "by_severity": by_severity,
            "auto_fixable_count": len([v for v in violations if v.auto_fixable]),
            "recommendations": self._generate_recommendations(violations),
        }

    def _generate_recommendations(self, violations: List[CultureViolation]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 按原则统计违规数量
        principle_counts = {}
        for violation in violations:
            principle_counts[violation.principle] = principle_counts.get(violation.principle, 0) + 1

        # 生成针对性建议
        for principle, count in sorted(principle_counts.items(), key=lambda x: x[1], reverse=True):
            if principle == "testing":
                recommendations.append(f"为新模块编写单元测试 ({count} 个缺失)")
            elif principle == "documentation":
                recommendations.append(f"完善文档字符串 ({count} 个缺失)")
            elif principle == "security":
                recommendations.append(f"修复安全问题 ({count} 个发现)")
            elif principle == "code_quality":
                recommendations.append(f"改善代码质量 ({count} 个问题)")

        return recommendations[:5]  # 只返回前5个建议


# 使用示例
if __name__ == "__main__":
    # 初始化AI开发文化助手
    assistant = AIDevCultureAssistant(Path("."))

    try:
        # 启动实时监控
        assistant.start_assistance()

        print("🔍 监控中... (按Ctrl+C停止)")

        # 模拟开发过程
        time.sleep(10)

        # 检查提交门禁
        can_commit = assistant.check_before_commit()
        print(f"可以提交: {can_commit}")

        # 生成文化报告
        report = assistant.generate_culture_report()
        print(f"文化报告: {json.dumps(report, indent=2, ensure_ascii=False)}")

    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        assistant.stop_assistance()
