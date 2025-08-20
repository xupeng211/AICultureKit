#!/usr/bin/env python3
"""
深度代码质量分析工具
"""

import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class CodeIssue:
    """代码问题"""

    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str


class DeepCodeAnalyzer:
    """深度代码分析器"""

    def __init__(self):
        """__init__函数"""
        self.issues = []
        self.metrics = defaultdict(int)

    def analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """分析整个项目"""
        print("🔍 开始深度代码质量分析...")

        python_files = list(project_path.rglob("*.py"))
        print(f"📁 找到 {len(python_files)} 个Python文件")

        for file_path in python_files:
            if self._should_analyze_file(file_path):
                self._analyze_file(file_path)

        return self._generate_report()

    def _should_analyze_file(self, file_path: Path) -> bool:
        """判断是否应该分析该文件"""
        # 跳过虚拟环境和缓存目录
        skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
        return not any(part in skip_dirs for part in file_path.parts)

    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree, content)
            except SyntaxError as e:
                self.issues.append(
                    CodeIssue(
                        file_path=str(file_path),
                        line_number=e.lineno or 0,
                        issue_type="syntax_error",
                        severity="high",
                        description=f"语法错误: {e.msg}",
                        suggestion="修复语法错误",
                    )
                )

            # 分析文本内容
            self._analyze_text_content(file_path, content)

        except Exception as e:
            print(f"❌ 分析 {file_path} 时出错: {e}")

    def _analyze_ast(self, file_path: Path, tree: ast.AST, content: str):
        """分析AST"""
        lines = content.split('\n')

        for node in ast.walk(tree):
            # 检查函数复杂度
            if isinstance(node, ast.FunctionDef):
                self._check_function_complexity(file_path, node, lines)

            # 检查类设计
            elif isinstance(node, ast.ClassDef):
                self._check_class_design(file_path, node, lines)

            # 检查异常处理
            elif isinstance(node, ast.ExceptHandler):
                self._check_exception_handling(file_path, node, lines)

            # 检查魔法数字
            elif isinstance(node, ast.Num):
                self._check_magic_numbers(file_path, node, lines)

    def _analyze_text_content(self, file_path: Path, content: str):
        """分析文本内容"""
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                self.issues.append(
                    CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="line_too_long",
                        severity="medium",
                        description=f"行长度 {len(line)} 超过120字符",
                        suggestion="将长行拆分为多行",
                    )
                )

            # 检查TODO/FIXME注释
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                self.issues.append(
                    CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="todo_comment",
                        severity="low",
                        description="发现TODO/FIXME注释",
                        suggestion="完成待办事项或创建issue跟踪",
                    )
                )

            # 检查硬编码字符串
            if re.search(r'["\'][^"\']{20,}["\']', line):
                if not line.strip().startswith('#'):  # 不是注释
                    self.issues.append(
                        CodeIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="hardcoded_string",
                            severity="medium",
                            description="发现长硬编码字符串",
                            suggestion="考虑使用常量或配置文件",
                        )
                    )

    def _check_function_complexity(
        self, file_path: Path, node: ast.FunctionDef, lines: List[str]
    ):
        """检查函数复杂度"""
        # 计算圈复杂度
        complexity = self._calculate_cyclomatic_complexity(node)

        if complexity > 10:
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="high_complexity",
                    severity="high",
                    description=f"函数 {node.name} 圈复杂度过高: {complexity}",
                    suggestion="将复杂函数拆分为更小的函数",
                )
            )

        # 检查函数长度
        func_lines = (
            node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
        )
        if func_lines > 50:
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="long_function",
                    severity="medium",
                    description=f"函数 {node.name} 过长: {func_lines} 行",
                    suggestion="将长函数拆分为更小的函数",
                )
            )

        # 检查参数数量
        if len(node.args.args) > 5:
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="too_many_parameters",
                    severity="medium",
                    description=f"函数 {node.name} 参数过多: {len(node.args.args)}",
                    suggestion="考虑使用数据类或字典传递参数",
                )
            )

    def _check_class_design(
        self, file_path: Path, node: ast.ClassDef, lines: List[str]
    ):
        """检查类设计"""
        # 计算类的方法数量
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        if len(methods) > 20:
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="too_many_methods",
                    severity="medium",
                    description=f"类 {node.name} 方法过多: {len(methods)}",
                    suggestion="考虑将类拆分或使用组合模式",
                )
            )

        # 检查是否有文档字符串
        if not ast.get_docstring(node):
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="missing_docstring",
                    severity="low",
                    description=f"类 {node.name} 缺少文档字符串",
                    suggestion="添加类的文档字符串",
                )
            )

    def _check_exception_handling(
        self, file_path: Path, node: ast.ExceptHandler, lines: List[str]
    ):
        """检查异常处理"""
        # 检查裸露的except
        if node.type is None:
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="bare_except",
                    severity="high",
                    description="使用了裸露的except子句",
                    suggestion="指定具体的异常类型",
                )
            )

        # 检查空的异常处理
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.issues.append(
                CodeIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    issue_type="empty_except",
                    severity="medium",
                    description="空的异常处理块",
                    suggestion="添加适当的异常处理逻辑或日志记录",
                )
            )

    def _check_magic_numbers(self, file_path: Path, node: ast.Num, lines: List[str]):
        """检查魔法数字"""
        # 跳过常见的数字
        common_numbers = {0, 1, 2, -1, 100, 1000}

        if hasattr(node, 'n') and node.n not in common_numbers:
            if isinstance(node.n, (int, float)) and abs(node.n) > 1:
                self.issues.append(
                    CodeIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        issue_type="magic_number",
                        severity="low",
                        description=f"发现魔法数字: {node.n}",
                        suggestion="使用命名常量替代魔法数字",
                    )
                )

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
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
            'total_issues': len(self.issues),
            'by_severity': dict(by_severity),
            'by_type': dict(by_type),
            'by_file': dict(by_file),
            'summary': {
                'high_severity': len(by_severity['high']),
                'medium_severity': len(by_severity['medium']),
                'low_severity': len(by_severity['low']),
                'files_with_issues': len(by_file),
            },
        }


def main():
    """主函数"""
    analyzer = DeepCodeAnalyzer()
    report = analyzer.analyze_project(Path('.'))

    print("\n📊 深度代码质量分析报告")
    print("=" * 50)

    summary = report['summary']
    print(f"总问题数: {report['total_issues']}")
    print(f"高严重性: {summary['high_severity']} 个")
    print(f"中等严重性: {summary['medium_severity']} 个")
    print(f"低严重性: {summary['low_severity']} 个")
    print(f"有问题的文件: {summary['files_with_issues']} 个")

    print("\n🔍 按问题类型分组:")
    for issue_type, issues in report['by_type'].items():
        print(f"  {issue_type}: {len(issues)} 个")

    print("\n🚨 高严重性问题详情:")
    high_issues = report['by_severity'].get('high', [])
    for i, issue in enumerate(high_issues[:10], 1):
        print(f"  {i}. {issue.file_path}:{issue.line_number}")
        print(f"     {issue.description}")
        print(f"     建议: {issue.suggestion}")
        print()

    if len(high_issues) > 10:
        print(f"  ... 还有 {len(high_issues) - 10} 个高严重性问题")

    return report


if __name__ == "__main__":
    main()
