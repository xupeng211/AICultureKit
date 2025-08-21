#!/usr/bin/env python3
"""
AICultureKit IDE集成脚本
提供一键聚合、生成补丁、验证的完整工作流
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict


class AICultureKitIDE:
    """AICultureKit IDE集成主类"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.artifacts_dir = self.project_root / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

    def run_full_workflow(
        self, base: str = "origin/main", auto_apply: bool = False
    ) -> Dict[str, Any]:
        """运行完整的一键工作流"""

        print("🚀 AICultureKit IDE 一键工作流启动")
        print("=" * 60)

        workflow_result = {
            "steps": [],
            "success": True,
            "total_problems_before": 0,
            "total_problems_after": 0,
            "patches_generated": 0,
            "patches_applied": 0,
        }

        # 步骤1: 聚合问题
        print("\n📊 步骤1: 聚合问题...")
        step1_result = self._run_problem_aggregator(base)
        workflow_result["steps"].append(step1_result)

        if not step1_result["success"]:
            print("❌ 问题聚合失败，工作流终止")
            workflow_result["success"] = False
            return workflow_result

        workflow_result["total_problems_before"] = step1_result.get("total_problems", 0)
        print(f"✅ 发现 {workflow_result['total_problems_before']} 个问题")

        if workflow_result["total_problems_before"] == 0:
            print("🎉 没有发现问题，工作流完成")
            return workflow_result

        # 步骤2: 生成AI补丁
        print("\n🤖 步骤2: 生成AI修复补丁...")
        step2_result = self._run_ai_fix_agent()
        workflow_result["steps"].append(step2_result)

        if not step2_result["success"]:
            print("⚠️ AI补丁生成失败，但继续工作流")
        else:
            workflow_result["patches_generated"] = step2_result.get("patches_count", 0)
            print(f"✅ 生成 {workflow_result['patches_generated']} 个补丁")

        # 步骤3: 应用补丁（可选）
        if auto_apply and workflow_result["patches_generated"] > 0:
            print("\n🔧 步骤3: 自动应用补丁...")
            step3_result = self._apply_patches()
            workflow_result["steps"].append(step3_result)

            if step3_result["success"]:
                workflow_result["patches_applied"] = step3_result.get(
                    "patches_applied", 0
                )
                print(f"✅ 应用 {workflow_result['patches_applied']} 个补丁")
            else:
                print("⚠️ 补丁应用失败")

        # 步骤4: 验证修复效果
        print("\n🔍 步骤4: 验证修复效果...")
        step4_result = self._verify_fixes(base)
        workflow_result["steps"].append(step4_result)

        if step4_result["success"]:
            workflow_result["total_problems_after"] = step4_result.get(
                "total_problems", 0
            )
            print(f"✅ 修复后剩余 {workflow_result['total_problems_after']} 个问题")
        else:
            print("⚠️ 修复验证失败")

        # 生成工作流摘要
        self._generate_workflow_summary(workflow_result)

        print("\n" + "=" * 60)
        print("🎉 AICultureKit IDE 一键工作流完成")

        return workflow_result

    def _run_problem_aggregator(self, base: str) -> Dict[str, Any]:
        """运行问题聚合器"""

        try:
            cmd = [
                "python",
                "-m",
                "tools.problem_aggregator.aggregator",
                "--base",
                base,
                "--out",
                str(self.artifacts_dir / "ide_problems.json"),
                "--md",
                str(self.artifacts_dir / "ide_problems_report.md"),
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                # 读取问题数量
                problems_file = self.artifacts_dir / "ide_problems.json"
                if problems_file.exists():
                    with open(problems_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    total_problems = data.get("summary", {}).get("total", 0)
                else:
                    total_problems = 0

                return {
                    "step": "problem_aggregation",
                    "success": True,
                    "total_problems": total_problems,
                    "output_file": str(problems_file),
                    "report_file": str(self.artifacts_dir / "ide_problems_report.md"),
                }
            else:
                return {
                    "step": "problem_aggregation",
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout,
                }

        except Exception as e:
            return {"step": "problem_aggregation", "success": False, "error": str(e)}

    def _run_ai_fix_agent(self) -> Dict[str, Any]:
        """运行AI修复代理"""

        try:
            problems_file = self.artifacts_dir / "ide_problems.json"
            if not problems_file.exists():
                return {
                    "step": "ai_fix_generation",
                    "success": False,
                    "error": "问题文件不存在",
                }

            cmd = [
                "python",
                "-m",
                "tools.ai_fix_agent.agent",
                "--in",
                str(problems_file),
                "--out",
                str(self.artifacts_dir / "ide_ai_fixes"),
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=180
            )

            if result.returncode == 0:
                # 统计生成的补丁数量
                fixes_dir = self.artifacts_dir / "ide_ai_fixes"
                patches_count = (
                    len(list(fixes_dir.glob("*.patch"))) if fixes_dir.exists() else 0
                )

                return {
                    "step": "ai_fix_generation",
                    "success": True,
                    "patches_count": patches_count,
                    "output_dir": str(fixes_dir),
                }
            else:
                return {
                    "step": "ai_fix_generation",
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout,
                }

        except Exception as e:
            return {"step": "ai_fix_generation", "success": False, "error": str(e)}

    def _apply_patches(self) -> Dict[str, Any]:
        """应用AI生成的补丁"""

        try:
            fixes_dir = self.artifacts_dir / "ide_ai_fixes"
            apply_script = fixes_dir / "apply_fixes.sh"

            if not apply_script.exists():
                return {
                    "step": "patch_application",
                    "success": False,
                    "error": "应用脚本不存在",
                }

            # 使脚本可执行
            apply_script.chmod(0o755)

            result = subprocess.run(
                ["./apply_fixes.sh"],
                cwd=fixes_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # 统计应用的补丁数量（从输出中解析）
            patches_applied = result.stdout.count("补丁应用成功")

            return {
                "step": "patch_application",
                "success": result.returncode == 0,
                "patches_applied": patches_applied,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {"step": "patch_application", "success": False, "error": str(e)}

    def _verify_fixes(self, base: str) -> Dict[str, Any]:
        """验证修复效果"""

        try:
            cmd = [
                "python",
                "-m",
                "tools.problem_aggregator.aggregator",
                "--base",
                base,
                "--out",
                str(self.artifacts_dir / "ide_post_fix_problems.json"),
                "--md",
                str(self.artifacts_dir / "ide_post_fix_report.md"),
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                # 读取修复后的问题数量
                problems_file = self.artifacts_dir / "ide_post_fix_problems.json"
                if problems_file.exists():
                    with open(problems_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    total_problems = data.get("summary", {}).get("total", 0)
                else:
                    total_problems = 0

                return {
                    "step": "fix_verification",
                    "success": True,
                    "total_problems": total_problems,
                    "output_file": str(problems_file),
                    "report_file": str(self.artifacts_dir / "ide_post_fix_report.md"),
                }
            else:
                return {
                    "step": "fix_verification",
                    "success": False,
                    "error": result.stderr,
                }

        except Exception as e:
            return {"step": "fix_verification", "success": False, "error": str(e)}

    def _generate_workflow_summary(self, workflow_result: Dict[str, Any]) -> None:
        """生成工作流摘要"""

        summary_file = self.artifacts_dir / "ide_workflow_summary.md"

        lines = []
        lines.append("# 🚀 AICultureKit IDE 工作流摘要")
        lines.append("")
        lines.append(f"**执行时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 整体结果
        status = "✅ 成功" if workflow_result["success"] else "❌ 失败"
        lines.append(f"**整体状态**: {status}")
        lines.append("")

        # 问题统计
        before = workflow_result["total_problems_before"]
        after = workflow_result["total_problems_after"]
        fixed = before - after if after >= 0 else 0

        lines.append("## 📊 问题统计")
        lines.append("")
        lines.append(f"- **修复前**: {before} 个问题")
        lines.append(f"- **修复后**: {after} 个问题")
        lines.append(f"- **已修复**: {fixed} 个问题")
        lines.append(
            f"- **修复率**: {(fixed/before*100):.1f}%"
            if before > 0
            else "- **修复率**: N/A"
        )
        lines.append("")

        # 补丁统计
        lines.append("## 🤖 AI修复统计")
        lines.append("")
        lines.append(f"- **生成补丁**: {workflow_result['patches_generated']} 个")
        lines.append(f"- **应用补丁**: {workflow_result['patches_applied']} 个")
        lines.append("")

        # 步骤详情
        lines.append("## 📋 执行步骤")
        lines.append("")

        for i, step in enumerate(workflow_result["steps"], 1):
            step_name = step["step"]
            step_status = "✅" if step["success"] else "❌"
            lines.append(f"{i}. **{step_name}**: {step_status}")

            if not step["success"] and "error" in step:
                lines.append(f"   - 错误: {step['error']}")

        lines.append("")

        # 下一步建议
        lines.append("## 🎯 下一步建议")
        lines.append("")

        if after > 0:
            lines.append(
                f"1. 查看剩余 {after} 个问题: `artifacts/ide_post_fix_report.md`"
            )
            lines.append("2. 手工修复无法自动处理的问题")
            lines.append("3. 重新运行工作流验证修复效果")
        else:
            lines.append("🎉 所有问题已修复，可以提交代码")

        # 写入文件
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"📋 工作流摘要已保存: {summary_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AICultureKit IDE一键工作流")
    parser.add_argument("--base", default="origin/main", help="Git基准分支")
    parser.add_argument(
        "--auto-apply", action="store_true", help="自动应用AI生成的补丁"
    )
    parser.add_argument("--project-root", default=".", help="项目根目录")

    args = parser.parse_args()

    # 运行工作流
    ide = AICultureKitIDE(args.project_root)
    result = ide.run_full_workflow(args.base, args.auto_apply)

    # 退出码
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
