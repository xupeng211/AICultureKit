#!/usr/bin/env python3
"""
🏗️ 基础设施检查器 - 检查项目基础设施配置

这个模块用于检查项目的基础设施配置，包括环境管理、依赖管理、
配置管理、跨平台兼容性等问题。
"""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class InfrastructureViolation:
    """基础设施违规记录"""

    category: str
    severity: str  # "critical", "warning", "info"
    message: str
    file_path: str | None = None
    line_number: int | None = None
    suggestion: str | None = None
    auto_fixable: bool = False


class InfrastructureChecker:
    """基础设施检查器"""

    def __init__(self, project_path: Path) -> None:
        """初始化基础设施检查器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.violations: list[InfrastructureViolation] = []

    def check_all_infrastructure(self) -> list[InfrastructureViolation]:
        """执行所有基础设施检查

        Returns:
            发现的违规列表
        """
        self.violations.clear()

        # 环境管理检查
        self._check_environment_isolation()
        self._check_python_version_consistency()

        # 依赖管理检查
        self._check_dependency_management()
        self._check_security_vulnerabilities()

        # 配置管理检查
        self._check_configuration_management()
        self._check_environment_variables()

        # 基础设施即代码检查
        self._check_infrastructure_as_code()
        self._check_ci_cd_configuration()

        # 环境一致性检查
        self._check_cross_platform_compatibility()
        self._check_build_reproducibility()

        # IDE和开发工具检查
        self._check_development_tools()

        return self.violations

    def _add_violation(
        self,
        category: str,
        severity: str,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
        auto_fixable: bool = False,
    ) -> None:
        """添加违规记录"""
        self.violations.append(
            InfrastructureViolation(
                category=category,
                severity=severity,
                message=message,
                file_path=file_path,
                line_number=line_number,
                suggestion=suggestion,
                auto_fixable=auto_fixable,
            )
        )

    # 环境管理检查

    def _check_environment_isolation(self) -> None:
        """检查环境隔离配置"""
        # 检查是否在虚拟环境中
        if not self._is_in_virtual_env():
            self._add_violation(
                category="环境隔离",
                severity="critical",
                message="未使用虚拟环境，可能导致依赖冲突",
                suggestion="创建并激活Python虚拟环境: python -m venv .venv && source .venv/bin/activate",
                auto_fixable=True,
            )

        # 检查虚拟环境目录是否在.gitignore中
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            venv_patterns = [".venv", "venv/", "env/", "ENV/"]
            if not any(pattern in gitignore_content for pattern in venv_patterns):
                self._add_violation(
                    category="环境隔离",
                    severity="warning",
                    message="虚拟环境目录未在.gitignore中排除",
                    file_path=str(gitignore_path),
                    suggestion="在.gitignore中添加虚拟环境目录: .venv/, venv/, env/",
                    auto_fixable=True,
                )

        # 检查环境设置脚本
        setup_scripts = ["setup_environment.sh", "setup.sh", "bootstrap.sh"]
        if not any((self.project_path / script).exists() for script in setup_scripts):
            self._add_violation(
                category="环境隔离",
                severity="warning",
                message="缺少自动化环境设置脚本",
                suggestion="创建setup_environment.sh脚本用于一键环境设置",
                auto_fixable=True,
            )

    def _check_python_version_file(self) -> None:
        """检查.python-version文件"""
        python_version_file = self.project_path / ".python-version"
        if not python_version_file.exists():
            self._add_violation(
                category="版本一致性",
                severity="warning",
                message="缺少.python-version文件，无法确保Python版本一致性",
                suggestion="创建.python-version文件指定Python版本",
                auto_fixable=True,
            )

    def _check_pyproject_python_version(self) -> None:
        """检查pyproject.toml中的Python版本要求"""
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            if "requires-python" in content:
                # 提取Python版本要求
                match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    version_requirement = match.group(1)
                    if ">=" in version_requirement and version_requirement.count(".") < 2:
                        self._add_violation(
                            category="版本一致性",
                            severity="warning",
                            message=f"Python版本要求过于宽泛: {version_requirement}",
                            file_path=str(pyproject_path),
                            suggestion="使用更具体的版本要求，如 '>=3.11,<3.12'",
                            auto_fixable=False,
                        )

    def _check_cicd_python_version(self) -> None:
        """检查CI/CD配置中的Python版本"""
        github_workflow_dir = self.project_path / ".github" / "workflows"
        if github_workflow_dir.exists():
            for workflow_file in github_workflow_dir.glob("*.yml"):
                content = workflow_file.read_text()
                if "python-version" in content or "PYTHON_VERSION" in content:
                    # 简单检查是否使用了不同的Python版本
                    current_python = f"{sys.version_info.major}.{sys.version_info.minor}"
                    if current_python not in content:
                        self._add_violation(
                            category="版本一致性",
                            severity="warning",
                            message="CI/CD中的Python版本可能与开发环境不一致",
                            file_path=str(workflow_file),
                            suggestion=f"确保CI/CD使用相同的Python版本: {current_python}",
                            auto_fixable=False,
                        )

    def _check_python_version_consistency(self) -> None:
        """检查Python版本一致性"""
        self._check_python_version_file()
        self._check_pyproject_python_version()
        self._check_cicd_python_version()

    # 依赖管理检查

    def _check_dependency_management(self) -> None:
        """检查依赖管理配置"""
        requirements_txt = self.project_path / "requirements.txt"

        if requirements_txt.exists():
            content = requirements_txt.read_text()
            lines = [line.strip() for line in content.split("\n") if line.strip()]

            # 检查是否使用版本范围而非精确版本
            loose_versions = []
            for line in lines:
                if line.startswith("#") or line.startswith("-"):
                    continue
                if ">=" in line and "==" not in line:
                    loose_versions.append(line)

            if loose_versions:
                self._add_violation(
                    category="依赖管理",
                    severity="warning",
                    message="依赖使用版本范围而非精确版本，可能导致版本漂移",
                    file_path=str(requirements_txt),
                    suggestion="使用pip-tools生成精确版本的requirements.txt",
                    auto_fixable=False,
                )

        # 检查是否有锁定文件
        lock_files = [
            "requirements.lock",
            "requirements.freeze",
            "Pipfile.lock",
            "poetry.lock",
        ]
        has_lock_file = any((self.project_path / f).exists() for f in lock_files)

        if not has_lock_file:
            self._add_violation(
                category="依赖管理",
                severity="warning",
                message="缺少依赖锁定文件，构建可能不可重现",
                suggestion="生成依赖锁定文件: pip freeze > requirements.freeze",
                auto_fixable=True,
            )

        # 检查是否有开发依赖分离
        dev_files = ["requirements-dev.txt", "requirements/dev.txt", "pyproject.toml"]
        has_dev_deps = any((self.project_path / f).exists() for f in dev_files[:2])

        if not has_dev_deps and not (self.project_path / "pyproject.toml").exists():
            self._add_violation(
                category="依赖管理",
                severity="info",
                message="建议分离开发依赖和生产依赖",
                suggestion="创建requirements-dev.txt用于开发依赖",
                auto_fixable=False,
            )

    def _check_security_vulnerabilities(self) -> None:
        """检查安全漏洞"""
        # 检查是否有安全扫描配置
        security_tools = ["bandit", "safety", "pip-audit"]
        pyproject_path = self.project_path / "pyproject.toml"

        if pyproject_path.exists():
            content = pyproject_path.read_text()
            has_security_tools = any(tool in content for tool in security_tools)

            if not has_security_tools:
                self._add_violation(
                    category="安全管理",
                    severity="warning",
                    message="缺少自动化安全扫描工具配置",
                    suggestion="配置bandit和safety进行安全扫描",
                    auto_fixable=False,
                )

    # 配置管理检查

    def _check_configuration_management(self) -> None:
        """检查配置管理"""
        # 检查.env.example文件
        env_example = self.project_path / ".env.example"
        if not env_example.exists():
            self._add_violation(
                category="配置管理",
                severity="warning",
                message="缺少.env.example模板文件",
                suggestion="创建.env.example文件作为环境变量模板",
                auto_fixable=True,
            )

        # 检查.env文件是否在.gitignore中
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            if ".env" not in gitignore_content:
                self._add_violation(
                    category="配置管理",
                    severity="critical",
                    message=".env文件未在.gitignore中排除，可能泄露敏感信息",
                    file_path=str(gitignore_path),
                    suggestion="在.gitignore中添加.env文件",
                    auto_fixable=True,
                )

    def _check_environment_variables(self) -> None:
        """检查环境变量使用"""
        # 扫描代码中的硬编码问题
        python_files = list(self.project_path.rglob("*.py"))

        for py_file in python_files:
            if (
                py_file.name.startswith(".")
                or "venv" in str(py_file)
                or "__pycache__" in str(py_file)
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # 检查可能的硬编码密码、API密钥等
                    suspicious_patterns = [
                        r'password\s*=\s*["\'][^"\']{6,}["\']',
                        r'api_key\s*=\s*["\'][^"\']{10,}["\']',
                        r'secret\s*=\s*["\'][^"\']{8,}["\']',
                        r'token\s*=\s*["\'][^"\']{10,}["\']',
                    ]

                    for pattern in suspicious_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self._add_violation(
                                category="配置管理",
                                severity="critical",
                                message="发现可能的硬编码敏感信息",
                                file_path=str(py_file),
                                line_number=i,
                                suggestion="使用环境变量或配置文件管理敏感信息",
                                auto_fixable=False,
                            )

            except (UnicodeDecodeError, PermissionError):
                continue

    # 基础设施即代码检查

    def _check_infrastructure_as_code(self) -> None:
        """检查基础设施即代码配置"""
        # 检查Dockerfile
        dockerfile_paths = [
            self.project_path / "Dockerfile",
            self.project_path / "Dockerfile.dev",
            self.project_path / "docker" / "Dockerfile",
        ]

        has_dockerfile = any(path.exists() for path in dockerfile_paths)
        if not has_dockerfile:
            self._add_violation(
                category="基础设施即代码",
                severity="info",
                message="缺少Dockerfile，建议提供容器化支持",
                suggestion="创建Dockerfile用于容器化部署",
                auto_fixable=False,
            )

        # 检查docker-compose.yml
        compose_files = [
            self.project_path / "docker-compose.yml",
            self.project_path / "docker-compose.yaml",
            self.project_path / "docker-compose.dev.yml",
        ]

        has_compose = any(path.exists() for path in compose_files)
        if not has_compose and has_dockerfile:
            self._add_violation(
                category="基础设施即代码",
                severity="info",
                message="有Dockerfile但缺少docker-compose.yml",
                suggestion="创建docker-compose.yml用于本地开发环境",
                auto_fixable=False,
            )

    def _check_ci_cd_configuration(self) -> None:
        """检查CI/CD配置"""
        github_actions = self.project_path / ".github" / "workflows"
        gitlab_ci = self.project_path / ".gitlab-ci.yml"
        jenkins_file = self.project_path / "Jenkinsfile"

        has_ci_cd = (
            github_actions.exists()
            and any(github_actions.glob("*.yml"))
            or gitlab_ci.exists()
            or jenkins_file.exists()
        )

        if not has_ci_cd:
            self._add_violation(
                category="CI/CD",
                severity="warning",
                message="缺少CI/CD配置",
                suggestion="配置GitHub Actions、GitLab CI或其他CI/CD工具",
                auto_fixable=False,
            )

    # 环境一致性检查

    def _check_cross_platform_compatibility(self) -> None:
        """检查跨平台兼容性"""
        python_files = list(self.project_path.rglob("*.py"))

        for py_file in python_files:
            if py_file.name.startswith(".") or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")

                # 检查硬编码路径分隔符
                if "\\\\" in content or content.count("/") > content.count("os.path") * 3:
                    # 简单的启发式检查
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if re.search(r'["\'][A-Za-z]:[\\\/]', line) or line.count("\\\\") > 0:
                            self._add_violation(
                                category="跨平台兼容性",
                                severity="warning",
                                message="发现可能的硬编码路径",
                                file_path=str(py_file),
                                line_number=i,
                                suggestion="使用os.path.join()或pathlib处理路径",
                                auto_fixable=False,
                            )
                            break

            except (UnicodeDecodeError, PermissionError):
                continue

    def _check_build_reproducibility(self) -> None:
        """检查构建可重现性"""
        # 检查是否锁定了构建工具版本
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            if "build-system" in content:
                if not re.search(r"requires.*=.*\d+\.\d+", content):
                    self._add_violation(
                        category="构建可重现性",
                        severity="warning",
                        message="构建系统依赖版本未锁定",
                        file_path=str(pyproject_path),
                        suggestion="在build-system.requires中指定精确版本",
                        auto_fixable=False,
                    )

    # 开发工具检查

    def _check_development_tools(self) -> None:
        """检查开发工具配置"""
        # 检查.editorconfig
        editorconfig = self.project_path / ".editorconfig"
        if not editorconfig.exists():
            self._add_violation(
                category="开发工具",
                severity="info",
                message="缺少.editorconfig文件",
                suggestion="创建.editorconfig统一编辑器配置",
                auto_fixable=True,
            )

        # 检查IDE配置
        vscode_dir = self.project_path / ".vscode"
        if not vscode_dir.exists():
            self._add_violation(
                category="开发工具",
                severity="info",
                message="缺少VSCode配置",
                suggestion="创建.vscode/settings.json配置开发环境",
                auto_fixable=False,
            )

        # 检查pre-commit配置
        precommit_config = self.project_path / ".pre-commit-config.yaml"
        if not precommit_config.exists():
            self._add_violation(
                category="开发工具",
                severity="info",
                message="缺少pre-commit配置",
                suggestion="配置pre-commit自动化代码检查",
                auto_fixable=False,
            )

    # 辅助方法

    def _is_in_virtual_env(self) -> bool:
        """检查是否在虚拟环境中"""
        return (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
            or os.environ.get("VIRTUAL_ENV") is not None
        )

    def get_violations_by_severity(self, severity: str) -> list[InfrastructureViolation]:
        """按严重程度获取违规"""
        return [v for v in self.violations if v.severity == severity]

    def get_violations_by_category(self, category: str) -> list[InfrastructureViolation]:
        """按分类获取违规"""
        return [v for v in self.violations if v.category == category]

    def get_auto_fixable_violations(self) -> list[InfrastructureViolation]:
        """获取可自动修复的违规"""
        return [v for v in self.violations if v.auto_fixable]

    def generate_report(self) -> dict[str, Any]:
        """生成检查报告"""
        total_violations = len(self.violations)
        critical_count = len(self.get_violations_by_severity("critical"))
        warning_count = len(self.get_violations_by_severity("warning"))
        info_count = len(self.get_violations_by_severity("info"))
        auto_fixable_count = len(self.get_auto_fixable_violations())

        categories = {}
        for violation in self.violations:
            if violation.category not in categories:
                categories[violation.category] = []
            categories[violation.category].append(
                {
                    "severity": violation.severity,
                    "message": violation.message,
                    "file_path": violation.file_path,
                    "line_number": violation.line_number,
                    "suggestion": violation.suggestion,
                    "auto_fixable": violation.auto_fixable,
                }
            )

        return {
            "summary": {
                "total_violations": total_violations,
                "critical": critical_count,
                "warning": warning_count,
                "info": info_count,
                "auto_fixable": auto_fixable_count,
            },
            "categories": categories,
            "infrastructure_score": max(
                0, 100 - (critical_count * 20 + warning_count * 10 + info_count * 2)
            ),
        }
