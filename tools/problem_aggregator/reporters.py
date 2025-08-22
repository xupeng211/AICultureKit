"""
Problem reporters for generating human-readable reports
"""

from datetime import datetime
from typing import Any, Dict, List


class MarkdownReporter:
    """Markdown格式报告生成器"""

    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成Markdown报告"""

        lines = []

        # 标题和摘要
        lines.append("# 🔍 AICultureKit 问题聚合报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        metadata = result.get("metadata", {})
        if metadata:
            lines.append(f"**检查基准**: {metadata.get('base', 'HEAD')}")
            lines.append(f"**检查文件**: {metadata.get('files_checked', 'all')}")
            lines.append(f"**严格模式**: {'是' if metadata.get('strict_mode', False) else '否'}")

        lines.append("")

        # 问题摘要
        summary = result.get("summary", {})
        lines.append("## 📊 问题摘要")
        lines.append("")
        lines.append(f"- **总计**: {summary.get('total', 0)} 个问题")
        lines.append(f"- **阻塞性**: {summary.get('blocking', 0)} 个")

        by_severity = summary.get("by_severity", {})
        lines.append(f"- **错误**: {by_severity.get('error', 0)} 个")
        lines.append(f"- **警告**: {by_severity.get('warning', 0)} 个")
        lines.append(f"- **信息**: {by_severity.get('info', 0)} 个")
        lines.append("")

        # 优先级排序的问题分类
        categories = result.get("categories", {})

        # 1. 安全问题 (最高优先级)
        if categories.get("security"):
            lines.append("## 🔒 安全问题 (最高优先级)")
            lines.append("")
            lines.extend(self._format_problems(categories["security"]))
            lines.append("")

        # 2. 行为违规
        if categories.get("behavior_violations"):
            lines.append("## 🚫 行为违规")
            lines.append("")
            lines.extend(self._format_problems(categories["behavior_violations"]))
            lines.append("")

        # 3. 构建阻塞
        if categories.get("build_blocking"):
            lines.append("## 🛑 构建阻塞")
            lines.append("")
            lines.extend(self._format_problems(categories["build_blocking"]))
            lines.append("")

        # 4. 质量问题
        if categories.get("quality"):
            lines.append("## ⚠️ 质量问题")
            lines.append("")
            lines.extend(self._format_problems(categories["quality"]))
            lines.append("")

        # 5. 风格问题
        if categories.get("style"):
            lines.append("## 🎨 风格问题")
            lines.append("")
            lines.extend(self._format_problems(categories["style"]))
            lines.append("")

        # 6. 系统问题
        if categories.get("system"):
            lines.append("## ⚙️ 系统问题")
            lines.append("")
            lines.extend(self._format_problems(categories["system"]))
            lines.append("")

        # 修复建议汇总
        lines.append("## 🎯 修复建议")
        lines.append("")

        blocking_count = summary.get("blocking", 0)
        if blocking_count > 0:
            lines.append(f"### ⚡ 立即处理 ({blocking_count} 个阻塞性问题)")
            lines.append("")
            blocking_problems = [p for p in result.get("problems", []) if p.get("blocking", False)]
            for i, problem in enumerate(blocking_problems, 1):
                lines.append(
                    f"{i}. **{problem.get('file', 'N/A')}:{problem.get('line', 0)}** - {problem.get('message', '')}"
                )
                if problem.get("fix_suggestion"):
                    lines.append(f"   💡 {problem.get('fix_suggestion')}")
            lines.append("")

        # 按工具统计
        lines.append("### 📈 按工具统计")
        lines.append("")
        tool_stats = self._get_tool_statistics(result.get("problems", []))
        for tool, stats in tool_stats.items():
            lines.append(f"- **{tool}**: {stats['total']} 个问题 ({stats['blocking']} 个阻塞)")
        lines.append("")

        # 热点文件
        file_stats = self._get_file_statistics(result.get("problems", []))
        if file_stats:
            lines.append("### 🔥 问题热点文件")
            lines.append("")
            for file_path, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]:
                lines.append(f"- **{file_path}**: {count} 个问题")
            lines.append("")

        # 下一步行动
        lines.append("## 🚀 建议的下一步行动")
        lines.append("")

        if blocking_count > 0:
            lines.append("1. **立即修复阻塞性问题** - 这些问题会阻止代码提交")

        error_count = by_severity.get("error", 0)
        if error_count > 0:
            lines.append(f"2. **修复 {error_count} 个错误** - 这些是严重问题")

        warning_count = by_severity.get("warning", 0)
        if warning_count > 0:
            lines.append(f"3. **处理 {warning_count} 个警告** - 提升代码质量")

        lines.append("4. **运行自动修复工具** - 使用 `black`, `isort`, `ruff --fix` 等")
        lines.append("5. **重新运行检查** - 确认问题已解决")
        lines.append("")

        # 工具命令
        lines.append("## 🛠️ 有用的命令")
        lines.append("")
        lines.append("```bash")
        lines.append("# 自动修复代码格式")
        lines.append("python -m black .")
        lines.append("python -m isort .")
        lines.append("python -m ruff check --fix .")
        lines.append("")
        lines.append("# 运行测试和覆盖率")
        lines.append("python -m pytest --cov=aiculture --cov-report=term-missing")
        lines.append("")
        lines.append("# 重新运行问题聚合")
        lines.append(
            "python -m tools.problem_aggregator.aggregator --md artifacts/problems_report.md"
        )
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _format_problems(self, problems: List[Dict[str, Any]]) -> List[str]:
        """格式化问题列表"""
        lines = []

        for i, problem in enumerate(problems, 1):
            severity = problem.get("severity", "info")
            severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
            blocking_icon = " 🚫" if problem.get("blocking", False) else ""

            # 问题标题
            file_info = ""
            if problem.get("file"):
                file_info = f"**{problem['file']}"
                if problem.get("line"):
                    file_info += f":{problem['line']}"
                file_info += "**"

            tool = problem.get("tool", "unknown")
            message = problem.get("message", "未知问题")

            lines.append(f"{i}. {severity_icon}{blocking_icon} [{tool}] {file_info} {message}")

            # 修复建议
            if problem.get("fix_suggestion"):
                lines.append(f"   💡 **修复建议**: {problem['fix_suggestion']}")

            # 额外信息
            if problem.get("code"):
                lines.append(f"   🏷️ **错误码**: `{problem['code']}`")

            if problem.get("metadata"):
                metadata = problem["metadata"]
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        lines.append(f"   📊 **{key}**: {value}")

            lines.append("")

        return lines

    def _get_tool_statistics(self, problems: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """获取按工具的统计信息"""
        stats = {}

        for problem in problems:
            tool = problem.get("tool", "unknown")
            if tool not in stats:
                stats[tool] = {"total": 0, "blocking": 0}

            stats[tool]["total"] += 1
            if problem.get("blocking", False):
                stats[tool]["blocking"] += 1

        return stats

    def _get_file_statistics(self, problems: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取按文件的统计信息"""
        stats = {}

        for problem in problems:
            file_path = problem.get("file")
            if file_path:
                stats[file_path] = stats.get(file_path, 0) + 1

        return stats


