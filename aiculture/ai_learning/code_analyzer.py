"""
AI学习系统 - 代码分析器

负责分析项目代码，提取各种模式和特征。
"""

import ast
from collections import Counter
from pathlib import Path
from typing import Any

from .pattern_types import (
    DocumentationPatternAnalyzer,
    NamingPatternAnalyzer,
    StructurePatternAnalyzer,
    StylePatternAnalyzer,
)


class CodeAnalyzer:
    """代码分析器"""

    def __init__(self, project_path: Path):
        """初始化代码分析器"""
        self.project_path = project_path
        self.naming_analyzer = NamingPatternAnalyzer()
        self.structure_analyzer = StructurePatternAnalyzer()
        self.style_analyzer = StylePatternAnalyzer()
        self.doc_analyzer = DocumentationPatternAnalyzer()

        # 需要跳过的目录
        self.skip_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".mypy_cache",
            ".tox",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
        }

    def analyze_project(self) -> dict[str, Any]:
        """分析整个项目"""
        analysis_result = {
            "structure": self._analyze_structure(),
            "naming": self._analyze_naming(),
            "style": self._analyze_style(),
            "documentation": self._analyze_documentation(),
            "complexity": self._analyze_complexity(),
            "imports": self._analyze_imports(),
            "testing": self._analyze_testing(),
        }

        return analysis_result

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        # 跳过隐藏文件
        if file_path.name.startswith("."):
            return True

        # 跳过特定目录中的文件
        for part in file_path.parts:
            if part in self.skip_dirs:
                return True

        return False

    def _get_python_files(self) -> list[Path]:
        """获取所有Python文件"""
        python_files = []

        for file_path in self.project_path.rglob("*.py"):
            if not self._should_skip_file(file_path):
                python_files.append(file_path)

        return python_files

    def _analyze_structure(self) -> dict[str, Any]:
        """分析项目结构"""
        structure_data = {
            "directories": [],
            "file_extensions": Counter(),
            "total_files": 0,
            "python_files": 0,
        }

        # 分析目录结构
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                structure_data["directories"].append(item.name)

        # 分析文件类型
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                structure_data["total_files"] += 1

                if file_path.suffix:
                    structure_data["file_extensions"][file_path.suffix] += 1

                if file_path.suffix == ".py":
                    structure_data["python_files"] += 1

        return structure_data

    def _analyze_naming(self) -> dict[str, Any]:
        """分析命名模式"""
        naming_data = {
            "function_names": [],
            "class_names": [],
            "variable_names": [],
            "module_names": [],
        }

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # 提取函数名
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        naming_data["function_names"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        naming_data["class_names"].append(node.name)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                naming_data["variable_names"].append(target.id)

                # 模块名
                module_name = file_path.stem
                if module_name != "__init__":
                    naming_data["module_names"].append(module_name)

            except (SyntaxError, UnicodeDecodeError):
                continue

        return naming_data

    def _analyze_style(self) -> dict[str, Any]:
        """分析代码风格"""
        style_data = {
            "quote_usage": {"single": 0, "double": 0},
            "indentation": {"spaces": 0, "tabs": 0},
            "line_length": [],
            "blank_lines": 0,
        }

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                for line in lines:
                    # 分析引号使用
                    single_quotes = line.count("'") - line.count("\\'")
                    double_quotes = line.count('"') - line.count('\\"')

                    style_data["quote_usage"]["single"] += single_quotes
                    style_data["quote_usage"]["double"] += double_quotes

                    # 分析缩进
                    if line.strip():  # 非空行
                        leading_spaces = len(line) - len(line.lstrip(" "))
                        leading_tabs = len(line) - len(line.lstrip("\t"))

                        if leading_spaces > 0:
                            style_data["indentation"]["spaces"] += 1
                        if leading_tabs > 0:
                            style_data["indentation"]["tabs"] += 1

                        # 行长度
                        style_data["line_length"].append(len(line.rstrip()))
                    else:
                        style_data["blank_lines"] += 1

            except UnicodeDecodeError:
                continue

        return style_data

    def _analyze_documentation(self) -> dict[str, Any]:
        """分析文档模式"""
        doc_data = {
            "docstring_style": Counter(),
            "total_functions": 0,
            "documented_functions": 0,
            "total_classes": 0,
            "documented_classes": 0,
            "coverage": 0.0,
        }

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        doc_data["total_functions"] += 1

                        if ast.get_docstring(node):
                            doc_data["documented_functions"] += 1

                            # 分析文档字符串风格
                            docstring = ast.get_docstring(node)
                            if docstring:
                                if docstring.startswith('"""') or '"""' in docstring:
                                    doc_data["docstring_style"]["triple_double"] += 1
                                elif docstring.startswith("'''") or "'''" in docstring:
                                    doc_data["docstring_style"]["triple_single"] += 1

                    elif isinstance(node, ast.ClassDef):
                        doc_data["total_classes"] += 1

                        if ast.get_docstring(node):
                            doc_data["documented_classes"] += 1

            except (SyntaxError, UnicodeDecodeError):
                continue

        # 计算文档覆盖率
        total_items = doc_data["total_functions"] + doc_data["total_classes"]
        documented_items = doc_data["documented_functions"] + doc_data["documented_classes"]

        if total_items > 0:
            doc_data["coverage"] = documented_items / total_items

        return doc_data

    def _analyze_complexity(self) -> dict[str, Any]:
        """分析代码复杂度"""
        complexity_data = {
            "function_complexities": [],
            "avg_complexity": 0.0,
            "max_complexity": 0,
            "high_complexity_functions": [],
        }

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_cyclomatic_complexity(node)
                        complexity_data["function_complexities"].append(complexity)

                        if complexity > 10:  # 高复杂度阈值
                            complexity_data["high_complexity_functions"].append(
                                {
                                    "name": node.name,
                                    "complexity": complexity,
                                    "file": str(file_path),
                                }
                            )

            except (SyntaxError, UnicodeDecodeError):
                continue

        # 计算统计信息
        if complexity_data["function_complexities"]:
            complexity_data["avg_complexity"] = sum(complexity_data["function_complexities"]) / len(
                complexity_data["function_complexities"]
            )
            complexity_data["max_complexity"] = max(complexity_data["function_complexities"])

        return complexity_data

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _analyze_imports(self) -> dict[str, Any]:
        """分析导入模式"""
        import_data = {
            "import_types": Counter(),
            "imported_modules": Counter(),
            "relative_imports": 0,
            "absolute_imports": 0,
            "wildcard_imports": 0,
        }

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        import_data["import_types"]["import"] += 1
                        import_data["absolute_imports"] += 1

                        for alias in node.names:
                            import_data["imported_modules"][alias.name] += 1

                    elif isinstance(node, ast.ImportFrom):
                        import_data["import_types"]["from_import"] += 1

                        if node.level > 0:  # 相对导入
                            import_data["relative_imports"] += 1
                        else:
                            import_data["absolute_imports"] += 1

                        # 检查通配符导入
                        for alias in node.names:
                            if alias.name == "*":
                                import_data["wildcard_imports"] += 1

                            if node.module:
                                import_data["imported_modules"][node.module] += 1

            except (SyntaxError, UnicodeDecodeError):
                continue

        return import_data

    def _analyze_testing(self) -> dict[str, Any]:
        """分析测试模式"""
        testing_data = {
            "test_files": 0,
            "test_functions": 0,
            "test_frameworks": Counter(),
            "test_coverage_estimate": 0.0,
        }

        all_files = list(self.project_path.rglob("*.py"))
        python_files = [f for f in all_files if not self._should_skip_file(f)]

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # 检查是否为测试文件
                is_test_file = (
                    "test" in file_path.name.lower() or "test" in str(file_path.parent).lower()
                )

                if is_test_file:
                    testing_data["test_files"] += 1

                # 检查测试框架
                if "import unittest" in content or "from unittest" in content:
                    testing_data["test_frameworks"]["unittest"] += 1

                if "import pytest" in content or "from pytest" in content:
                    testing_data["test_frameworks"]["pytest"] += 1

                # 计算测试函数数量
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        testing_data["test_functions"] += 1

            except (SyntaxError, UnicodeDecodeError):
                continue

        # 估算测试覆盖率
        if len(python_files) > 0:
            testing_data["test_coverage_estimate"] = testing_data["test_files"] / len(python_files)

        return testing_data
