"""CI/CD智能守护系统
全面检测和预防构建失败的智能化解决方案
"""

import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import requests
import yaml

# 常量定义
MINUTES_PER_HOUR = 60


class RiskLevel(Enum):
    """风险等级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BuildRisk:
    """构建风险"""

    category: str
    risk_level: RiskLevel
    description: str
    impact: str
    prevention: str
    auto_fix: bool = False


class CICDGuardian:
    """CI/CD智能守护系统"""

    def __init__(self, project_path: str = ".") -> None:
        """内部方法： init"""
        self.project_path = Path(project_path)
        self.risks: list[BuildRisk] = []
        self.docker_client = None
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置"""
        config_file = self.project_path / "aiculture.yaml"
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def comprehensive_health_check(self) -> dict[str, Any]:
        """全面健康检查"""
        print("🔍 开始CI/CD构建健康检查...")

        self.risks.clear()

        # 1. 环境检查
        self._check_environment()

        # 2. 依赖检查
        self._check_dependencies()

        # 3. 网络检查
        self._check_network()

        # 4. 资源检查
        self._check_resources()

        # 5. 配置检查
        self._check_configuration()

        # 6. 代码质量检查
        self._check_code_quality()

        # 7. 安全检查
        self._check_security()

        return self._generate_report()

    def _check_environment(self) -> Any:
        """环境检查"""
        print("📦 检查环境配置...")

        # 检查Dockerfile基础镜像
        dockerfile = self.project_path / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile) as f:
                content = f.read()

            # 检查基础镜像版本固定
            if "FROM python:latest" in content or "FROM ubuntu:latest" in content:
                self.risks.append(
                    BuildRisk(
                        category="environment",
                        risk_level=RiskLevel.HIGH,
                        description="使用了不稳定的latest标签",
                        impact="基础镜像更新可能导致构建失败",
                        prevention="使用固定版本号，如 python:3.10-slim",
                        auto_fix=True,
                    ),
                )

            # 检查多阶段构建
            if "FROM" in content and content.count("FROM") == 1:
                self.risks.append(
                    BuildRisk(
                        category="environment",
                        risk_level=RiskLevel.MEDIUM,
                        description="未使用多阶段构建",
                        impact="镜像体积大，构建时间长",
                        prevention="采用多阶段构建优化镜像大小",
                        auto_fix=False,
                    ),
                )

        # 检查系统依赖
        if "apt-get install" in content and "apt-get clean" not in content:
            self.risks.append(
                BuildRisk(
                    category="environment",
                    risk_level=RiskLevel.MEDIUM,
                    description="未清理apt缓存",
                    impact="镜像体积增大",
                    prevention="添加 rm -rf /var/lib/apt/lists/*",
                    auto_fix=True,
                ),
            )

    def _check_dependencies(self) -> Any:
        """依赖检查"""
        print("📋 检查依赖管理...")

        # 检查requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                content = f.read()

            # 检查版本固定
            lines = content.strip().split("\n")
            unpinned = []
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    if ">=" in line or "~=" in line or "^" in line:
                        unpinned.append(line.strip())

            if unpinned:
                self.risks.append(
                    BuildRisk(
                        category="dependencies",
                        risk_level=RiskLevel.HIGH,
                        description=f"发现{len(unpinned)}个未固定版本的依赖",
                        impact="依赖版本更新可能导致构建失败",
                        prevention="使用 pip freeze 生成精确版本锁定",
                        auto_fix=True,
                    ),
                )

        # 检查依赖安全性
        try:
            result = subprocess.run(
                ["safety", "check", "-r", str(req_file)],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                self.risks.append(
                    BuildRisk(
                        category="dependencies",
                        risk_level=RiskLevel.CRITICAL,
                        description="发现依赖安全漏洞",
                        impact="存在安全风险，可能被拒绝部署",
                        prevention="更新有漏洞的依赖包",
                        auto_fix=False,
                    ),
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def _check_network(self) -> Any:
        """网络检查"""
        print("🌐 检查网络连通性...")

        # 检查关键服务连通性
        critical_urls = [
            "https://pypi.org/simple/",
            "https://registry-1.docker.io/",
            "https://github.com/",
            "https://api.github.com/",
        ]

        failed_connections = []
        for url in critical_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code >= 400:
                    failed_connections.append(url)
            except requests.RequestException:
                failed_connections.append(url)

        if failed_connections:
            self.risks.append(
                BuildRisk(
                    category="network",
                    risk_level=RiskLevel.HIGH,
                    description=f"无法连接到关键服务: {failed_connections}",
                    impact="构建过程中可能网络失败",
                    prevention="配置重试机制和备用镜像源",
                    auto_fix=False,
                ),
            )

    def _check_resources(self) -> Any:
        """资源检查"""
        print("💾 检查系统资源...")

        # 检查磁盘空间
        import shutil

        total, used, free = shutil.disk_usage(self.project_path)
        free_gb = free // (1024**3)

        if free_gb < 5:
            self.risks.append(
                BuildRisk(
                    category="resources",
                    risk_level=RiskLevel.CRITICAL,
                    description=f"磁盘空间不足: {free_gb}GB",
                    impact="构建过程中可能空间不足失败",
                    prevention="清理磁盘空间或增加存储",
                    auto_fix=False,
                ),
            )
        elif free_gb < 10:
            self.risks.append(
                BuildRisk(
                    category="resources",
                    risk_level=RiskLevel.MEDIUM,
                    description=f"磁盘空间紧张: {free_gb}GB",
                    impact="可能影响构建性能",
                    prevention="建议清理不必要文件",
                    auto_fix=False,
                ),
            )

        # 检查内存使用
        try:
            with open("/proc/meminfo") as f:
                meminfo = f.read()
            mem_available = (
                int(
                    [line for line in meminfo.split("\n") if "MemAvailable" in line][
                        0
                    ].split()[1],
                )
                // 1024
            )

            if mem_available < 2048:  # 小于2GB
                self.risks.append(
                    BuildRisk(
                        category="resources",
                        risk_level=RiskLevel.HIGH,
                        description=f"可用内存不足: {mem_available}MB",
                        impact="构建过程可能内存溢出",
                        prevention="关闭不必要进程或增加内存",
                        auto_fix=False,
                    ),
                )
        except (FileNotFoundError, IndexError):
            pass  # 非Linux系统

    def _check_configuration(self) -> Any:
        """配置检查"""
        print("⚙️ 检查配置文件...")

        # 检查.dockerignore
        dockerignore = self.project_path / ".dockerignore"
        if not dockerignore.exists():
            self.risks.append(
                BuildRisk(
                    category="configuration",
                    risk_level=RiskLevel.MEDIUM,
                    description="缺少.dockerignore文件",
                    impact="可能复制不必要文件，增加构建时间",
                    prevention="创建.dockerignore排除不必要文件",
                    auto_fix=True,
                ),
            )

        # 检查CI/CD配置
        ci_config = self.project_path / ".github" / "workflows"
        if ci_config.exists():
            for workflow_file in ci_config.glob("*.yml"):
                with open(workflow_file) as f:
                    workflow = yaml.safe_load(f)

                # 检查超时设置
                jobs = workflow.get("jobs", {})
                for job_name, job_config in jobs.items():
                    if "timeout-minutes" not in job_config:
                        self.risks.append(
                            BuildRisk(
                                category="configuration",
                                risk_level=RiskLevel.MEDIUM,
                                description=f"作业 {job_name} 缺少超时设置",
                                impact="可能导致无限等待",
                                prevention="添加 timeout-minutes 配置",
                                auto_fix=True,
                            ),
                        )

    def _check_code_quality(self) -> Any:
        """代码质量检查"""
        print("📝 检查代码质量...")

        # 检查是否有AI文化配置
        if not (self.project_path / "aiculture.yaml").exists():
            self.risks.append(
                BuildRisk(
                    category="code_quality",
                    risk_level=RiskLevel.MEDIUM,
                    description="缺少AI开发文化配置",
                    impact="无法自动质量检查和修复",
                    prevention="运行 aiculture enable-culture 启用",
                    auto_fix=True,
                ),
            )

    def _check_security(self) -> Any:
        """安全检查"""
        print("🔒 检查安全配置...")

        # 检查密钥泄露
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        import re

        for py_file in self.project_path.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.risks.append(
                            BuildRisk(
                                category="security",
                                risk_level=RiskLevel.CRITICAL,
                                description=f"在 {py_file} 中发现可能的硬编码密钥",
                                impact="敏感信息泄露风险",
                                prevention="使用环境变量或密钥管理服务",
                                auto_fix=False,
                            ),
                        )
                        break
            except Exception:
                continue

    def _generate_report(self) -> dict[str, Any]:
        """生成检查报告"""
        critical_risks = [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
        medium_risks = [r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]
        low_risks = [r for r in self.risks if r.risk_level == RiskLevel.LOW]

        # 计算风险评分
        score = 100
        score -= len(critical_risks) * 25
        score -= len(high_risks) * 15
        score -= len(medium_risks) * 8
        score -= len(low_risks) * 3
        score = max(0, score)

        return {
            "timestamp": time.time(),
            "score": score,
            "risk_summary": {
                "critical": len(critical_risks),
                "high": len(high_risks),
                "medium": len(medium_risks),
                "low": len(low_risks),
                "total": len(self.risks),
            },
            "risks": [
                {
                    "category": risk.category,
                    "risk_level": risk.risk_level.value,
                    "description": risk.description,
                    "impact": risk.impact,
                    "prevention": risk.prevention,
                    "auto_fix": risk.auto_fix,
                }
                for risk in self.risks
            ],
            "recommendation": self._get_recommendation(score),
        }

    def _get_recommendation(self, score: int) -> str:
        """获取建议"""
        if score >= 90:
            return "✅ 构建风险很低，可以安全部署"
        if score >= 70:
            return "⚠️ 存在中等风险，建议修复后部署"
        if score >= 50:
            return "🚨 存在高风险，必须修复关键问题"
        return "🔥 风险极高，禁止部署，需要全面修复"

    def auto_fix_issues(self) -> dict[str, Any]:
        """自动修复问题"""
        print("🔧 开始自动修复问题...")

        fixed_issues = []
        failed_fixes = []

        for risk in self.risks:
            if risk.auto_fix:
                try:
                    if self._fix_issue(risk):
                        fixed_issues.append(risk.description)
                    else:
                        failed_fixes.append(risk.description)
                except Exception as e:
                    raise e
                    failed_fixes.append(f"{risk.description}: {e!s}")

        return {
            "fixed": fixed_issues,
            "failed": failed_fixes,
            "success_rate": (
                len(fixed_issues) / (len(fixed_issues) + len(failed_fixes))
                if (len(fixed_issues) + len(failed_fixes)) > 0
                else 1.0
            ),
        }

    def _fix_issue(self, risk: BuildRisk) -> bool:
        """修复具体问题"""
        if "latest标签" in risk.description:
            return self._fix_dockerfile_base_image()
        if "dockerignore" in risk.description:
            return self._create_dockerignore()
        if "未固定版本" in risk.description:
            return self._fix_requirements_versions()
        if "超时设置" in risk.description:
            return self._add_workflow_timeouts()
        if "AI开发文化配置" in risk.description:
            return self._setup_ai_culture()

        return False

    def _fix_dockerfile_base_image(self) -> bool:
        """修复Dockerfile基础镜像"""
        dockerfile = self.project_path / "Dockerfile"
        if not dockerfile.exists():
            return False

        with open(dockerfile) as f:
            content = f.read()

        # 替换latest标签
        content = content.replace("FROM python:latest", "FROM python:3.10-slim")
        content = content.replace("FROM ubuntu:latest", "FROM ubuntu:22.04")

        with open(dockerfile, "w") as f:
            f.write(content)

        return True

    def _create_dockerignore(self) -> bool:
        """创建.dockerignore文件"""
        dockerignore_content = """# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.pytest_cache
.cache

# Documentation
docs/
*.md
!README.md

# Development
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Tests
tests/
test_*
*_test.py

# Build
build/
dist/
*.egg-info/
"""

        dockerignore = self.project_path / ".dockerignore"
        with open(dockerignore, "w") as f:
            f.write(dockerignore_content)

        return True

    def _fix_requirements_versions(self) -> bool:
        """修复requirements版本"""
        req_file = self.project_path / "requirements.txt"
        if not req_file.exists():
            return False

        # 生成锁定版本
        try:
            result = subprocess.run(
                ["pip", "freeze"],
                check=False,
                capture_output=True,
                text=True,
                timeout=MINUTES_PER_HOUR,
            )
            if result.returncode == 0:
                lock_file = self.project_path / "requirements.lock"
                with open(lock_file, "w") as f:
                    f.write(result.stdout)
                return True
        except subprocess.TimeoutExpired:
            pass

        return False

    def _add_workflow_timeouts(self) -> bool:
        """添加工作流超时设置"""
        workflows_dir = self.project_path / ".github" / "workflows"
        if not workflows_dir.exists():
            return False

        modified = False
        for workflow_file in workflows_dir.glob("*.yml"):
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)

            jobs = workflow.get("jobs", {})
            for _job_name, job_config in jobs.items():
                if "timeout-minutes" not in job_config:
                    job_config["timeout-minutes"] = 30
                    modified = True

            if modified:
                with open(workflow_file, "w") as f:
                    yaml.dump(workflow, f, default_flow_style=False)

        return modified

    def _setup_ai_culture(self) -> bool:
        """设置AI开发文化"""
        try:
            from .auto_setup import setup_ai_culture

            return setup_ai_culture(str(self.project_path))
        except ImportError:
            return False


def run_cicd_health_check(project_path: str = ".") -> dict[str, Any]:
    """运行CI/CD健康检查"""
    guardian = CICDGuardian(project_path)
    return guardian.comprehensive_health_check()


def auto_fix_cicd_issues(project_path: str = ".") -> dict[str, Any]:
    """自动修复CI/CD问题"""
    guardian = CICDGuardian(project_path)
    guardian.comprehensive_health_check()
    return guardian.auto_fix_issues()
