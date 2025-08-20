from typing import Any

#!/usr/bin/env python3
"""
安全的文档字符串添加器
为缺失文档字符串的函数和类添加基础文档
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List


class DocstringAdder:
    """文档字符串添加器"""

    def __init__(self, project_path: Path = None) -> None:
        """内部方法： init"""
        self.project_path = project_path or Path.cwd()
        self.added_count = 0

    def generate_function_docstring(self, func_node: ast.FunctionDef) -> str:
        """为函数生成文档字符串"""
        func_name = func_node.name
        args = [arg.arg for arg in func_node.args.args if arg.arg != 'self']

        # 基于函数名生成描述
        if func_name.startswith('test_'):
            return f'"""测试 {func_name[5:].replace("_", " ")} 功能"""'
        elif func_name.startswith('_'):
            return f'"""内部方法：{func_name[1:].replace("_", " ")}"""'
        elif func_name in ['__init__', '__str__', '__repr__']:
            return (
                f'"""初始化方法"""'
                if func_name == '__init__'
                else f'"""字符串表示方法"""'
            )
        else:
            # 根据参数生成描述
            if args:
                args_desc = "\n        ".join(f"{arg}: 参数说明" for arg in args)
                return f'"""执行 {func_name.replace("_", " ")} 操作\n    \n    Args:\n        {args_desc}\n    """'
            else:
                return f'"""执行 {func_name.replace("_", " ")} 操作"""'

    def generate_class_docstring(self, class_node: ast.ClassDef) -> str:
        """为类生成文档字符串"""
        class_name = class_node.name

        # 基于类名生成描述
        if class_name.endswith('Test'):
            return f'"""测试 {class_name[:-4]} 类"""'
        elif class_name.endswith('Manager'):
            return f'"""{class_name[:-7]} 管理器"""'
        elif class_name.endswith('Checker'):
            return f'"""{class_name[:-7]} 检查器"""'
        elif class_name.endswith('Config'):
            return f'"""{class_name[:-6]} 配置类"""'
        else:
            return f'"""{class_name} 类"""'

    def add_docstring_to_node(
        self, content: str, node: ast.FunctionDef | ast.ClassDef
    ) -> str:
        """为节点添加文档字符串"""
        lines = content.split('\n')

        # 找到函数/类定义行
        def_line = node.lineno - 1  # ast行号从1开始

        # 检查下一行是否已经有文档字符串
        if def_line + 1 < len(lines):
            next_line = lines[def_line + 1].strip()
            if next_line.startswith('"""') or next_line.startswith("'''"):
                return content  # 已经有文档字符串

        # 计算缩进
        def_line_content = lines[def_line]
        indent = len(def_line_content) - len(def_line_content.lstrip())

        # 生成文档字符串
        if isinstance(node, ast.FunctionDef):
            docstring = self.generate_function_docstring(node)
        else:
            docstring = self.generate_class_docstring(node)

        # 插入文档字符串
        docstring_line = ' ' * (indent + 4) + docstring
        lines.insert(def_line + 1, docstring_line)

        self.added_count += 1
        return '\n'.join(lines)

    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            # 收集需要添加文档字符串的节点
            nodes_to_process = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # 检查是否已有文档字符串
                    if not ast.get_docstring(node):
                        nodes_to_process.append(node)

            if not nodes_to_process:
                return False

            # 按行号倒序处理，避免行号偏移问题
            nodes_to_process.sort(key=lambda x: x.lineno, reverse=True)

            modified_content = content
            for node in nodes_to_process:
                modified_content = self.add_docstring_to_node(modified_content, node)

            # 写回文件
            file_path.write_text(modified_content, encoding='utf-8')
            return True

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return False

    def process_all_files(self) -> Dict[str, int]:
        """处理所有Python文件"""
        stats = {"processed": 0, "modified": 0, "added_docstrings": 0}

        for py_file in self.project_path.rglob("*.py"):
            # 跳过虚拟环境和隐藏目录
            if any(
                part.startswith('.') or part in ['venv', '__pycache__', 'build', 'dist']
                for part in py_file.parts
            ):
                continue

            # 跳过模板文件
            if '{{' in str(py_file) or '}}' in str(py_file):
                continue

            stats["processed"] += 1
            old_count = self.added_count

            if self.process_file(py_file):
                stats["modified"] += 1
                added_in_file = self.added_count - old_count
                print(f"✅ {py_file}: 添加了 {added_in_file} 个文档字符串")

        stats["added_docstrings"] = self.added_count
        return stats


def main() -> Any:
    """主函数"""
    adder = DocstringAdder()

    print("🚀 开始添加文档字符串...")
    stats = adder.process_all_files()

    print("\n" + "=" * 50)
    print("📊 文档字符串添加完成！")
    print("=" * 50)
    print(f"📁 处理文件数: {stats['processed']}")
    print(f"✏️  修改文件数: {stats['modified']}")
    print(f"📝 添加文档字符串数: {stats['added_docstrings']}")

    if stats['added_docstrings'] > 0:
        print(f"\n💡 建议运行以下命令格式化代码:")
        print("   black . && isort .")


if __name__ == "__main__":
    main()
