#!/usr/bin/env python3
"""修复关键导入问题的脚本"""

from pathlib import Path


def fix_imports_in_file(file_path: Path) -> bool:
    """修复单个文件中的导入问题"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")

        # 检查需要添加的导入
        imports_to_add = []

        # 检查是否使用了但没有导入的模块
        if (
            "CultureEnforcer" in content
            and "from .culture_enforcer import CultureEnforcer" not in content
        ):
            imports_to_add.append("from .culture_enforcer import CultureEnforcer")

        if (
            "CICDGuardian" in content
            and "from .cicd_culture import CICDGuardian" not in content
        ):
            imports_to_add.append("from .cicd_culture import CICDGuardian")

        if "subprocess." in content and "import subprocess" not in content:
            imports_to_add.append("import subprocess")

        if "json." in content and "import json" not in content:
            imports_to_add.append("import json")

        if "ast." in content and "import ast" not in content:
            imports_to_add.append("import ast")

        if "os." in content and "import os" not in content:
            imports_to_add.append("import os")

        if "sys." in content and "import sys" not in content:
            imports_to_add.append("import sys")

        if "time." in content and "import time" not in content:
            imports_to_add.append("import time")

        if "datetime." in content and "import datetime" not in content:
            imports_to_add.append("import datetime")

        if "re." in content and "import re" not in content:
            imports_to_add.append("import re")

        # 如果需要添加导入，找到合适的位置
        if imports_to_add:
            # 找到导入区域的结束位置
            import_end_line = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    import_end_line = i
                elif line.strip() and not line.startswith("#") and import_end_line > 0:
                    break

            # 在导入区域末尾添加新的导入
            for import_stmt in imports_to_add:
                if import_stmt not in content:
                    lines.insert(import_end_line + 1, import_stmt)
                    import_end_line += 1

        # 修复空白行问题
        fixed_lines = []
        for line in lines:
            # 移除行尾空白
            fixed_line = line.rstrip()
            fixed_lines.append(fixed_line)

        new_content = "\n".join(fixed_lines)

        # 如果有变化，写回文件
        if new_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def fix_specific_files():
    """修复特定文件中的已知问题"""
    # 修复 cli.py 中的导入问题
    cli_file = Path("aiculture/cli.py")
    if cli_file.exists():
        try:
            with open(cli_file, encoding="utf-8") as f:
                content = f.read()

            # 添加缺失的导入
            imports_needed = []
            if (
                "CultureEnforcer" in content
                and "from .culture_enforcer import CultureEnforcer" not in content
            ):
                imports_needed.append("from .culture_enforcer import CultureEnforcer")

            if (
                "CICDGuardian" in content
                and "from .cicd_culture import CICDGuardian" not in content
            ):
                imports_needed.append("from .cicd_culture import CICDGuardian")

            if "subprocess." in content and "import subprocess" not in content:
                imports_needed.append("import subprocess")

            if imports_needed:
                lines = content.split("\n")
                # 找到导入区域
                import_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        import_line = i

                # 添加导入
                for import_stmt in imports_needed:
                    lines.insert(import_line + 1, import_stmt)
                    import_line += 1

                with open(cli_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                print(f"✅ 修复了 {cli_file} 的导入问题")

        except Exception as e:
            print(f"❌ 修复 {cli_file} 时出错: {e}")

    # 修复 culture_enforcer.py 中的导入问题
    enforcer_file = Path("aiculture/culture_enforcer.py")
    if enforcer_file.exists():
        try:
            with open(enforcer_file, encoding="utf-8") as f:
                content = f.read()

            if "json." in content and "import json" not in content:
                lines = content.split("\n")
                # 找到导入区域
                for i, line in enumerate(lines):
                    if line.strip().startswith("from pathlib import Path"):
                        lines.insert(i + 1, "import json")
                        break

                with open(enforcer_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                print(f"✅ 修复了 {enforcer_file} 的导入问题")

        except Exception as e:
            print(f"❌ 修复 {enforcer_file} 时出错: {e}")

    # 修复 culture_penetration_system.py 中的导入问题
    penetration_file = Path("aiculture/culture_penetration_system.py")
    if penetration_file.exists():
        try:
            with open(penetration_file, encoding="utf-8") as f:
                content = f.read()

            if "ast." in content and "import ast" not in content:
                lines = content.split("\n")
                # 找到导入区域
                for i, line in enumerate(lines):
                    if line.strip().startswith("import os"):
                        lines.insert(i + 1, "import ast")
                        break

                with open(penetration_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                print(f"✅ 修复了 {penetration_file} 的导入问题")

        except Exception as e:
            print(f"❌ 修复 {penetration_file} 时出错: {e}")


def remove_trailing_whitespace():
    """移除所有Python文件中的行尾空白"""
    python_files = list(Path("aiculture").rglob("*.py"))

    fixed_count = 0
    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 移除行尾空白
            lines = content.split("\n")
            fixed_lines = [line.rstrip() for line in lines]
            new_content = "\n".join(fixed_lines)

            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                fixed_count += 1

        except Exception as e:
            print(f"❌ 处理 {file_path} 时出错: {e}")

    print(f"✅ 清理了 {fixed_count} 个文件的行尾空白")


def main():
    """主函数"""
    print("🔧 开始修复关键代码质量问题...")

    # 1. 修复特定文件的导入问题
    print("\n1. 修复导入问题...")
    fix_specific_files()

    # 2. 移除行尾空白
    print("\n2. 清理行尾空白...")
    remove_trailing_whitespace()

    # 3. 修复其他文件的导入问题
    print("\n3. 检查其他文件的导入问题...")
    python_files = list(Path("aiculture").rglob("*.py"))
    fixed_count = 0

    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
            print(f"✅ 修复了 {file_path}")

    print(f"\n🔧 总共修复了 {fixed_count} 个文件的导入问题")

    print("\n🎉 关键代码质量问题修复完成！")
    print("💡 建议运行 'flake8 aiculture' 检查剩余问题")


if __name__ == "__main__":
    main()
