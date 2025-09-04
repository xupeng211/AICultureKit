#!/usr/bin/env python3
"""
🚀 Cursor闭环执行器

整合项目上下文加载和质量检查，提供完整的闭环开发流程。
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from context_loader import ProjectContextLoader
from env_checker import EnvironmentChecker
from quality_checker import QualityChecker


class CursorClosedLoopRunner:
    """Cursor闭环执行器"""

    def __init__(self, project_root: str = ".", task_description: str = ""):
        """
        初始化闭环执行器

        Args:
            project_root: 项目根目录
            task_description: 任务描述
        """
        self.project_root = Path(project_root).resolve()
        self.task_description = task_description
        self.execution_log: Dict[str, Any] = {}

    def run_complete_cycle(self) -> Dict[str, Any]:
        """
        运行完整的闭环流程

        Returns:
            执行结果字典
        """
        print("🚀 开始Cursor闭环开发流程...")

        self.execution_log = {
            "timestamp": datetime.now().isoformat(),
            "task_description": self.task_description,
            "project_root": str(self.project_root),
            "phases": {},
            "overall_success": False,
        }

        # 定义执行阶段
        phases = [
            ("env_check", "开发环境检查", self._check_environment),
            ("context_loading", "项目上下文加载", self._load_context),
            ("rule_application", "开发规则应用", self._apply_rules),
            ("task_breakdown", "任务分解分析", self._analyze_task),
            ("quality_check", "代码质量检查", self._run_quality_check),
            ("git_operations", "Git操作处理", self._handle_git_operations),
            ("documentation", "文档更新", self._update_documentation),
        ]

        # 执行各个阶段
        for phase_id, phase_name, phase_func in phases:
            print(f"\n📋 阶段: {phase_name}")

            try:
                success, message, details = phase_func()

                self.execution_log["phases"][phase_id] = {
                    "name": phase_name,
                    "success": success,
                    "message": message,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                }

                if success:
                    print(f"✅ {phase_name}成功: {message}")
                else:
                    print(f"❌ {phase_name}失败: {message}")
                    # 某些阶段失败不应该终止整个流程
                    if phase_id in ["quality_check"]:
                        print("⚠️ 关键阶段失败，但继续执行...")

            except Exception as e:
                print(f"💥 {phase_name}异常: {e}")
                self.execution_log["phases"][phase_id] = {
                    "name": phase_name,
                    "success": False,
                    "message": f"阶段异常: {e}",
                    "details": {"exception": str(e)},
                    "timestamp": datetime.now().isoformat(),
                }

        # 判断整体成功状态
        self.execution_log["overall_success"] = self._evaluate_overall_success()

        if self.execution_log["overall_success"]:
            print("\n🎉 闭环开发流程成功完成！")
        else:
            print("\n⚠️ 闭环开发流程完成，但存在一些问题")

        return self.execution_log

    def _load_context(self) -> Tuple[bool, str, Dict]:
        """加载项目上下文"""
        try:
            loader = ProjectContextLoader(str(self.project_root))
            context = loader.load_all_context()
            loader.save_context()

            return (
                True,
                f"成功加载项目上下文，包含{len(context.get('existing_modules', {}).get('python_modules', []))}个模块",
                {
                    "context_summary": {
                        "python_files": context.get("project_stats", {}).get(
                            "total_python_files", 0
                        ),
                        "test_files": context.get("project_stats", {}).get(
                            "total_test_files", 0
                        ),
                        "lines_of_code": context.get("project_stats", {}).get(
                            "total_lines_of_code", 0
                        ),
                        "git_branch": context.get("git_info", {}).get("current_branch"),
                    }
                },
            )

        except Exception as e:
            return False, f"上下文加载失败: {e}", {"exception": str(e)}

    def _apply_rules(self) -> Tuple[bool, str, Dict]:
        """应用开发规则"""
        try:
            rules_file = self.project_root / "rules.md"
            if not rules_file.exists():
                return False, "rules.md文件不存在", {"suggestion": "创建开发规则文件"}

            # 读取规则内容
            rules_content = rules_file.read_text(encoding="utf-8")

            # 检查规则完整性
            required_sections = ["基本原则", "代码规范", "Git工作流", "检查点清单"]
            missing_sections = []

            for section in required_sections:
                if section not in rules_content:
                    missing_sections.append(section)

            if missing_sections:
                return (
                    False,
                    f"规则文件缺少必要章节: {missing_sections}",
                    {"missing_sections": missing_sections},
                )

            return (
                True,
                "开发规则验证通过",
                {
                    "rules_file_size": len(rules_content),
                    "sections_found": required_sections,
                },
            )

        except Exception as e:
            return False, f"规则应用失败: {e}", {"exception": str(e)}

    def _analyze_task(self) -> Tuple[bool, str, Dict]:
        """分析任务分解"""
        if not self.task_description.strip():
            return True, "未提供具体任务，跳过任务分析", {"skipped": True}

        try:
            # 简单的任务分析
            task_words = self.task_description.split()
            complexity_indicators = ["模块", "系统", "接口", "数据库", "API", "服务"]

            complexity_score = sum(
                1 for word in task_words if word in complexity_indicators
            )

            # 根据复杂度评估建议的子任务
            if complexity_score >= 3:
                suggested_subtasks = ["设计模块架构", "实现核心功能", "编写单元测试", "集成测试", "文档编写"]
            elif complexity_score >= 1:
                suggested_subtasks = ["实现核心功能", "编写单元测试", "文档更新"]
            else:
                suggested_subtasks = ["实现功能", "添加测试"]

            return (
                True,
                f"任务分析完成，复杂度评分: {complexity_score}",
                {
                    "task_length": len(self.task_description),
                    "word_count": len(task_words),
                    "complexity_score": complexity_score,
                    "suggested_subtasks": suggested_subtasks,
                },
            )

        except Exception as e:
            return False, f"任务分析失败: {e}", {"exception": str(e)}

    def _run_quality_check(self) -> Tuple[bool, str, Dict]:
        """运行代码质量检查"""
        try:
            checker = QualityChecker(str(self.project_root))
            results = checker.run_all_checks()
            checker.save_results()
            checker.save_iteration_log()

            return (
                results["overall_status"] == "passed",
                f"质量检查{results['overall_status']}，重试{results['retry_count']}次",
                {
                    "overall_status": results["overall_status"],
                    "retry_count": results["retry_count"],
                    "checks_summary": {
                        check_id: {
                            "success": check_data["success"],
                            "message": check_data["message"],
                        }
                        for check_id, check_data in results.get("checks", {}).items()
                    },
                },
            )

        except Exception as e:
            return False, f"质量检查失败: {e}", {"exception": str(e)}

    def _handle_git_operations(self) -> Tuple[bool, str, Dict]:
        """处理Git操作"""
        try:
            git_operations = []

            # 检查Git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return False, "Git状态检查失败", {"error": result.stderr}

            changes = result.stdout.strip().split("\n") if result.stdout.strip() else []

            if not changes:
                return True, "工作区干净，无需Git操作", {"changes": []}

            # 如果有变更，可以选择性地进行操作
            git_operations.append(f"发现 {len(changes)} 个文件变更")

            # 这里可以添加自动提交逻辑（可选）
            # 但为了安全，我们只报告状态

            return (
                True,
                f"Git状态检查完成，{len(changes)}个文件有变更",
                {
                    "changes_count": len(changes),
                    "changes": changes[:10],  # 只显示前10个
                    "operations": git_operations,
                },
            )

        except Exception as e:
            return False, f"Git操作失败: {e}", {"exception": str(e)}

    def _update_documentation(self) -> Tuple[bool, str, Dict]:
        """更新文档"""
        try:
            docs_updated = []

            # 检查是否需要更新README
            readme_file = self.project_root / "README.md"
            if readme_file.exists():
                docs_updated.append("README.md存在")
            else:
                docs_updated.append("README.md缺失")

            # 检查API文档
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                doc_files = list(docs_dir.rglob("*.md"))
                docs_updated.append(f"文档目录包含{len(doc_files)}个文件")

            return (
                True,
                f"文档检查完成，{len(docs_updated)}项检查",
                {"documentation_items": docs_updated},
            )

        except Exception as e:
            return False, f"文档更新失败: {e}", {"exception": str(e)}

    def _check_environment(self) -> Tuple[bool, str, Dict]:
        """检查开发环境"""
        try:
            checker = EnvironmentChecker(str(self.project_root))
            results = checker.run_all_checks()

            all_passed = all(result["success"] for result in results.values())
            failed_checks = [
                result["name"] for result in results.values() if not result["success"]
            ]

            if all_passed:
                return (
                    True,
                    "开发环境检查全部通过",
                    {
                        "total_checks": len(results),
                        "passed_checks": len(results),
                        "failed_checks": [],
                    },
                )
            else:
                return (
                    False,
                    f"环境检查失败，{len(failed_checks)}项需要修复",
                    {
                        "total_checks": len(results),
                        "passed_checks": len(results) - len(failed_checks),
                        "failed_checks": failed_checks,
                        "fix_suggestions": checker.get_action_items(),
                    },
                )

        except Exception as e:
            return False, f"环境检查失败: {e}", {"exception": str(e)}

    def _evaluate_overall_success(self) -> bool:
        """评估整体成功状态"""
        critical_phases = ["env_check", "context_loading", "quality_check"]

        for phase_id in critical_phases:
            phase_result = self.execution_log["phases"].get(phase_id)
            if not phase_result or not phase_result.get("success"):
                return False

        return True

    def save_execution_log(
        self, output_file: str = "logs/cursor_execution.json"
    ) -> None:
        """保存执行日志"""
        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)

        print(f"💾 执行日志已保存到: {output_path}")

    def print_summary(self) -> None:
        """打印执行摘要"""
        print(f"\n📊 闭环执行摘要:")
        print(f"   🎯 任务: {self.task_description or '未指定'}")
        print(f"   ⚡ 整体状态: {'成功' if self.execution_log['overall_success'] else '部分失败'}")

        for phase_id, phase_data in self.execution_log["phases"].items():
            status = "✅" if phase_data["success"] else "❌"
            print(f"   {status} {phase_data['name']}: {phase_data['message']}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor闭环执行器")
    parser.add_argument("--task", default="", help="任务描述")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument(
        "--output", default="logs/cursor_execution.json", help="执行日志输出文件"
    )
    parser.add_argument("--summary", action="store_true", help="显示执行摘要")

    args = parser.parse_args()

    runner = CursorClosedLoopRunner(args.project_root, args.task)
    results = runner.run_complete_cycle()
    runner.save_execution_log(args.output)

    if args.summary:
        runner.print_summary()

    # 返回适当的退出代码
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
