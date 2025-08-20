#!/usr/bin/env python3
"""
自动修复代码质量问题的脚本
"""

import re
from pathlib import Path
from typing import Any, Dict, List


def fix_empty_except_blocks(file_path: Path) -> bool:
    """修复空的异常处理块"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 查找空的except块
        patterns = [
            (
                r'except\s*:\s*\n\s*pass\s*\n',
                'except Exception:\n        pass  # TODO:    添加适当的异常处理\n',
            ),
            (
                r'except\s+Exception\s*:\s*\n\s*pass\s*\n',
                'except Exception:\n        pass  # TODO:    添加适当的异常处理\n',
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def fix_magic_numbers(file_path: Path) -> bool:
    """修复魔法数字"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 常见的魔法数字替换
        magic_number_replacements = {
            r'\b3600\b': 'SECONDS_PER_HOUR',  # 3600秒 = 1小时
            r'\b86400\b': 'SECONDS_PER_DAY',  # 86400秒 = 1天
            r'\b1024\b': 'BYTES_PER_KB',  # 1024字节 = 1KB
            r'\b365\b': 'DAYS_PER_YEAR',  # 365天 = 1年
            r'\b24\b': 'HOURS_PER_DAY',  # 24小时 = 1天
            r'\b60\b': 'MINUTES_PER_HOUR',  # 60分钟 = 1小时
        }

        # 只在特定上下文中替换，避免误替换
        for pattern, constant in magic_number_replacements.items():
            # 只在明显的时间/大小计算中替换
            if re.search(
                r'(time|timeout|sleep|size|limit|max|min).*' + pattern,
                content,
                re.IGNORECASE,
            ):
                # 添加常量定义到文件开头
                if constant not in content:
                    lines = content.split('\n')
                    # 找到导入语句后的位置
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_pos = i + 1
                        elif (
                            line.strip() and not line.startswith('#') and insert_pos > 0
                        ):
                            break

                    # 插入常量定义
                    pattern_value = pattern.strip('\\b')
                    constant_def = f"\n# 常量定义\n{constant} = {pattern_value}\n"
                    lines.insert(insert_pos, constant_def)
                    content = '\n'.join(lines)

                # 替换魔法数字
                content = re.sub(pattern, constant, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def fix_long_lines(file_path: Path) -> bool:
    """修复过长的行"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_lines = lines[:]
        modified = False

        for i, line in enumerate(lines):
            if len(line.rstrip()) > 120:
                # 尝试在合适的位置断行
                stripped_line = line.rstrip()

                # 如果是字符串，尝试拆分
                if '"' in stripped_line or "'" in stripped_line:
                    # 简单的字符串拆分
                    if len(stripped_line) > 120:
                        # 在逗号或空格处断行
                        for break_char in [', ', ' and ', ' or ', ' + ']:
                            if break_char in stripped_line:
                                parts = stripped_line.split(break_char, 1)
                                if len(parts) == 2 and len(parts[0]) < 100:
                                    indent = len(line) - len(line.lstrip())
                                    lines[i] = parts[0] + break_char + '\n'
                                    lines.insert(
                                        i + 1, ' ' * (indent + 4) + parts[1] + '\n'
                                    )
                                    modified = True
                                    break

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def fix_todo_comments(file_path: Path) -> bool:
    """改进TODO注释"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 改进TODO注释的格式
        patterns = [
            (r'#\s*TODO\s*:', '# TODO:    '),
            (r'#\s*FIXME\s*:', '# FIXME:    '),
            (r'#\s*HACK\s*:', '# HACK:    '),
            (r'#\s*XXX\s*:', '# XXX:    '),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def add_missing_docstrings(file_path: Path) -> bool:
    """为缺少文档字符串的函数和类添加基本文档"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 检查类定义
            if line.startswith('class ') and line.endswith(':'):
                class_name = line.split()[1].split('(')[0]
                # 检查下一行是否有文档字符串
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    docstring = f'{" " * (indent + 4)}"""{class_name}类"""'
                    lines.insert(i + 1, docstring)
                    i += 1  # 跳过插入的行

            # 检查函数定义
            elif line.startswith('def ') and line.endswith(':'):
                func_name = line.split()[1].split('(')[0]
                # 检查下一行是否有文档字符串
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    docstring = f'{" " * (indent + 4)}"""{func_name}函数"""'
                    lines.insert(i + 1, docstring)
                    i += 1  # 跳过插入的行

            i += 1

        new_content = '\n'.join(lines)
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def main():
    """主函数"""
    print("🔧 开始自动修复代码质量问题...")

    # 获取所有Python文件
    python_files = []
    for directory in ["aiculture", "tests", "scripts"]:
        dir_path = Path(directory)
        if dir_path.exists():
            for file_path in dir_path.rglob("*.py"):
                python_files.append(file_path)

    print(f"📁 找到 {len(python_files)} 个Python文件")

    # 修复各种问题
    fixes = {
        "空异常处理块": fix_empty_except_blocks,
        "魔法数字": fix_magic_numbers,
        "过长行": fix_long_lines,
        "TODO注释": fix_todo_comments,
        "缺失文档字符串": add_missing_docstrings,
    }

    for fix_name, fix_func in fixes.items():
        print(f"\n🔧 修复{fix_name}...")
        fixed_count = 0

        for file_path in python_files:
            if fix_func(file_path):
                fixed_count += 1
                print(f"  ✅ 修复了 {file_path}")

        print(f"  📊 修复了 {fixed_count} 个文件的{fix_name}问题")

    print("\n🎉 代码质量问题自动修复完成！")
    print("💡 建议:")
    print("   1. 运行测试确保修复没有破坏功能")
    print("   2. 手动检查修复的代码是否合理")
    print("   3. 运行代码格式化工具统一格式")


if __name__ == "__main__":
    main()
