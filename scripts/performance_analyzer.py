#!/usr/bin/env python3
"""
性能分析器
分析代码中可能的性能问题并提供优化建议
"""

import ast
from pathlib import Path
from typing import Any


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, project_path: Path = None):
        """__init__函数"""
        self.project_path = project_path or Path.cwd()
        self.issues = []

    def analyze_file(self, file_path: Path) -> list[dict[str, Any]]:
        """分析单个文件的性能问题"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            lines = content.split("\n")

            file_issues = []

            # 分析各种性能问题
            file_issues.extend(self.check_large_functions(tree, file_path))
            file_issues.extend(self.check_nested_loops(tree, file_path))
            file_issues.extend(self.check_string_concatenation(tree, file_path, lines))
            file_issues.extend(self.check_inefficient_patterns(tree, file_path, lines))
            file_issues.extend(self.check_file_size(file_path, lines))

            return file_issues

        except Exception as e:
            return [
                {
                    "file": str(file_path),
                    "line": 0,
                    "issue": "parse_error",
                    "description": f"无法解析文件: {e}",
                    "suggestion": "检查语法错误",
                    "severity": "error",
                }
            ]

    def check_large_functions(self, tree: ast.AST, file_path: Path) -> list[dict[str, Any]]:
        """检查过大的函数"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数行数
                if hasattr(node, "end_lineno") and node.end_lineno:
                    func_lines = node.end_lineno - node.lineno + 1

                    if func_lines > 50:
                        issues.append(
                            {
                                "file": str(file_path),
                                "line": node.lineno,
                                "issue": "large_function",
                                "description": f"函数 '{node.name}' 过大 ({func_lines} 行)",
                                "suggestion": "考虑将大函数拆分为多个小函数",
                                "severity": "warning" if func_lines < 100 else "error",
                            }
                        )

        return issues

    def check_nested_loops(self, tree: ast.AST, file_path: Path) -> list[dict[str, Any]]:
        """检查嵌套循环"""
        issues = []

        def count_nested_loops(node, depth=0):
            """count_nested_loops函数"""
            if isinstance(node, (ast.For, ast.While)):
                depth += 1
                if depth > 2:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": node.lineno,
                            "issue": "deep_nested_loops",
                            "description": f"深度嵌套循环 (深度: {depth})",
                            "suggestion": "考虑使用函数或生成器来减少嵌套",
                            "severity": "warning",
                        }
                    )

            for child in ast.iter_child_nodes(node):
                count_nested_loops(child, depth)

        count_nested_loops(tree)
        return issues

    def check_string_concatenation(
        self, tree: ast.AST, file_path: Path, lines: list[str]
    ) -> list[dict[str, Any]]:
        """检查字符串拼接性能问题"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                # 检查是否是字符串拼接
                if (
                    isinstance(node.left, ast.Str)
                    or isinstance(node.right, ast.Str)
                    or (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str))
                    or (isinstance(node.right, ast.Constant) and isinstance(node.right.value, str))
                ):
                    # 检查是否在循环中
                    parent = node
                    in_loop = False
                    while hasattr(parent, "parent"):
                        parent = parent.parent
                        if isinstance(parent, (ast.For, ast.While)):
                            in_loop = True
                            break

                    if in_loop:
                        issues.append(
                            {
                                "file": str(file_path),
                                "line": node.lineno,
                                "issue": "string_concat_in_loop",
                                "description": "循环中的字符串拼接可能影响性能",
                                "suggestion": "考虑使用列表收集字符串，最后用join()连接",
                                "severity": "warning",
                            }
                        )

        return issues

    def check_inefficient_patterns(
        self, tree: ast.AST, file_path: Path, lines: list[str]
    ) -> list[dict[str, Any]]:
        """检查低效的代码模式"""
        issues = []

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 检查低效的列表操作
            if "for" in line_stripped and "in range(len(" in line_stripped:
                issues.append(
                    {
                        "file": str(file_path),
                        "line": i,
                        "issue": "inefficient_iteration",
                        "description": "使用range(len())进行迭代",
                        "suggestion": "考虑直接迭代列表或使用enumerate()",
                        "severity": "info",
                    }
                )

            # 检查重复的字典查找
            if line_stripped.count("[") > 2 and "dict" in line_stripped.lower():
                issues.append(
                    {
                        "file": str(file_path),
                        "line": i,
                        "issue": "repeated_dict_lookup",
                        "description": "可能存在重复的字典查找",
                        "suggestion": "考虑将查找结果缓存到变量中",
                        "severity": "info",
                    }
                )

        return issues

    def check_file_size(self, file_path: Path, lines: list[str]) -> list[dict[str, Any]]:
        """检查文件大小"""
        issues = []
        line_count = len(lines)

        if line_count > 500:
            issues.append(
                {
                    "file": str(file_path),
                    "line": 0,
                    "issue": "large_file",
                    "description": f"文件过大 ({line_count} 行)",
                    "suggestion": "考虑将大文件拆分为多个模块",
                    "severity": "warning" if line_count < 1000 else "error",
                }
            )

        return issues

    def analyze_all_files(self) -> dict[str, Any]:
        """分析所有Python文件"""
        all_issues = []
        stats = {"files_analyzed": 0, "issues_found": 0}

        for py_file in self.project_path.rglob("*.py"):
            # 跳过虚拟环境和隐藏目录
            if any(
                part.startswith(".") or part in ["venv", "__pycache__", "build", "dist"]
                for part in py_file.parts
            ):
                continue

            # 跳过模板文件
            if "{{" in str(py_file) or "}}" in str(py_file):
                continue

            stats["files_analyzed"] += 1
            file_issues = self.analyze_file(py_file)
            all_issues.extend(file_issues)

            if file_issues:
                print(f"📁 {py_file}: 发现 {len(file_issues)} 个性能问题")

        stats["issues_found"] = len(all_issues)

        # 按严重程度分组
        by_severity = {"error": [], "warning": [], "info": []}
        for issue in all_issues:
            by_severity[issue["severity"]].append(issue)

        return {"stats": stats, "issues": all_issues, "by_severity": by_severity}

    def generate_report(self, analysis_result: dict[str, Any]) -> str:
        """生成性能分析报告"""
        stats = analysis_result["stats"]
        by_severity = analysis_result["by_severity"]

        report = f"""
