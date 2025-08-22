#!/usr/bin/env python3
"""
AI行为强制执行器

确保所有AI编程工具严格遵循开发文化标准，
当遇到质量门禁时必须解决问题而不是绕过。
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from .culture_enforcer import CultureEnforcer
from .error_handling import get_logger


class AIBehaviorViolation(Enum):
    """AI行为违规类型"""

    BYPASS_QUALITY_GATE = "bypass_quality_gate"
    IGNORE_CULTURE_CHECK = "ignore_culture_check"
    FORCE_PUSH_WITH_ERRORS = "force_push_with_errors"
    DISABLE_HOOKS = "disable_hooks"
    SKIP_TESTS = "skip_tests"


@dataclass
class AIBehaviorRule:
    """AI行为规则"""

    rule_id: str
    description: str
    violation_type: AIBehaviorViolation
    severity: str  # "critical", "high", "medium", "low"
    enforcement_action: str
    message: str


class AIBehaviorEnforcer:
    """AI行为强制执行器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.logger = get_logger("ai_behavior_enforcer")
        self.violation_log = self.project_path / ".aiculture" / "ai_violations.json"
        self.violation_log.parent.mkdir(exist_ok=True)

        # 定义AI行为规则
        self.rules = [
            AIBehaviorRule(
                rule_id="NO_BYPASS_QUALITY_GATE",
                description="禁止绕过质量门禁",
                violation_type=AIBehaviorViolation.BYPASS_QUALITY_GATE,
                severity="critical",
                enforcement_action="block_operation",
                message="🚨 严重违规：AI工具试图绕过质量门禁！必须解决问题而不是绕过标准。",
            ),
            AIBehaviorRule(
                rule_id="NO_DISABLE_HOOKS",
                description="禁止禁用Git钩子",
                violation_type=AIBehaviorViolation.DISABLE_HOOKS,
                severity="critical",
                enforcement_action="block_operation",
                message="🚨 严重违规：AI工具试图禁用Git钩子！这违背了文化标准的核心原则。",
            ),
            AIBehaviorRule(
                rule_id="NO_FORCE_PUSH_WITH_ERRORS",
                description="禁止在有错误时强制推送",
                violation_type=AIBehaviorViolation.FORCE_PUSH_WITH_ERRORS,
                severity="high",
                enforcement_action="block_operation",
                message="⚠️ 高风险违规：AI工具试图在有错误时强制推送！必须先修复所有错误。",
            ),
            AIBehaviorRule(
                rule_id="NO_IGNORE_CULTURE_CHECK",
                description="禁止忽视文化检查结果",
                violation_type=AIBehaviorViolation.IGNORE_CULTURE_CHECK,
                severity="high",
                enforcement_action="warn_and_guide",
                message="⚠️ 违规警告：AI工具忽视了文化检查结果！必须分析并解决所有问题。",
            ),
            AIBehaviorRule(
                rule_id="NO_SKIP_TESTS",
                description="禁止跳过测试",
                violation_type=AIBehaviorViolation.SKIP_TESTS,
                severity="medium",
                enforcement_action="warn_and_guide",
                message="⚠️ 违规警告：AI工具试图跳过测试！测试是质量保证的基础。",
            ),
        ]

    def detect_hook_manipulation(self) -> List[AIBehaviorViolation]:
        """检测Git钩子操作"""
        violations = []

        # 检查是否有禁用钩子的操作
        git_hooks_dir = self.project_path / ".git" / "hooks"
        if git_hooks_dir.exists():
            for hook_file in git_hooks_dir.glob("*"):
                if hook_file.is_file() and not os.access(hook_file, os.X_OK):
                    # 发现被禁用的钩子
                    violations.append(AIBehaviorViolation.DISABLE_HOOKS)
                    self.logger.critical(f"检测到被禁用的Git钩子: {hook_file.name}")

        return violations

    def detect_bypass_attempts(self) -> List[AIBehaviorViolation]:
        """检测绕过质量门禁的尝试"""
        violations = []

        # 检查最近的Git操作
        try:
            # 检查最近的提交是否绕过了钩子
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--oneline",
                    "-10",
                    "--grep=bypass",
                    "--grep=skip",
                    "--grep=disable",
                ],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                violations.append(AIBehaviorViolation.BYPASS_QUALITY_GATE)
                self.logger.warning("检测到可能的绕过行为在Git历史中")

        except Exception as e:
            self.logger.error(f"检测绕过尝试时出错: {e}")

        return violations

    def check_culture_compliance(self) -> Dict[str, Any]:
        """检查文化合规性并提供详细问题信息 - 收集所有问题"""
        try:
            enforcer = CultureEnforcer(str(self.project_path))
            result = enforcer.enforce_all()

            # 提取详细的违规信息
            violations = result.get("violations", [])
            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warning"]

            # 构建详细的错误信息 - 显示所有错误，不限制数量
            detailed_errors = []
            for i, error in enumerate(errors, 1):
                error_info = {
                    "index": i,
                    "description": error.description,
                    "severity": error.severity,
                    "principle": getattr(error, "principle", "unknown"),
                    "file_path": getattr(error, "file_path", None),
                    "line_number": getattr(error, "line_number", None),
                    "suggestion": getattr(error, "suggestion", None),
                }
                detailed_errors.append(error_info)

            # 构建详细的警告信息 - 显示所有警告
            detailed_warnings = []
            for i, warning in enumerate(warnings, 1):
                warning_info = {
                    "index": i,
                    "description": warning.description,
                    "severity": warning.severity,
                    "principle": getattr(warning, "principle", "unknown"),
                    "file_path": getattr(warning, "file_path", None),
                    "line_number": getattr(warning, "line_number", None),
                    "suggestion": getattr(warning, "suggestion", None),
                }
                detailed_warnings.append(warning_info)

            # 记录发现的问题数量
            total_issues = len(detailed_errors) + len(detailed_warnings)
            if total_issues > 0:
                self.logger.warning(
                    f"发现 {len(detailed_errors)} 个错误和 {len(detailed_warnings)} 个警告，共 {total_issues} 个问题"
                )

            return {
                "compliant": result.get("errors", 0) == 0,  # 只有没有错误才算合规
                "errors": result.get("errors", 0),
                "warnings": result.get("warnings", 0),
                "score": result.get("score", 100),
                "detailed_errors": detailed_errors,
                "detailed_warnings": detailed_warnings,
                "total_issues": total_issues,
            }

        except Exception as e:
            self.logger.error(f"文化合规检查失败: {e}")
            return {"compliant": False, "error": str(e)}

    def record_violation(self, violation: AIBehaviorViolation, context: Dict[str, Any] = None):
        """记录AI行为违规"""
        violation_record = {
            "timestamp": time.time(),
            "violation_type": violation.value,
            "context": context or {},
            "severity": self._get_rule_by_violation(violation).severity,
            "message": self._get_rule_by_violation(violation).message,
        }

        # 读取现有违规记录
        violations = []
        if self.violation_log.exists():
            try:
                with open(self.violation_log, "r", encoding="utf-8") as f:
                    violations = json.load(f)
            except Exception:
                violations = []

        # 添加新违规记录
        violations.append(violation_record)

        # 保存违规记录
        with open(self.violation_log, "w", encoding="utf-8") as f:
            json.dump(violations, f, indent=2, ensure_ascii=False)

        self.logger.error(f"记录AI行为违规: {violation.value}")

    def _get_rule_by_violation(self, violation: AIBehaviorViolation) -> AIBehaviorRule:
        """根据违规类型获取规则"""
        for rule in self.rules:
            if rule.violation_type == violation:
                return rule

        # 默认规则
        return AIBehaviorRule(
            rule_id="UNKNOWN",
            description="未知违规",
            violation_type=violation,
            severity="medium",
            enforcement_action="warn",
            message="检测到未知的AI行为违规",
        )

    def enforce_ai_behavior(self) -> Dict[str, Any]:
        """强制执行AI行为规范"""
        self.logger.info("开始AI行为规范检查...")

        violations = []

        # 1. 检测钩子操作
        hook_violations = self.detect_hook_manipulation()
        violations.extend(hook_violations)

        # 2. 检测绕过尝试
        bypass_violations = self.detect_bypass_attempts()
        violations.extend(bypass_violations)

        # 3. 检查文化合规性
        culture_status = self.check_culture_compliance()

        # 记录所有违规
        for violation in violations:
            self.record_violation(violation)

        # 生成执行报告
        report = {
            "timestamp": time.time(),
            "violations_detected": len(violations),
            "violations": [v.value for v in violations],
            "culture_compliance": culture_status,
            "enforcement_actions": [],
        }

        # 执行强制措施
        enforcement_actions = []
        for violation in violations:
            rule = self._get_rule_by_violation(violation)

            if rule.enforcement_action == "block_operation":
                print(f"\n{rule.message}")
                print("🛑 操作被阻止！必须遵循文化标准。")
                enforcement_actions.append(f"blocked_{violation.value}")

            elif rule.enforcement_action == "warn_and_guide":
                print(f"\n{rule.message}")
                print("📋 请按照以下步骤解决问题：")
                self._provide_guidance(violation)
                enforcement_actions.append(f"warned_{violation.value}")

        # 如果文化检查有问题，显示完整的问题分析
        if not culture_status.get("compliant", True) or culture_status.get("total_issues", 0) > 0:
            print("\n🔍 完整问题分析报告:")
            print(f"📊 文化质量评分: {culture_status.get('score', 0)}/100")
            print(f"❌ 错误: {culture_status.get('errors', 0)} 个")
            print(f"⚠️  警告: {culture_status.get('warnings', 0)} 个")
            print(f"📋 总问题数: {culture_status.get('total_issues', 0)} 个")

            # 显示所有错误详情
            detailed_errors = culture_status.get("detailed_errors", [])
            if detailed_errors:
                print(f"\n🚨 所有错误详情 ({len(detailed_errors)} 个):")
                for error in detailed_errors:
                    print(f"  {error['index']}. {error['description']}")
                    if error.get("file_path"):
                        print(f"     📁 文件: {error['file_path']}")
                    if error.get("line_number"):
                        print(f"     📍 行号: {error['line_number']}")
                    if error.get("suggestion"):
                        print(f"     💡 建议: {error['suggestion']}")
                    print()

            # 显示所有警告详情
            detailed_warnings = culture_status.get("detailed_warnings", [])
            if detailed_warnings:
                print(f"⚠️  所有警告详情 ({len(detailed_warnings)} 个):")
                for warning in detailed_warnings:
                    print(f"  {warning['index']}. {warning['description']}")
                    if warning.get("file_path"):
                        print(f"     📁 文件: {warning['file_path']}")
                    if warning.get("line_number"):
                        print(f"     📍 行号: {warning['line_number']}")
                    if warning.get("suggestion"):
                        print(f"     💡 建议: {warning['suggestion']}")
                    print()

            # 提供综合修复指导
            print("🎯 综合修复指导:")
            print(f"   1. 上面列出了所有 {culture_status.get('total_issues', 0)} 个问题的详细信息")
            print(f"   2. 请逐一修复每个问题，特别是 {len(detailed_errors)} 个错误")
            print("   3. 根据每个问题的建议进行修复")
            print("   4. 修复完成后重新提交，系统会重新检查所有问题")
            print("   5. 只有所有错误都解决后才能成功推送")

        report["enforcement_actions"] = enforcement_actions
        return report

    def _provide_guidance(self, violation: AIBehaviorViolation):
        """提供违规解决指导"""
        guidance = {
            AIBehaviorViolation.BYPASS_QUALITY_GATE: [
                "1. 运行 'python -c \"from aiculture.culture_enforcer import CultureEnforcer; print(CultureEnforcer('.').enforce_all())\"'",
                "2. 分析所有错误和警告",
                "3. 逐一修复每个问题",
                "4. 重新运行检查确认修复",
                "5. 正常提交和推送",
            ],
            AIBehaviorViolation.DISABLE_HOOKS: [
                "1. 重新启用所有Git钩子: chmod +x .git/hooks/*",
                "2. 运行文化检查找出问题",
                "3. 修复所有发现的问题",
                "4. 通过正当途径提交代码",
            ],
            AIBehaviorViolation.IGNORE_CULTURE_CHECK: [
                "1. 仔细阅读文化检查报告",
                "2. 理解每个错误和警告的含义",
                "3. 制定修复计划",
                "4. 逐步实施修复",
                "5. 验证修复效果",
            ],
        }

        steps = guidance.get(violation, ["请联系项目维护者获取帮助"])
        for step in steps:
            print(f"   {step}")

    def get_violation_history(self) -> List[Dict[str, Any]]:
        """获取违规历史"""
        if not self.violation_log.exists():
            return []

        try:
            with open(self.violation_log, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"读取违规历史失败: {e}")
            return []

    def generate_behavior_report(self) -> Dict[str, Any]:
        """生成AI行为报告"""
        violations = self.get_violation_history()

        # 统计违规类型
        violation_stats = {}
        for violation in violations:
            vtype = violation["violation_type"]
            violation_stats[vtype] = violation_stats.get(vtype, 0) + 1

        # 计算行为评分
        total_violations = len(violations)
        critical_violations = len([v for v in violations if v.get("severity") == "critical"])

        behavior_score = max(0, 100 - (critical_violations * 30) - (total_violations * 5))

        return {
            "behavior_score": behavior_score,
            "total_violations": total_violations,
            "critical_violations": critical_violations,
            "violation_stats": violation_stats,
            "recent_violations": violations[-5:] if violations else [],
            "compliance_status": ("compliant" if behavior_score >= 80 else "non_compliant"),
        }


def main():
    """主函数 - 用于命令行调用"""
    enforcer = AIBehaviorEnforcer()

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        # 生成行为报告
        report = enforcer.generate_behavior_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        # 执行行为检查
        result = enforcer.enforce_ai_behavior()

        if result["violations_detected"] > 0:
            print(f"\n🚨 检测到 {result['violations_detected']} 个AI行为违规！")
            sys.exit(1)
        else:
            print("✅ AI行为规范检查通过")


if __name__ == "__main__":
    main()
