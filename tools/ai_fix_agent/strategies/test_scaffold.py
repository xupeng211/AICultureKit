"""
测试脚手架生成策略
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Tuple


class TestScaffoldStrategy:
    """测试脚手架生成策略"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def can_fix(self, problem: Dict[str, Any]) -> bool:
        """判断是否可以生成测试脚手架"""
        return problem.get("type") in [
            "test_coverage",
            "file_coverage",
            "diff_coverage",
            "new_file_coverage",
        ]

    def generate_fix(self, problems: List[Dict[str, Any]]) -> Tuple[str, str, float]:
        """
        生成测试脚手架

        Returns:
            (patch_content, explanation, confidence)
        """

        # 收集需要测试的文件
        files_to_test = set()
        for problem in problems:
            if not self.can_fix(problem):
                continue

            file_path = problem.get("file", "")
            if file_path and file_path.endswith(".py") and not file_path.startswith("test_"):
                files_to_test.add(file_path)

        if not files_to_test:
            return "", "没有需要生成测试的文件", 0.0

        # 生成测试脚手架
        test_files = []
        explanations = []

        for file_path in files_to_test:
            test_content, test_explanation = self._generate_test_file(file_path)
            if test_content:
                test_files.append((file_path, test_content))
                explanations.append(test_explanation)

        if not test_files:
            return "", "无法生成有效的测试脚手架", 0.0

        # 生成patch（创建新测试文件）
        patch_content = self._generate_test_creation_patch(test_files)
        explanation = "## 测试脚手架生成\n\n" + "\n".join(explanations)
        confidence = 0.8  # 测试脚手架生成的置信度较高

        return patch_content, explanation, confidence

    def _generate_test_file(self, file_path: str) -> Tuple[str, str]:
        """为指定文件生成测试脚手架"""

        full_path = self.project_root / file_path
        if not full_path.exists():
            return "", f"文件不存在: {file_path}"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return "", f"读取文件失败: {e}"

        # 解析Python文件
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return "", f"语法错误，无法解析: {e}"

        # 提取类和函数
        classes, functions = self._extract_testable_items(tree)

        if not classes and not functions:
            return "", "文件中没有发现可测试的类或函数"

        # 生成测试内容
        test_content = self._generate_test_content(file_path, classes, functions)
        explanation = (
            f"为 {file_path} 生成测试脚手架 ({len(classes)} 个类, {len(functions)} 个函数)"
        )

        return test_content, explanation

    def _extract_testable_items(self, tree: ast.AST) -> Tuple[List[Dict], List[Dict]]:
        """提取可测试的类和函数"""

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 提取类信息
                if not node.name.startswith("_"):  # 跳过私有类
                    class_info = {
                        "name": node.name,
                        "methods": [],
                        "docstring": ast.get_docstring(node) or "",
                    }

                    # 提取类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                            method_info = {
                                "name": item.name,
                                "args": [arg.arg for arg in item.args.args[1:]],  # 跳过self
                                "docstring": ast.get_docstring(item) or "",
                                "returns": self._get_return_annotation(item),
                            }
                            class_info["methods"].append(method_info)

                    classes.append(class_info)

            elif isinstance(node, ast.FunctionDef):
                # 提取顶级函数
                if not node.name.startswith("_") and not self._is_inside_class(node, tree):
                    function_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                        "returns": self._get_return_annotation(node),
                    }
                    functions.append(function_info)

        return classes, functions

    def _is_inside_class(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """检查函数是否在类内部"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item is func_node:
                        return True
        return False

    def _get_return_annotation(self, func_node: ast.FunctionDef) -> str:
        """获取函数返回类型注解"""
        if func_node.returns:
            if isinstance(func_node.returns, ast.Name):
                return func_node.returns.id
            elif isinstance(func_node.returns, ast.Constant):
                return str(func_node.returns.value)
        return "Any"

    def _generate_test_content(
        self, file_path: str, classes: List[Dict], functions: List[Dict]
    ) -> str:
        """生成测试文件内容"""

        # 计算模块路径
        module_path = file_path.replace("/", ".").replace(".py", "")
        f"test_{Path(file_path).stem}.py"

        lines = []

        # 文件头
        lines.append('"""')
        lines.append(f"Tests for {module_path}")
        lines.append("")
        lines.append("Generated test scaffold - please implement actual test logic")
        lines.append('"""')
        lines.append("")

        # 导入
        lines.append("import pytest")
        lines.append("from unittest.mock import Mock, patch")
        lines.append("")

        # 导入被测试模块
        if classes or functions:
            imports = []
            for cls in classes:
                imports.append(cls["name"])
            for func in functions:
                imports.append(func["name"])

            lines.append(f"from {module_path} import {', '.join(imports)}")
            lines.append("")

        # 生成类测试
        for cls in classes:
            lines.extend(self._generate_class_tests(cls))
            lines.append("")

        # 生成函数测试
        for func in functions:
            lines.extend(self._generate_function_tests(func))
            lines.append("")

        # 添加集成测试占位符
        if classes or functions:
            lines.append("# TODO: Add integration tests")
            lines.append("# TODO: Add edge case tests")
            lines.append("# TODO: Add error handling tests")

        return "\n".join(lines)

    def _generate_class_tests(self, class_info: Dict) -> List[str]:
        """生成类测试"""

        lines = []
        class_name = class_info["name"]

        lines.append(f"class Test{class_name}:")
        lines.append(f'    """Tests for {class_name} class"""')
        lines.append("")

        # 生成初始化测试
        lines.append("    def test_init(self):")
        lines.append(f'        """Test {class_name} initialization"""')
        lines.append(f"        instance = {class_name}()")
        lines.append("        assert instance is not None")
        lines.append("        # TODO: Add specific initialization tests")
        lines.append("")

        # 为每个方法生成测试
        for method in class_info["methods"]:
            method_name = method["name"]
            args = method["args"]

            lines.append(f"    def test_{method_name}(self):")
            lines.append(f'        """Test {class_name}.{method_name} method"""')
            lines.append(f"        instance = {class_name}()")

            # 生成方法调用
            if args:
                arg_list = ", ".join([f"{arg}=None" for arg in args])
                lines.append(f"        result = instance.{method_name}({arg_list})")
            else:
                lines.append(f"        result = instance.{method_name}()")

            lines.append("        # TODO: Add assertions for expected behavior")
            lines.append("        # assert result == expected_value")
            lines.append("")

        return lines

    def _generate_function_tests(self, func_info: Dict) -> List[str]:
        """生成函数测试"""

        lines = []
        func_name = func_info["name"]
        args = func_info["args"]

        lines.append(f"def test_{func_name}():")
        lines.append(f'    """Test {func_name} function"""')

        # 生成函数调用
        if args:
            arg_list = ", ".join([f"{arg}=None" for arg in args])
            lines.append(f"    result = {func_name}({arg_list})")
        else:
            lines.append(f"    result = {func_name}()")

        lines.append("    # TODO: Add assertions for expected behavior")
        lines.append("    # assert result == expected_value")
        lines.append("")

        # 生成边界测试
        lines.append(f"def test_{func_name}_edge_cases():")
        lines.append(f'    """Test {func_name} edge cases"""')
        lines.append("    # TODO: Test with None values")
        lines.append("    # TODO: Test with empty values")
        lines.append("    # TODO: Test with invalid values")
        lines.append("    pass")
        lines.append("")

        # 生成错误测试
        lines.append(f"def test_{func_name}_errors():")
        lines.append(f'    """Test {func_name} error handling"""')
        lines.append("    # TODO: Test expected exceptions")
        lines.append("    # with pytest.raises(ValueError):")
        lines.append(f"    #     {func_name}(invalid_input)")
        lines.append("    pass")

        return lines

    def _generate_test_creation_patch(self, test_files: List[Tuple[str, str]]) -> str:
        """生成创建测试文件的patch"""

        patches = []

        for file_path, test_content in test_files:
            # 计算测试文件路径
            test_file_path = self._get_test_file_path(file_path)

            # 生成创建文件的patch
            patch_lines = [
                "--- /dev/null",
                f"+++ b/{test_file_path}",
                f"@@ -0,0 +1,{len(test_content.split(chr(10)))} @@",
            ]

            for line in test_content.split("\n"):
                patch_lines.append(f"+{line}")

            patches.append("\n".join(patch_lines))

        return "\n\n".join(patches)

    def _get_test_file_path(self, source_file_path: str) -> str:
        """计算测试文件路径"""

        source_path = Path(source_file_path)

        # 如果源文件在子目录中，在tests目录下创建相同结构
        if len(source_path.parts) > 1:
            test_path = Path("tests") / source_path.parent / f"test_{source_path.stem}.py"
        else:
            test_path = Path("tests") / f"test_{source_path.stem}.py"

        return str(test_path)

    def generate_todo_list(self, problems: List[Dict[str, Any]]) -> str:
        """生成测试TODO清单"""

        todos = []
        todos.append("# 测试覆盖率改进TODO清单\n")

        # 按文件分组
        files_by_coverage = {}
        for problem in problems:
            if not self.can_fix(problem):
                continue

            file_path = problem.get("file", "unknown")
            coverage = problem.get("metadata", {}).get("file_coverage", 0)

            if file_path not in files_by_coverage:
                files_by_coverage[file_path] = coverage

        # 按覆盖率排序
        sorted_files = sorted(files_by_coverage.items(), key=lambda x: x[1])

        todos.append("## 优先级排序（按当前覆盖率）\n")

        for i, (file_path, coverage) in enumerate(sorted_files, 1):
            todos.append(f"{i}. **{file_path}** (当前覆盖率: {coverage:.1f}%)")
            todos.append("   - [ ] 分析现有测试")
            todos.append("   - [ ] 识别未覆盖的代码路径")
            todos.append("   - [ ] 编写针对性测试用例")
            todos.append("   - [ ] 验证覆盖率提升")
            todos.append("")

        todos.append("## 通用测试改进建议\n")
        todos.append("- [ ] 添加边界值测试")
        todos.append("- [ ] 添加异常处理测试")
        todos.append("- [ ] 添加集成测试")
        todos.append("- [ ] 添加性能测试（如需要）")
        todos.append("- [ ] 添加并发测试（如需要）")
        todos.append("")

        todos.append("## 测试质量检查\n")
        todos.append("- [ ] 确保测试独立性")
        todos.append("- [ ] 确保测试可重复性")
        todos.append("- [ ] 添加有意义的断言")
        todos.append("- [ ] 使用描述性的测试名称")
        todos.append("- [ ] 添加测试文档")

        return "\n".join(todos)


def main():
    """测试函数"""
    strategy = TestScaffoldStrategy()

    # 测试问题
    test_problems = [
        {
            "type": "file_coverage",
            "file": "example.py",
            "metadata": {"file_coverage": 45.0},
        }
    ]

    patch, explanation, confidence = strategy.generate_fix(test_problems)
    print(f"Patch:\n{patch}")
    print(f"Explanation: {explanation}")
    print(f"Confidence: {confidence}")

    # 测试TODO清单
    todo_list = strategy.generate_todo_list(test_problems)
    print(f"\nTODO List:\n{todo_list}")


if __name__ == "__main__":
    main()
