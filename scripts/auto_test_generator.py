#!/usr/bin/env python3
"""
AICultureKit 自动测试生成器
基于代码分析自动生成测试用例
"""

import ast
from pathlib import Path
from typing import Any, Dict


class AutoTestGenerator:
    """自动测试生成器"""

    def __init__(self, project_path: Path = None) -> None:
        """TODO: 添加函数文档字符串"""
        self.project_path = project_path or Path.cwd()
        self.generated_tests = []

    def analyze_function(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """分析函数并生成测试信息"""
        info = {
            "name": func_node.name,
            "args": [arg.arg for arg in func_node.args.args],
            "returns": None,
            "docstring": ast.get_docstring(func_node),
            "is_async": isinstance(func_node, ast.AsyncFunctionDef),
        }

        # 分析返回类型
        if func_node.returns:
            info["returns"] = ast.unparse(func_node.returns)

        return info

    def analyze_class(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """分析类并生成测试信息"""
        methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append(self.analyze_function(node))

        return {
            "name": class_node.name,
            "methods": methods,
            "docstring": ast.get_docstring(class_node),
            "bases": [ast.unparse(base) for base in class_node.bases],
        }

    def generate_function_tests(
        self, func_info: Dict[str, Any], module_name: str
    ) -> str:
        """为函数生成测试代码"""
        func_name = func_info["name"]
        args = func_info["args"]

        # 生成基础测试
        test_code = f'''
    def test_{func_name}_basic(self):
        """测试 {func_name} 基础功能"""
        # TODO:    添加具体的测试逻辑
        # 示例参数: {", ".join(args) if args else "无参数"}
        '''

        if args:
            test_code += f'''
        # 测试正常情况
        # result = {func_name}({", ".join(f"test_{arg}" for arg in args)})
        # assert result is not None
        '''
        else:
            test_code += f'''
        # result = {func_name}()
        # assert result is not None
        '''

        test_code += '''
        pass  # 移除此行并添加实际测试
'''

        # 生成边界测试
        test_code += f'''
    def test_{func_name}_edge_cases(self):
        """测试 {func_name} 边界情况"""
        # TODO:    添加边界情况测试
        '''

        if args:
            test_code += (
                '''
        # 测试空值
        # with pytest.raises(ValueError):
        #     result = '''
                + func_name
                + '''(None)

        # 测试无效输入
        # with pytest.raises(TypeError):
        #     result = '''
                + func_name
                + '''("invalid")
        '''
            )

        test_code += '''
        pass  # 移除此行并添加实际测试
'''

        return test_code

    def generate_class_tests(self, class_info: Dict[str, Any], module_name: str) -> str:
        """为类生成测试代码"""
        class_name = class_info["name"]

        test_code = f'''
class Test{class_name}:
    """测试 {class_name} 类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        # TODO:    初始化测试对象
        # self.instance = {class_name}()
        pass

    def test_{class_name.lower()}_initialization(self):
        """测试 {class_name} 初始化"""
        # TODO:    测试对象创建
        # instance = {class_name}()
        # assert instance is not None
        pass
'''

        # 为每个方法生成测试
        for method in class_info["methods"]:
            if method["name"].startswith("_") and method["name"] != "__init__":
                continue  # 跳过私有方法

            method_name = method["name"]
            test_code += f'''
    def test_{method_name}(self):
        """测试 {method_name} 方法"""
        # TODO:    添加 {method_name} 方法的测试
        # result = self.instance.{method_name}()
        # assert result is not None
        pass
'''

        return test_code

    def generate_test_file(self, py_file: Path) -> str:
        """为Python文件生成完整的测试文件"""
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except Exception as e:
            print(f"❌ 无法解析文件 {py_file}: {e}")
            return ""

        module_name = (
            str(py_file.relative_to(self.project_path))
            .replace('/', '.')
            .replace('.py', '')
        )

        # 生成测试文件头部
        test_content = f'''"""
自动生成的测试文件: {py_file.name}
模块: {module_name}

⚠️  这是自动生成的测试模板，请根据实际需求修改
"""

import pytest
from unittest.mock import Mock, patch
from {module_name} import *


'''

        # 分析模块中的函数和类
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # 只处理模块级别的函数
                functions.append(self.analyze_function(node))
            elif isinstance(node, ast.ClassDef):
                classes.append(self.analyze_class(node))

        # 生成函数测试
        if functions:
            test_content += "# 函数测试\n"
            for func in functions:
                if not func["name"].startswith("_"):  # 跳过私有函数
                    test_content += f"class Test{func['name'].title()}Function:\n"
                    test_content += f'    """测试 {func["name"]} 函数"""\n'
                    test_content += self.generate_function_tests(func, module_name)
                    test_content += "\n"

        # 生成类测试
        if classes:
            test_content += "# 类测试\n"
            for cls in classes:
                test_content += self.generate_class_tests(cls, module_name)
                test_content += "\n"

        # 如果没有找到任何可测试的内容
        if not functions and not classes:
            test_content += '''
class TestModule:
    """模块基础测试"""

    def test_module_import(self) -> None:
        """测试模块可以正常导入"""
        # 如果能执行到这里，说明模块导入成功
        assert True

    def test_module_attributes(self) -> None:
        """测试模块属性"""
        # TODO:    添加模块属性测试
        pass
'''

        return test_content

    def generate_all_tests(self) -> int:
        """为所有Python文件生成测试"""
        print("🧪 开始生成自动测试...")

        test_dir = self.project_path / "tests"
        test_dir.mkdir(exist_ok=True)

        # 创建 __init__.py
        (test_dir / "__init__.py").touch()

        generated_count = 0
        source_dir = self.project_path / "aiculture"

        for py_file in source_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # 计算测试文件路径
            relative_path = py_file.relative_to(source_dir)
            test_file = test_dir / f"test_{relative_path}"

            # 如果测试文件已存在且不是空的，跳过
            if test_file.exists() and test_file.stat().st_size > 100:
                continue

            # 生成测试内容
            test_content = self.generate_test_file(py_file)
            if test_content:
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text(test_content, encoding='utf-8')
                generated_count += 1
                self.generated_tests.append(str(test_file))
                print(f"✅ 生成测试文件: {test_file}")

        return generated_count


def main() -> None:
    """主函数"""
    generator = AutoTestGenerator()
    count = generator.generate_all_tests()

    print("\n" + "=" * 50)
    print("🎉 自动测试生成完成！")
    print("=" * 50)
    print(f"📊 生成了 {count} 个测试文件")

    if generator.generated_tests:
        print("\n📋 生成的测试文件:")
        for test_file in generator.generated_tests:
            print(f"   - {test_file}")

        print("\n💡 下一步:")
        print("   1. 查看生成的测试文件")
        print("   2. 根据实际需求修改测试逻辑")
        print("   3. 运行 pytest 验证测试")
        print("   4. 逐步完善测试用例")
    else:
        print("✨ 所有测试文件都已存在！")


if __name__ == "__main__":
    main()