🚀 AICultureKit 性能分析报告
{'='*50}

📊 分析统计:
  - 分析文件数: {stats['files_analyzed']}
  - 发现问题数: {stats['issues_found']}
  - 错误: {len(by_severity['error'])}
  - 警告: {len(by_severity['warning'])}
  - 信息: {len(by_severity['info'])}

"""

        # 按严重程度显示问题
        for severity in ["error", "warning", "info"]:
            issues = by_severity[severity]
            if not issues:
                continue

            emoji = {"error": "🔴", "warning": "🟡", "info": "🔵"}[severity]
            report += f"\n{emoji} {severity.upper()} ({len(issues)}个):\n"

            # 按问题类型分组
            by_type = {}
            for issue in issues:
                issue_type = issue["issue"]
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(issue)

            for issue_type, type_issues in by_type.items():
                report += f"\n  📋 {issue_type} ({len(type_issues)}个):\n"
                for issue in type_issues[:3]:  # 只显示前3个
                    report += f"    - {issue['file']}:{issue['line']} - {issue['description']}\n"
                    report += f"      💡 {issue['suggestion']}\n"

                if len(type_issues) > 3:
                    report += f"    ... 还有 {len(type_issues) - 3} 个类似问题\n"

        # 优化建议
        report += """

💡 优化建议:
  1. 优先修复错误级别的问题
  2. 将大文件拆分为多个模块
  3. 重构过大的函数
  4. 优化循环中的字符串操作
  5. 减少深度嵌套的循环

📈 预期收益:
  - 提高代码可维护性
  - 减少内存使用
  - 提升运行性能
  - 改善代码可读性
"""

        return report


def main() -> None:
    """主函数"""
    analyzer = PerformanceAnalyzer()

    print("🚀 开始性能分析...")
    result = analyzer.analyze_all_files()

    print("\n" + "=" * 50)
    report = analyzer.generate_report(result)
    print(report)

    # 保存报告到文件
    report_file = Path("performance_analysis_report.md")
    report_file.write_text(report, encoding="utf-8")
    print(f"📄 详细报告已保存到: {report_file}")


if __name__ == "__main__":
    main()
