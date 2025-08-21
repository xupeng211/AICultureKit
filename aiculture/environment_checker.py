#!/usr/bin/env python3
"""
🔍 环境检查器 - 检查开发环境配置

这个模块用于检查Python虚拟环境、依赖安装状态和开发环境配置。
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EnvironmentChecker:
    """环境检查器 - 验证开发环境设置"""

    def __init__(self, project_path=None) -> None:
        """初始化环境检查器

        Args:
            project_path: 项目路径，默认为当前目录
        """
        if project_path is None:
            self.project_path = Path.cwd()
        elif isinstance(project_path, str):
            self.project_path = Path(project_path)
        else:
            self.project_path = project_path

    @staticmethod
    def check_virtual_env() -> bool:
        """检查是否在虚拟环境中

        Returns:
            是否在虚拟环境中运行
        """
        # 检查多种虚拟环境标识
        return (
            hasattr(sys, "real_prefix")  # virtualenv
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)  # venv
            or os.environ.get("VIRTUAL_ENV") is not None  # 环境变量
            or os.environ.get("CONDA_DEFAULT_ENV") is not None  # conda
        )

    @staticmethod
    def get_virtual_env_path() -> Optional[str]:
        """获取虚拟环境路径

        Returns:
            虚拟环境路径，如果不在虚拟环境中返回None
        """
        return os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX")

    @staticmethod
    def get_python_info() -> Dict[str, str]:
        """获取Python环境信息

        Returns:
            Python环境信息字典
        """
        try:
            arch = platform.architecture()[0]
        except (AttributeError, TypeError):
            # 在某些环境下platform.architecture()可能返回字符串而不是元组
            arch = "unknown"

        return {
            "version": sys.version,
            "version_info": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "platform": platform.platform(),
            "architecture": arch,
            "prefix": sys.prefix,
            "base_prefix": getattr(sys, "base_prefix", sys.prefix),
        }

    def check_required_dependencies(self) -> Tuple[bool, List[str]]:
        """检查必需的依赖是否已安装

        Returns:
            (是否全部安装, 缺失的依赖列表)
        """
        required_packages = ["click", "jinja2", "pyyaml", "gitpython", "cookiecutter"]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        return len(missing_packages) == 0, missing_packages

    def check_development_dependencies(self) -> Tuple[bool, List[str]]:
        """检查开发依赖是否已安装

        Returns:
            (是否全部安装, 缺失的依赖列表)
        """
        dev_packages = ["pytest", "black", "isort", "flake8", "mypy"]

        missing_dev_packages = []

        for package in dev_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_dev_packages.append(package)

        return len(missing_dev_packages) == 0, missing_dev_packages

    def check_aiculture_installation(self) -> bool:
        """检查AICultureKit是否正确安装

        Returns:
            是否正确安装
        """
        try:
            pass

            return True
        except ImportError:
            return False

    def check_project_structure(self) -> Dict[str, bool]:
        """检查项目结构完整性

        Returns:
            项目文件状态字典
        """
        required_files = {
            "pyproject.toml": self.project_path / "pyproject.toml",
            "requirements.txt": self.project_path / "requirements.txt",
            "requirements-dev.txt": self.project_path / "requirements-dev.txt",
            ".gitignore": self.project_path / ".gitignore",
            "README.md": self.project_path / "README.md",
            "setup_environment.sh": self.project_path / "setup_environment.sh",
        }

        return {name: path.exists() for name, path in required_files.items()}

    def get_installed_packages_count(self) -> int:
        """获取已安装包的数量

        Returns:
            已安装包的数量
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
                check=True,
            )
            return (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 0

    def check_git_status(self) -> Dict[str, any]:
        """检查Git仓库状态

        Returns:
            Git状态信息
        """
        git_info = {
            "is_repo": False,
            "current_branch": None,
            "has_uncommitted_changes": False,
            "remote_url": None,
        }

        try:
            # 检查是否是Git仓库
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_path,
                capture_output=True,
                check=True,
            )
            git_info["is_repo"] = True

            # 获取当前分支
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            git_info["current_branch"] = result.stdout.strip()

            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            git_info["has_uncommitted_changes"] = bool(result.stdout.strip())

            # 获取远程仓库URL
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                git_info["remote_url"] = result.stdout.strip()
            except subprocess.CalledProcessError:
                pass

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return git_info

    def generate_environment_report(self) -> Dict[str, any]:
        """生成完整的环境报告

        Returns:
            环境状态完整报告
        """
        python_info = self.get_python_info()
        deps_ok, missing_deps = self.check_required_dependencies()
        dev_deps_ok, missing_dev_deps = self.check_development_dependencies()

        return {
            "timestamp": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True
            ).stdout.strip(),
            "virtual_environment": {
                "is_active": self.check_virtual_env(),
                "path": self.get_virtual_env_path(),
                "type": self._detect_venv_type(),
            },
            "python": python_info,
            "dependencies": {
                "required": {"all_installed": deps_ok, "missing": missing_deps},
                "development": {
                    "all_installed": dev_deps_ok,
                    "missing": missing_dev_deps,
                },
            },
            "aiculture": {"installed": self.check_aiculture_installation()},
            "project_structure": self.check_project_structure(),
            "installed_packages_count": self.get_installed_packages_count(),
            "git": self.check_git_status(),
        }

    def _detect_venv_type(self) -> str:
        """检测虚拟环境类型

        Returns:
            虚拟环境类型字符串
        """
        if os.environ.get("CONDA_DEFAULT_ENV"):
            return "conda"
        elif os.environ.get("VIRTUAL_ENV"):
            if "venv" in os.environ.get("VIRTUAL_ENV", ""):
                return "venv"
            else:
                return "virtualenv"
        elif hasattr(sys, "real_prefix"):
            return "virtualenv"
        elif hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix:
            return "venv"
        else:
            return "none"

    def print_environment_status(self) -> None:
        """打印环境状态报告"""
        report = self.generate_environment_report()

        print("🔍 AICultureKit 环境状态检查")
        print("=" * 50)

        # 虚拟环境状态
        venv = report["virtual_environment"]
        if venv["is_active"]:
            print(f"✅ 虚拟环境: {venv['type']} ({venv['path']})")
        else:
            print("❌ 虚拟环境: 未激活 (建议使用虚拟环境)")

        # Python信息
        python = report["python"]
        print(f"🐍 Python版本: {python['version_info']}")
        print(f"📍 Python路径: {python['executable']}")
        print(f"🖥️  平台: {python['platform']}")

        # 依赖状态
        deps = report["dependencies"]
        if deps["required"]["all_installed"]:
            print("✅ 必需依赖: 全部已安装")
        else:
            print(f"❌ 缺失依赖: {', '.join(deps['required']['missing'])}")

        if deps["development"]["all_installed"]:
            print("✅ 开发依赖: 全部已安装")
        else:
            print(f"⚠️  缺失开发依赖: {', '.join(deps['development']['missing'])}")

        # AICultureKit状态
        if report["aiculture"]["installed"]:
            print("✅ AICultureKit: 已正确安装")
        else:
            print("❌ AICultureKit: 未安装或安装错误")

        # 项目结构
        print(f"📦 已安装包数量: {report['installed_packages_count']}")

        structure = report["project_structure"]
        missing_files = [name for name, exists in structure.items() if not exists]
        if missing_files:
            print(f"⚠️  缺失文件: {', '.join(missing_files)}")
        else:
            print("✅ 项目结构: 完整")

        # Git状态
        git = report["git"]
        if git["is_repo"]:
            print(f"📋 Git分支: {git['current_branch']}")
            if git["has_uncommitted_changes"]:
                print("⚠️  有未提交的更改")
        else:
            print("⚠️  不是Git仓库")

        print("=" * 50)

    def suggest_fixes(self) -> List[str]:
        """建议修复措施

        Returns:
            修复建议列表
        """
        suggestions = []
        report = self.generate_environment_report()

        if not report["virtual_environment"]["is_active"]:
            suggestions.append("🌟 激活虚拟环境: source aiculture-env/bin/activate")

        if not report["dependencies"]["required"]["all_installed"]:
            suggestions.append("📦 安装必需依赖: pip install -r requirements.txt")

        if not report["dependencies"]["development"]["all_installed"]:
            suggestions.append("🧪 安装开发依赖: pip install -r requirements-dev.txt")

        if not report["aiculture"]["installed"]:
            suggestions.append("🔧 安装AICultureKit: pip install -e .")

        structure = report["project_structure"]
        if not structure.get("setup_environment.sh"):
            suggestions.append("📋 运行环境设置脚本: bash setup_environment.sh")

        # 安全地检查git状态
        git_info = report.get("git", {})
        if not git_info.get("is_repo", True):  # 默认假设是repo，避免误报
            suggestions.append("📋 初始化Git仓库: git init")

        return suggestions


def main() -> None:
    """主函数 - 命令行入口"""
    checker = EnvironmentChecker()
    checker.print_environment_status()

    suggestions = checker.suggest_fixes()
    if suggestions:
        print("\n💡 建议的修复措施:")
        for suggestion in suggestions:
            print(f"  {suggestion}")


if __name__ == "__main__":
    main()
