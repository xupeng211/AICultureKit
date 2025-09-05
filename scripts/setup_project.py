#!/usr/bin/env python3
"""
🔧 项目初始化脚本

快速设置完整的开发环境，包括Git初始化、依赖安装、基础文件创建等。
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: Path = None) -> bool:
    """
    运行命令并返回是否成功

    Args:
        command: 要执行的命令
        cwd: 工作目录

    Returns:
        是否执行成功
    """
    try:
        result = subprocess.run(
            command.split(), cwd=cwd, capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def setup_git(project_root: Path) -> bool:
    """初始化Git仓库"""
    print("🌿 初始化Git仓库...")

    if (project_root / ".git").exists():
        print("   Git仓库已存在，跳过初始化")
        return True

    success = True

    # 初始化仓库
    if not run_command("git init", project_root):
        print("   ❌ Git初始化失败")
        success = False

    # 创建.gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
logs/*.log
logs/*.json
backup/
.env
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
"""

    gitignore_file = project_root / ".gitignore"
    gitignore_file.write_text(gitignore_content)

    print("   ✅ Git仓库初始化完成")
    return success


def create_basic_files(project_root: Path) -> bool:
    """创建基础Python文件"""
    print("📁 创建基础文件结构...")

    # 创建__init__.py文件
    init_files = [
        "src/core/__init__.py",
        "src/models/__init__.py",
        "src/services/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/fixtures/__init__.py",
    ]

    for init_file in init_files:
        file_path = project_root / init_file
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if not file_path.exists():
            file_path.write_text('"""模块初始化文件"""\n')

    # 创建示例测试文件
    test_example = project_root / "tests/test_example.py"
    if not test_example.exists():
        test_content = '''"""示例测试文件"""

import pytest


def test_example():
    """示例测试函数"""
    assert 1 + 1 == 2


def test_string_operations():
    """字符串操作测试"""
    text = "Hello, World!"
    assert text.upper() == "HELLO, WORLD!"
    assert text.lower() == "hello, world!"


class TestExampleClass:
    """示例测试类"""
    def test_list_operations(self):
        """列表操作测试"""
        test_list = [1, 2, 3]
        test_list.append(4)
        assert len(test_list) == 4
        assert test_list[-1] == 4
'''
        test_example.write_text(test_content)

    print("   ✅ 基础文件结构创建完成")
    return True


def install_dependencies(project_root: Path) -> bool:
    """安装项目依赖"""
    print("📦 安装项目依赖...")

    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print("   ⚠️ requirements.txt不存在，跳过依赖安装")
        return True

    # 检查是否有虚拟环境
    venv_paths = [project_root / "venv", project_root / "env", project_root / ".venv"]

    has_venv = any(venv_path.exists() for venv_path in venv_paths)

    if not has_venv:
        print("   💡 建议创建虚拟环境: python -m venv venv")

    # 安装依赖
    if run_command("pip install -r requirements.txt", project_root):
        print("   ✅ 依赖安装完成")
        return True
    else:
        print("   ❌ 依赖安装失败")
        return False


def setup_pre_commit(project_root: Path) -> bool:
    """设置pre-commit钩子"""
    print("🔧 设置pre-commit钩子...")

    # 创建.pre-commit-config.yaml
    precommit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
"""

    config_file = project_root / ".pre-commit-config.yaml"
    config_file.write_text(precommit_config)

    # 安装pre-commit钩子
    if run_command("pre-commit install", project_root):
        print("   ✅ pre-commit钩子设置完成")
        return True
    else:
        print("   ⚠️ pre-commit钩子设置失败（可能未安装pre-commit）")
        return False


def run_initial_tests(project_root: Path) -> bool:
    """运行初始测试"""
    print("🧪 运行初始测试...")

    # 运行示例测试
    if run_command("python -m pytest tests/test_example.py -v", project_root):
        print("   ✅ 初始测试通过")
        return True
    else:
        print("   ⚠️ 初始测试失败（可能未安装pytest）")
        return False


def main():
    """主函数"""
    print("🚀 开始项目初始化...")

    project_root = Path.cwd()
    print(f"   项目根目录: {project_root}")

    # 执行初始化步骤
    steps = [
        ("Git初始化", lambda: setup_git(project_root)),
        ("创建基础文件", lambda: create_basic_files(project_root)),
        ("安装依赖", lambda: install_dependencies(project_root)),
        ("设置pre-commit", lambda: setup_pre_commit(project_root)),
        ("运行初始测试", lambda: run_initial_tests(project_root)),
    ]

    success_count = 0
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
        except Exception as e:
            print(f"   💥 {step_name}异常: {e}")

    print(f"\n📊 初始化完成: {success_count}/{len(steps)} 步骤成功")

    if success_count == len(steps):
        print("\n🎉 项目初始化完全成功！")
        print("\n下一步建议:")
        print("1. 运行 python scripts/context_loader.py --summary")
        print("2. 运行 python scripts/quality_checker.py --summary")
        print("3. 开始使用Cursor闭环开发系统")
    else:
        print("\n⚠️ 项目初始化部分完成，请检查上述错误")
        sys.exit(1)


if __name__ == "__main__":
    main()
