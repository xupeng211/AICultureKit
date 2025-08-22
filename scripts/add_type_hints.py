#!/usr/bin/env python3
"""类型注解添加器
为缺失类型注解的函数添加基础类型提示
"""

import ast
from pathlib import Path
from typing import Any


class TypeHintAdder:
    """类型注解添加器"""

    def __init__(self, project_path: Path = None) -> None:
        """__init__函数"""
        self.project_path = project_path or Path.cwd()
        self.added_count = 0

    def infer_return_type(self, func_node: ast.FunctionDef) -> str:
        """推断函数返回类型"""
        func_name = func_node.name

        # 基于函数名推断返回类型
        if (
            func_name.startswith("is_")
            or func_name.startswith("has_")
            or func_name.startswith("can_")
        ):
            return "bool"
        if func_name.startswith("get_") and "list" in func_name.lower():
            return "List[Any]"
        if func_name.startswith("get_") and "dict" in func_name.lower():
            return "Dict[str, Any]"
        if (
            func_name.startswith("get_")
            or func_name.startswith("create_")
            or func_name.startswith("build_")
        ):
            return "Any"
        if func_name == "__init__":
            return "None"
        if func_name == "__str__" or func_name == "__repr__":
            return "str"
        if "count" in func_name.lower():
            return "int"
        if "path" in func_name.lower():
            return "Path"

        # 检查函数体中的return语句
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return):
                if node.value is None:
                    return "None"
                if isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, bool):
                        return "bool"
                    if isinstance(node.value.value, int):
                        return "int"
                    if isinstance(node.value.value, str):
                        return "str"
                elif isinstance(node.value, ast.Dict):
                    return "Dict[str, Any]"
                elif isinstance(node.value, ast.List):
                    return "List[Any]"

        # 默认返回类型
        return "Any"

    def add_return_type_annotation(
        self,
        content: str,
        func_node: ast.FunctionDef,
    ) -> str:
        """为函数添加返回类型注解"""
        lines = content.split("\n")

        # 找到函数定义行
        def_line_idx = func_node.lineno - 1

        # 检查是否已经有返回类型注解
        def_line = lines[def_line_idx]
        if "->" in def_line:
            return content  # 已经有返回类型注解

        # 推断返回类型
        return_type = self.infer_return_type(func_node)

        # 找到冒号的位置
        colon_pos = def_line.rfind(":")
        if colon_pos == -1:
            return content  # 找不到冒号，跳过

        # 插入返回类型注解
        new_def_line = (
            def_line[:colon_pos] + f" -> {return_type}" + def_line[colon_pos:]
        )
        lines[def_line_idx] = new_def_line

        self.added_count += 1
        return "\n".join(lines)

    def add_import_statements(self, content: str, needed_imports: set) -> str:
        """添加必要的导入语句"""
        if not needed_imports:
            return content

        lines = content.split("\n")

        # 找到合适的位置插入导入语句
        insert_pos = 0

        # 跳过文档字符串和编码声明
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped.startswith("#")
                or stripped.startswith('"""')
                or stripped.startswith("'''")
            ):
                continue
            if (
                stripped.startswith("from __future__")
                or stripped.startswith("import")
                or stripped.startswith("from")
            ):
                insert_pos = i + 1
            elif stripped:
                break

        # 检查是否已经有typing导入
        has_typing_import = any(
            "from typing import" in line or "import typing" in line
            for line in lines[: insert_pos + 5]
        )

        if not has_typing_import and needed_imports:
            import_line = f"from typing import {', '.join(sorted(needed_imports))}"
            lines.insert(insert_pos, import_line)
            lines.insert(insert_pos + 1, "")  # 添加空行

        return "\n".join(lines)

    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # 收集需要添加类型注解的函数
            functions_to_process = []
            needed_imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否已有返回类型注解
                    if node.returns is None:
                        functions_to_process.append(node)

                        # 确定需要的导入
                        return_type = self.infer_return_type(node)
                        if return_type in [
                            "List[Any]",
                            "Dict[str, Any]",
                            "Any",
                            "Optional[Any]",
                        ]:
                            if "List" in return_type:
                                needed_imports.add("List")
                            if "Dict" in return_type:
                                needed_imports.add("Dict")
                            if "Any" in return_type:
                                needed_imports.add("Any")
                            if "Optional" in return_type:
                                needed_imports.add("Optional")
                        elif return_type == "Path":
                            # 这个需要特殊处理，因为它来自pathlib
                            pass

            if not functions_to_process:
                return False

            # 按行号倒序处理，避免行号偏移问题
            functions_to_process.sort(key=lambda x: x.lineno, reverse=True)

            modified_content = content
            for func_node in functions_to_process:
                modified_content = self.add_return_type_annotation(
                    modified_content,
                    func_node,
                )

            # 添加必要的导入语句
            if needed_imports:
                modified_content = self.add_import_statements(
                    modified_content,
                    needed_imports,
                )

            # 写回文件
            file_path.write_text(modified_content, encoding="utf-8")
            return True

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return False

    def process_all_files(self) -> dict[str, int]:
        """处理所有Python文件"""
        stats = {"processed": 0, "modified": 0, "added_annotations": 0}

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

            stats["processed"] += 1
            old_count = self.added_count

            if self.process_file(py_file):
                stats["modified"] += 1
                added_in_file = self.added_count - old_count
                print(f"✅ {py_file}: 添加了 {added_in_file} 个类型注解")

        stats["added_annotations"] = self.added_count
        return stats


def main() -> Any:
    """主函数"""
    adder = TypeHintAdder()

    print("🚀 开始添加类型注解...")
    stats = adder.process_all_files()

    print("\n" + "=" * 50)
    print("📊 类型注解添加完成！")
    print("=" * 50)
    print(f"📁 处理文件数: {stats['processed']}")
    print(f"✏️  修改文件数: {stats['modified']}")
    print(f"🔧 添加类型注解数: {stats['added_annotations']}")

    if stats["added_annotations"] > 0:
        print("\n💡 建议运行以下命令格式化代码:")
        print("   black . && isort .")
        print("   mypy aiculture --ignore-missing-imports")


if __name__ == "__main__":
    main()
