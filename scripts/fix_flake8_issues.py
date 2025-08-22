#!/usr/bin/env python3
"""
自动修复flake8问题的脚本
"""

import re
import subprocess
from pathlib import Path


def run_flake8() -> list[str]:
    """运行flake8并获取问题列表"""
    try:
        result = subprocess.run(
            ["flake8", "aiculture", "--max-line-length=100", "--ignore=E203,W503"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def fix_unused_imports(file_path: Path, content: str) -> str:
    """修复未使用的导入"""
    lines = content.split("\n")

    # 需要移除的未使用导入
    unused_patterns = [
        r"from dataclasses import field",
        r"from typing import Optional",
        r"from typing import Set",
        r"from typing import Tuple",
        r"import ast",
        r"import hashlib",
        r"import subprocess",
        r"import os",
        r"import json",
        r"from typing import Callable",
        r"from datetime import datetime",
        r"from datetime import timedelta",
    ]

    # 只移除确实未使用的导入
    for i, line in enumerate(lines):
        for pattern in unused_patterns:
            if re.match(pattern, line.strip()):
                # 检查是否在代码中使用
                import_name = pattern.split()[-1].replace(",", "")
                if import_name not in content or content.count(import_name) <= 1:
                    lines[i] = ""  # 移除该行

    return "\n".join(lines)


def fix_whitespace_issues(content: str) -> str:
    """修复空白字符问题"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # 移除行尾空白
        line = line.rstrip()

        # 修复空白行中的空格
        if line.strip() == "":
            line = ""

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_line_length(content: str) -> str:
    """修复行长度问题"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) > 100:
            # 简单的行分割策略
            if " and " in line and len(line) > 100:
                # 在 and 处分割
                parts = line.split(" and ")
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(parts[0] + " and")
                    fixed_lines.append(" " * (indent + 4) + parts[1])
                    continue

            if ", " in line and len(line) > 100:
                # 在逗号处分割
                parts = line.split(", ")
                if len(parts) > 2:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(parts[0] + ",")
                    for part in parts[1:-1]:
                        fixed_lines.append(" " * (indent + 4) + part + ",")
                    fixed_lines.append(" " * (indent + 4) + parts[-1])
                    continue

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_f_string_issues(content: str) -> str:
    """修复f-string问题"""
    # 将没有占位符的f-string改为普通字符串
    content = re.sub(r'f"([^{}"]*)"', r'"\1"', content)
    content = re.sub(r"f'([^{}']*)'", r"'\1'", content)
    return content


def fix_variable_issues(content: str) -> str:
    """修复变量问题"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # 修复未使用的变量
        if "F841" in line or "local variable" in line and "assigned to but never used" in line:
            # 在变量名前加下划线表示故意未使用
            if "=" in line and not line.strip().startswith("#"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    var_part = parts[0].strip()
                    if not var_part.startswith("_"):
                        line = line.replace(var_part, "_" + var_part, 1)

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_redefinition_issues(content: str) -> str:
    """修复重定义问题"""
    lines = content.split("\n")

    # 移除重复的导入
    seen_imports = set()
    fixed_lines = []

    for line in lines:
        if line.strip().startswith(("import ", "from ")):
            if line.strip() in seen_imports:
                continue  # 跳过重复的导入
            seen_imports.add(line.strip())

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file(file_path: Path) -> bool:
    """修复单个文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 应用各种修复
        content = fix_unused_imports(file_path, content)
        content = fix_whitespace_issues(content)
        content = fix_line_length(content)
        content = fix_f_string_issues(content)
        content = fix_variable_issues(content)
        content = fix_redefinition_issues(content)

        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 修复了 {file_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def main():
    """主函数"""
    print("🔧 开始自动修复flake8问题...")

    # 获取所有Python文件
    python_files = []
    for py_file in Path("aiculture").rglob("*.py"):
        if not any(part.startswith(".") or part in ["__pycache__"] for part in py_file.parts):
            python_files.append(py_file)

    print(f"📁 找到 {len(python_files)} 个Python文件")

    # 修复文件
    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1

    print(f"✅ 修复了 {fixed_count} 个文件")

    # 运行black和isort进行最终格式化
    print("🎨 运行black和isort进行格式化...")
    try:
        subprocess.run(["black", "aiculture"], check=True)
        subprocess.run(["isort", "aiculture"], check=True)
        print("✅ 格式化完成")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ 格式化时出现问题: {e}")

    # 再次检查flake8
    print("🔍 再次检查flake8...")
    issues = run_flake8()
    if issues and issues[0]:  # 检查是否有实际问题
        print(f"⚠️ 仍有 {len(issues)} 个问题需要手动修复")
        for issue in issues[:5]:  # 只显示前5个
            print(f"   {issue}")
    else:
        print("🎉 所有flake8问题已修复！")


if __name__ == "__main__":
    main()
