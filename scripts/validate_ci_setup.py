#!/usr/bin/env python3
"""
CI/CD 配置验证脚本
验证工作流触发逻辑和质量门控配置
"""

import json
import re
from pathlib import Path

import yaml


class CICDValidator:
    """CI/CD 配置验证器"""

    def __init__(self, project_root: Path | None = None):
        self.root = project_root or Path.cwd()
        self.github_dir = self.root / ".github" / "workflows"

    def validate_workflow_triggers(self):
        """验证工作流触发逻辑"""
        print("🔍 验证工作流触发逻辑...")

        # 检查 Quick Check 工作流
        quick_check_path = self.github_dir / "quick-check.yml"
        if quick_check_path.exists():
            with open(quick_check_path) as f:
                quick_check = yaml.safe_load(f)

            triggers = quick_check.get("on", {})
            if "push" in triggers:
                branches = triggers["push"].get("branches", [])
                print(f"  ✅ Quick Check 触发分支: {branches}")
                if "feature/**" in branches:
                    print("  ✅ feature 分支触发 Quick Check - 正确")
                else:
                    print("  ❌ 缺少 feature/** 分支触发")
            else:
                print("  ❌ Quick Check 缺少 push 触发")
        else:
            print("  ❌ quick-check.yml 不存在")

        # 检查 Quality Gate 工作流
        quality_gate_path = self.github_dir / "quality-gate.yml"
        if quality_gate_path.exists():
            with open(quality_gate_path) as f:
                quality_gate = yaml.safe_load(f)

            triggers = quality_gate.get("on", {})
            if "pull_request" in triggers:
                branches = triggers["pull_request"].get("branches", [])
                print(f"  ✅ Quality Gate 触发分支: {branches}")
                if "main" in branches:
                    print("  ✅ PR to main 触发 Quality Gate - 正确")
                else:
                    print("  ❌ 缺少 main 分支 PR 触发")
            else:
                print("  ❌ Quality Gate 缺少 pull_request 触发")
        else:
            print("  ❌ quality-gate.yml 不存在")

    def validate_coverage_config(self):
        """验证覆盖率配置一致性"""
        print("\n📊 验证覆盖率配置...")

        # 检查 pyproject.toml
        pyproject_path = self.root / "pyproject.toml"
        pyproject_threshold = None
        if pyproject_path.exists():
            with open(pyproject_path) as f:
                content = f.read()
                match = re.search(r"fail_under\s*=\s*(\d+)", content)
                if match:
                    pyproject_threshold = int(match.group(1))
                    print(f"  ✅ pyproject.toml 覆盖率阈值: {pyproject_threshold}%")
                else:
                    print("  ❌ pyproject.toml 缺少 fail_under 配置")
        else:
            print("  ❌ pyproject.toml 不存在")

        # 检查 Quality Gate 工作流中的阈值
        quality_gate_path = self.github_dir / "quality-gate.yml"
        workflow_threshold = None
        if quality_gate_path.exists():
            with open(quality_gate_path) as f:
                content = f.read()
                match = re.search(r"COVERAGE_THRESHOLD_MIN:\s*(\d+)", content)
                if match:
                    workflow_threshold = int(match.group(1))
                    print(f"  ✅ workflow 覆盖率阈值: {workflow_threshold}%")
                else:
                    print("  ❌ workflow 缺少 COVERAGE_THRESHOLD_MIN")
        else:
            print("  ❌ quality-gate.yml 不存在")

        # 检查一致性
        if pyproject_threshold and workflow_threshold:
            if pyproject_threshold == workflow_threshold:
                print(f"  ✅ 配置一致: {pyproject_threshold}%")
            else:
                print(
                    f"  ⚠️  配置不一致: pyproject.toml={pyproject_threshold}%, workflow={workflow_threshold}%"
                )

    def get_current_coverage(self):
        """获取当前覆盖率"""
        print("\n📈 检查当前覆盖率...")

        coverage_json_path = self.root / "coverage.json"
        if coverage_json_path.exists():
            try:
                with open(coverage_json_path) as f:
                    coverage_data = json.load(f)

                totals = coverage_data.get("totals", {})
                coverage_percent = totals.get("percent_covered", 0)
                covered_lines = totals.get("covered_lines", 0)
                total_lines = totals.get("num_statements", 0)

                print(f"  📊 当前覆盖率: {coverage_percent:.1f}%")
                print(f"  📝 覆盖行数: {covered_lines}/{total_lines}")

                return coverage_percent
            except Exception as e:
                print(f"  ❌ 解析 coverage.json 失败: {e}")
        else:
            print("  ⚠️  coverage.json 不存在，运行测试生成覆盖率报告")

        return None

    def validate_soft_fail_config(self):
        """验证软失败配置"""
        print("\n🛡️ 验证软失败配置...")

        quality_gate_path = self.github_dir / "quality-gate.yml"
        if quality_gate_path.exists():
            with open(quality_gate_path) as f:
                content = f.read()

            # 检查 SOFT_FAIL 环境变量
            if "SOFT_FAIL: true" in content:
                print("  ✅ 软失败开关已启用")

                # 检查各个检查步骤是否使用 continue-on-error
                checks = [
                    ("ruff check", "Ruff 代码检查"),
                    ("bandit", "安全检查"),
                    ("detect-secrets", "密钥扫描"),
                    ("mypy", "类型检查"),
                ]

                for check_cmd, check_name in checks:
                    if "continue-on-error: ${ env.SOFT_FAIL == 'true' }" in content:
                        if check_cmd.lower() in content.lower():
                            print(f"  ✅ {check_name} 配置为软失败")

                # 检查测试是否为硬阻断
                if "Test with coverage (BLOCKING)" in content:
                    if (
                        "continue-on-error"
                        not in content.split("Test with coverage (BLOCKING)")[1].split(
                            "- name:"
                        )[0]
                    ):
                        print("  ✅ 测试覆盖率配置为硬阻断")
                    else:
                        print("  ⚠️  测试覆盖率可能不是硬阻断")
            else:
                print("  ❌ 软失败开关未启用")
        else:
            print("  ❌ quality-gate.yml 不存在")

    def run_validation(self):
        """运行完整验证"""
        print("🔧 AICultureKit CI/CD 配置验证")
        print("=" * 50)

        self.validate_workflow_triggers()
        self.validate_coverage_config()
        current_coverage = self.get_current_coverage()
        self.validate_soft_fail_config()

        print("\n" + "=" * 50)
        print("📋 验证总结:")

        # 基于当前覆盖率给出建议
        if current_coverage:
            if current_coverage >= 25:
                print(f"  ✅ 当前覆盖率 {current_coverage:.1f}% 符合阈值要求")
            else:
                print(f"  ⚠️  当前覆盖率 {current_coverage:.1f}% 低于25%阈值，需要提升")

        print("\n🚀 下一步建议:")
        print("  1. 确保所有核心模块测试通过")
        print("  2. 逐步提升覆盖率至30%")
        print("  3. 验证 CI 流程稳定性")
        print("  4. 准备进入阶段1质量提升")


if __name__ == "__main__":
    validator = CICDValidator()
    validator.run_validation()
