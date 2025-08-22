#!/usr/bin/env python3
"""
问题聚合器

一次性收集和展示项目中的所有问题，避免多次循环修复。
"""

import json
import sys
from pathlib import Path
from typing import Any

from .ai_behavior_enforcer import AIBehaviorEnforcer
from .culture_enforcer import CultureEnforcer
from .error_handling import get_logger


class ProblemAggregator:
    """问题聚合器 - 一次性收集所有问题"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.logger = get_logger("problem_aggregator")

    def collect_all_problems(self) -> dict[str, Any]:
        """收集项目中的所有问题"""
        self.logger.info("开始收集所有问题...")

        all_problems = {
            "timestamp": self._get_timestamp(),
            "project_path": str(self.project_path),
            "summary": {
                "total_errors": 0,
                "total_warnings": 0,
                "total_issues": 0,
                "blocking_issues": 0,
            },
            "categories": {
                "ai_behavior_violations": [],
                "culture_errors": [],
                "culture_warnings": [],
                "security_issues": [],
                "performance_issues": [],
                "accessibility_issues": [],
            },
            "files_affected": set(),
            "fix_priority": [],
        }

        # 1. 检查AI行为违规
        try:
            behavior_enforcer = AIBehaviorEnforcer(str(self.project_path))
            behavior_result = behavior_enforcer.enforce_ai_behavior()

            if behavior_result["violations_detected"] > 0:
                all_problems["categories"]["ai_behavior_violations"] = behavior_result["violations"]
                all_problems["summary"]["blocking_issues"] += behavior_result["violations_detected"]

        except Exception as e:
            self.logger.warning(f"AI行为检查失败: {e}")

        # 2. 收集文化标准问题
        try:
            culture_enforcer = CultureEnforcer(str(self.project_path))
            culture_result = culture_enforcer.enforce_all()

            violations = culture_result.get("violations", [])

            for violation in violations:
                problem_info = {
                    "description": violation.description,
                    "severity": violation.severity,
                    "principle": getattr(violation, "principle", "unknown"),
                    "file_path": getattr(violation, "file_path", None),
                    "line_number": getattr(violation, "line_number", None),
                    "suggestion": getattr(violation, "suggestion", None),
                    "category": getattr(violation, "category", "general"),
                }

                # 添加到相应分类
                if violation.severity == "error":
                    all_problems["categories"]["culture_errors"].append(problem_info)
                    all_problems["summary"]["total_errors"] += 1
                    all_problems["summary"]["blocking_issues"] += 1
                else:
                    all_problems["categories"]["culture_warnings"].append(problem_info)
                    all_problems["summary"]["total_warnings"] += 1

                # 记录受影响的文件
                if problem_info["file_path"]:
                    all_problems["files_affected"].add(problem_info["file_path"])

                # 按类别分类
                category = problem_info["category"]
                if "security" in category.lower() or "privacy" in category.lower():
                    all_problems["categories"]["security_issues"].append(problem_info)
                elif "performance" in category.lower():
                    all_problems["categories"]["performance_issues"].append(problem_info)
                elif "accessibility" in category.lower():
                    all_problems["categories"]["accessibility_issues"].append(problem_info)

        except Exception as e:
            self.logger.error(f"文化检查失败: {e}")

        # 3. 计算总数
        all_problems["summary"]["total_issues"] = (
            all_problems["summary"]["total_errors"] + all_problems["summary"]["total_warnings"]
        )

        # 4. 生成修复优先级
        all_problems["fix_priority"] = self._generate_fix_priority(all_problems)

        # 5. 转换set为list以便JSON序列化
        all_problems["files_affected"] = list(all_problems["files_affected"])

        self.logger.info(f"问题收集完成: {all_problems['summary']['total_issues']} 个问题")

        return all_problems

    def _generate_fix_priority(self, problems: dict[str, Any]) -> list[dict[str, Any]]:
        """生成修复优先级列表"""
        priority_list = []

        # 1. AI行为违规 - 最高优先级
        if problems["categories"]["ai_behavior_violations"]:
            priority_list.append(
                {
                    "priority": 1,
                    "category": "AI行为违规",
                    "count": len(problems["categories"]["ai_behavior_violations"]),
                    "description": "必须立即修复的AI行为违规",
                    "blocking": True,
                }
            )

        # 2. 安全问题 - 高优先级
        if problems["categories"]["security_issues"]:
            priority_list.append(
                {
                    "priority": 2,
                    "category": "安全问题",
                    "count": len(problems["categories"]["security_issues"]),
                    "description": "数据隐私和安全相关问题",
                    "blocking": True,
                }
            )

        # 3. 文化标准错误 - 高优先级
        if problems["categories"]["culture_errors"]:
            priority_list.append(
                {
                    "priority": 3,
                    "category": "文化标准错误",
                    "count": len(problems["categories"]["culture_errors"]),
                    "description": "违反开发文化标准的错误",
                    "blocking": True,
                }
            )

        # 4. 性能问题 - 中优先级
        if problems["categories"]["performance_issues"]:
            priority_list.append(
                {
                    "priority": 4,
                    "category": "性能问题",
                    "count": len(problems["categories"]["performance_issues"]),
                    "description": "影响系统性能的问题",
                    "blocking": False,
                }
            )

        # 5. 可访问性问题 - 中优先级
        if problems["categories"]["accessibility_issues"]:
            priority_list.append(
                {
                    "priority": 5,
                    "category": "可访问性问题",
                    "count": len(problems["categories"]["accessibility_issues"]),
                    "description": "影响用户可访问性的问题",
                    "blocking": False,
                }
            )

        # 6. 其他警告 - 低优先级
        other_warnings = len(problems["categories"]["culture_warnings"]) - (
            len(problems["categories"]["security_issues"])
            + len(problems["categories"]["performance_issues"])
            + len(problems["categories"]["accessibility_issues"])
        )

        if other_warnings > 0:
            priority_list.append(
                {
                    "priority": 6,
                    "category": "其他警告",
                    "count": other_warnings,
                    "description": "其他需要关注的警告",
                    "blocking": False,
                }
            )

        return priority_list

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import time

        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def display_problem_summary(self, problems: dict[str, Any]) -> None:
        """显示问题汇总"""
        print("\n" + "=" * 80)
        print("🔍 项目问题完整汇总报告")
        print("=" * 80)

        summary = problems["summary"]
        print("📊 问题统计:")
        print(f"   • 总问题数: {summary['total_issues']} 个")
        print(f"   • 错误: {summary['total_errors']} 个")
        print(f"   • 警告: {summary['total_warnings']} 个")
        print(f"   • 阻塞性问题: {summary['blocking_issues']} 个")
        print(f"   • 受影响文件: {len(problems['files_affected'])} 个")

        print("\n🎯 修复优先级:")
        for priority in problems["fix_priority"]:
            blocking_text = "🚫 阻塞" if priority["blocking"] else "⚠️  警告"
            print(
                f"   {priority['priority']}. {priority['category']} ({priority['count']} 个) - {blocking_text}"
            )
            print(f"      {priority['description']}")

        # 显示详细问题
        categories = problems["categories"]

        if categories["ai_behavior_violations"]:
            print(f"\n🤖 AI行为违规 ({len(categories['ai_behavior_violations'])} 个):")
            for i, violation in enumerate(categories["ai_behavior_violations"], 1):
                print(f"   {i}. {violation}")

        if categories["culture_errors"]:
            print(f"\n❌ 文化标准错误 ({len(categories['culture_errors'])} 个):")
            for i, error in enumerate(categories["culture_errors"], 1):
                print(f"   {i}. {error['description']}")
                if error.get("file_path"):
                    print(f"      📁 {error['file_path']}")
                if error.get("suggestion"):
                    print(f"      💡 {error['suggestion']}")
                print()

        if categories["security_issues"]:
            print(f"\n🔒 安全问题 ({len(categories['security_issues'])} 个):")
            for i, issue in enumerate(categories["security_issues"], 1):
                print(f"   {i}. {issue['description']}")
                if issue.get("file_path"):
                    print(f"      📁 {issue['file_path']}")
                if issue.get("suggestion"):
                    print(f"      💡 {issue['suggestion']}")
                print()

        if categories["culture_warnings"]:
            other_warnings = [
                w
                for w in categories["culture_warnings"]
                if w not in categories["security_issues"]
                and w not in categories["performance_issues"]
                and w not in categories["accessibility_issues"]
            ]

            if other_warnings:
                print(f"\n⚠️  其他警告 ({len(other_warnings)} 个):")
                for i, warning in enumerate(other_warnings[:5], 1):  # 只显示前5个
                    print(f"   {i}. {warning['description']}")
                    if warning.get("file_path"):
                        print(f"      📁 {warning['file_path']}")

                if len(other_warnings) > 5:
                    print(f"   ... 还有 {len(other_warnings) - 5} 个警告")

        print("\n🎯 修复建议:")
        print(f"   1. 优先修复 {summary['blocking_issues']} 个阻塞性问题")
        print("   2. 按优先级顺序逐一解决问题")
        print("   3. 每个问题都有具体的修复建议")
        print("   4. 修复完成后重新运行检查验证")
        print("   5. 所有错误解决后即可成功推送")

        print("=" * 80)

    def save_problem_report(self, problems: dict[str, Any], output_file: str = None) -> str:
        """保存问题报告到文件"""
        if output_file is None:
            output_file = (
                f"problem_report_{problems['timestamp'].replace(' ', '_').replace(':', '-')}.json"
            )

        output_path = self.project_path / output_file

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(problems, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"问题报告已保存到: {output_path}")
        return str(output_path)


def main():
    """主函数 - 命令行工具"""
    aggregator = ProblemAggregator()

    print("🔍 正在收集项目中的所有问题...")
    problems = aggregator.collect_all_problems()

    # 显示汇总
    aggregator.display_problem_summary(problems)

    # 保存报告
    report_file = aggregator.save_problem_report(problems)
    print(f"\n📄 详细报告已保存到: {report_file}")

    # 如果有阻塞性问题，返回错误码
    if problems["summary"]["blocking_issues"] > 0:
        print(
            f"\n🛑 发现 {problems['summary']['blocking_issues']} 个阻塞性问题，需要修复后才能继续"
        )
        sys.exit(1)
    else:
        print("\n✅ 没有阻塞性问题，可以继续操作")
        sys.exit(0)


if __name__ == "__main__":
    main()
