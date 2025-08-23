#!/usr/bin/env python3
"""
文档质量分析工具
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class DocumentationIssue:
    """文档问题"""

    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str


class DocumentationAnalyzer:
    """文档分析器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.issues = []

    def analyze_documentation(self) -> Dict[str, Any]:
        """分析文档质量"""
        print("📚 开始文档与注释质量分析...")

        # 分析Python文件的文档字符串
        self._analyze_python_docstrings()

        # 分析Markdown文档
        self._analyze_markdown_docs()

        # 分析代码注释质量
        self._analyze_code_comments()

        return self._generate_documentation_report()

    def _analyze_python_docstrings(self):
        """分析Python文档字符串"""
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                self._check_module_docstring(file_path, tree)
                self._check_class_docstrings(file_path, tree)
                self._check_function_docstrings(file_path, tree)

            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_module_docstring(self, file_path: Path, tree: ast.AST):
        """检查模块文档字符串"""
        module_docstring = ast.get_docstring(tree)

        if not module_docstring:
            self.issues.append(
                DocumentationIssue(
                    file_path=str(file_path),
                    line_number=1,
                    issue_type="missing_module_docstring",
                    severity="medium",
                    description="模块缺少文档字符串",
                    suggestion="添加模块级别的文档字符串，说明模块的用途和功能",
                )
            )
        elif len(module_docstring.strip()) < 10:
            self.issues.append(
                DocumentationIssue(
                    file_path=str(file_path),
                    line_number=1,
                    issue_type="short_module_docstring",
                    severity="low",
                    description="模块文档字符串过短",
                    suggestion="扩展模块文档字符串，提供更详细的说明",
                )
            )

    def _check_class_docstrings(self, file_path: Path, tree: ast.AST):
        """检查类文档字符串"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_docstring = ast.get_docstring(node)

                if not class_docstring:
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="missing_class_docstring",
                            severity="medium",
                            description=f"类 {node.name} 缺少文档字符串",
                            suggestion="添加类文档字符串，说明类的用途、属性和方法",
                        )
                    )
                elif len(class_docstring.strip()) < 20:
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="short_class_docstring",
                            severity="low",
                            description=f"类 {node.name} 文档字符串过短",
                            suggestion="扩展类文档字符串，提供更详细的说明",
                        )
                    )

    def _check_function_docstrings(self, file_path: Path, tree: ast.AST):
        """检查函数文档字符串"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 跳过私有方法和特殊方法
                if node.name.startswith("_"):
                    continue

                func_docstring = ast.get_docstring(node)

                if not func_docstring:
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="missing_function_docstring",
                            severity="low",
                            description=f"函数 {node.name} 缺少文档字符串",
                            suggestion="添加函数文档字符串，说明参数、返回值和功能",
                        )
                    )
                elif len(func_docstring.strip()) < 15:
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="short_function_docstring",
                            severity="low",
                            description=f"函数 {node.name} 文档字符串过短",
                            suggestion="扩展函数文档字符串，提供更详细的说明",
                        )
                    )

                # 检查参数文档
                if len(node.args.args) > 2:  # 有多个参数的函数
                    if not self._has_parameter_docs(func_docstring):
                        self.issues.append(
                            DocumentationIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type="missing_parameter_docs",
                                severity="low",
                                description=f"函数 {node.name} 缺少参数文档",
                                suggestion="在文档字符串中添加参数说明",
                            )
                        )

    def _analyze_markdown_docs(self):
        """分析Markdown文档"""
        md_files = list(self.project_path.rglob("*.md"))

        for file_path in md_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                self._check_markdown_structure(file_path, content)
                self._check_markdown_links(file_path, content)

            except UnicodeDecodeError:
                continue

    def _check_markdown_structure(self, file_path: Path, content: str):
        """检查Markdown结构"""
        lines = content.split("\n")

        # 检查是否有标题
        has_title = any(line.startswith("#") for line in lines[:10])
        if not has_title:
            self.issues.append(
                DocumentationIssue(
                    file_path=str(file_path),
                    line_number=1,
                    issue_type="missing_title",
                    severity="medium",
                    description="Markdown文档缺少标题",
                    suggestion="在文档开头添加主标题",
                )
            )

        # 检查文档长度
        if len(content.strip()) < 100:
            self.issues.append(
                DocumentationIssue(
                    file_path=str(file_path),
                    line_number=1,
                    issue_type="short_document",
                    severity="low",
                    description="文档内容过短",
                    suggestion="扩展文档内容，提供更详细的信息",
                )
            )

    def _check_markdown_links(self, file_path: Path, content: str):
        """检查Markdown链接"""
        # 查找所有链接
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(link_pattern, content)

        for i, (text, url) in enumerate(links, 1):
            # 检查相对路径链接是否存在
            if not url.startswith(("http://", "https://", "mailto:")):
                link_path = file_path.parent / url
                if not link_path.exists():
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="broken_link",
                            severity="medium",
                            description=f"链接指向不存在的文件: {url}",
                            suggestion="检查链接路径是否正确或创建对应的文件",
                        )
                    )

    def _analyze_code_comments(self):
        """分析代码注释质量"""
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                self._check_comment_quality(file_path, lines)

            except UnicodeDecodeError:
                continue

    def _check_comment_quality(self, file_path: Path, lines: List[str]):
        """检查注释质量"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 检查TODO注释
            if re.search(r"#\s*TODO", stripped, re.IGNORECASE):
                if len(stripped) < 20:  # TODO注释过短
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="short_todo_comment",
                            severity="low",
                            description="TODO注释过短，缺少详细说明",
                            suggestion="扩展TODO注释，说明具体需要做什么",
                        )
                    )

            # 检查单行注释
            if stripped.startswith("#") and not stripped.startswith("##"):
                comment_text = stripped[1:].strip()
                if len(comment_text) < 5:
                    self.issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="short_comment",
                            severity="low",
                            description="注释过短，缺少有用信息",
                            suggestion="提供更详细的注释说明",
                        )
                    )

    def _has_parameter_docs(self, docstring: str) -> bool:
        """检查是否有参数文档"""
        if not docstring:
            return False

        # 简单检查是否包含参数相关的关键词
        param_keywords = [
            "param",
            "parameter",
            "arg",
            "argument",
            "Args:",
            "Parameters:",
        ]
        return any(keyword in docstring for keyword in param_keywords)

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_dirs = {"venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        return any(part in skip_dirs for part in file_path.parts)

    def _generate_documentation_report(self) -> Dict[str, Any]:
        """生成文档分析报告"""
        # 按严重程度分组
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        # 按类型分组
        by_type = defaultdict(list)
        for issue in self.issues:
            by_type[issue.issue_type].append(issue)

        # 按文件分组
        by_file = defaultdict(list)
        for issue in self.issues:
            by_file[issue.file_path].append(issue)

        return {
            "total_issues": len(self.issues),
            "by_severity": dict(by_severity),
            "by_type": dict(by_type),
            "by_file": dict(by_file),
            "summary": {
                "high_severity": len(by_severity["high"]),
                "medium_severity": len(by_severity["medium"]),
                "low_severity": len(by_severity["low"]),
                "files_with_issues": len(by_file),
            },
        }


def main():
    """main函数"""
    analyzer = DocumentationAnalyzer(Path("."))
    report = analyzer.analyze_documentation()

    print("\n📚 文档与注释质量分析报告")
    print("=" * 50)

    summary = report["summary"]
    print(f"文档问题总数: {report['total_issues']}")
    print(f"高严重性: {summary['high_severity']} 个")
    print(f"中等严重性: {summary['medium_severity']} 个")
    print(f"低严重性: {summary['low_severity']} 个")
    print(f"有问题的文件: {summary['files_with_issues']} 个")

    print("\n🔍 按问题类型分组:")
    for issue_type, issues in report["by_type"].items():
        print(f"  {issue_type}: {len(issues)} 个")

    print("\n🚨 中等严重性问题详情:")
    medium_issues = report["by_severity"].get("medium", [])
    for i, issue in enumerate(medium_issues[:5], 1):
        print(f"  {i}. {issue.file_path}:{issue.line_number}")
        print(f"     {issue.description}")
        print(f"     建议: {issue.suggestion}")
        print()

    if len(medium_issues) > 5:
        print(f"  ... 还有 {len(medium_issues) - 5} 个中等严重性问题")

    return report


if __name__ == "__main__":
    main()