class DashboardReporter:
    """看板式报告生成器"""

    def generate_dashboard(self, result: Dict[str, Any]) -> str:
        """生成汇总看板"""

        lines = []

        # ASCII艺术标题
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append("║                    🔍 AICultureKit 问题看板                    ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        lines.append("")

        summary = result.get("summary", {})

        # 总体状态
        total = summary.get("total", 0)
        blocking = summary.get("blocking", 0)

        if blocking > 0:
            status = "🔴 阻塞"
            status_msg = f"发现 {blocking} 个阻塞性问题"
        elif summary.get("by_severity", {}).get("error", 0) > 0:
            status = "🟡 警告"
            status_msg = f"发现 {summary['by_severity']['error']} 个错误"
        elif total > 0:
            status = "🟢 通过"
            status_msg = f"发现 {total} 个非阻塞问题"
        else:
            status = "✅ 完美"
            status_msg = "未发现任何问题"

        lines.append(f"状态: {status}")
        lines.append(f"描述: {status_msg}")
        lines.append("")

        # 问题分布
        lines.append("问题分布:")
        categories = result.get("categories", {})
        for category, problems in categories.items():
            if problems:
                count = len(problems)
                blocking_count = len([p for p in problems if p.get("blocking", False)])
                blocking_text = f" ({blocking_count} 阻塞)" if blocking_count > 0 else ""

                category_names = {
                    "security": "🔒 安全",
                    "behavior_violations": "🚫 行为违规",
                    "build_blocking": "🛑 构建阻塞",
                    "quality": "⚠️ 质量",
                    "style": "🎨 风格",
                    "system": "⚙️ 系统",
                }

                category_name = category_names.get(category, category)
                lines.append(f"  {category_name}: {count}{blocking_text}")

        lines.append("")

        # 风险热力图（简化版）
        file_stats = self._get_file_risk_heatmap(result.get("problems", []))
        if file_stats:
            lines.append("🔥 风险热点:")
            for file_path, risk_score in sorted(
                file_stats.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                risk_level = "🔴" if risk_score >= 10 else "🟡" if risk_score >= 5 else "🟢"
                lines.append(f"  {risk_level} {file_path} (风险: {risk_score})")

        lines.append("")

        return "\n".join(lines)

    def _get_file_risk_heatmap(self, problems: List[Dict[str, Any]]) -> Dict[str, int]:
        """计算文件风险热力图"""
        risk_scores = {}

        for problem in problems:
            file_path = problem.get("file")
            if not file_path:
                continue

            # 计算风险分数
            risk_score = 1  # 基础分数

            severity = problem.get("severity", "info")
            if severity == "error":
                risk_score += 5
            elif severity == "warning":
                risk_score += 2

            if problem.get("blocking", False):
                risk_score += 10

            problem_type = problem.get("type", "")
            if problem_type == "security":
                risk_score += 8
            elif problem_type in ["test_failure", "test_collection"]:
                risk_score += 6

            risk_scores[file_path] = risk_scores.get(file_path, 0) + risk_score

        return risk_scores
