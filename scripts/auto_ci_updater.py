#!/usr/bin/env python3
"""
自动CI配置更新器 - 将防御机制自动集成到CI流程中

这个模块负责：
1. 自动更新CI配置文件（GitHub Actions、Makefile等）
2. 集成新的防御规则到现有工作流
3. 更新项目配置文件（requirements、setup.cfg等）
4. 创建或更新文档说明
5. 验证配置更新的有效性

作者：AI CI Guardian System
版本：v1.0.0
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import click
import yaml


class MakefileUpdater:
    """Makefile更新器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.makefile_path = project_root / "Makefile"

    def add_defense_targets(self, defenses: Dict[str, List[str]]) -> bool:
        """向Makefile添加防御机制相关的目标"""
        if not self.makefile_path.exists():
            click.echo("⚠️ Makefile不存在，跳过更新")
            return False

        try:
            with open(self.makefile_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否已经有防御相关的目标
            if "validate-defenses" in content:
                click.echo("ℹ️ Makefile已包含防御验证目标")
                return True

            # 添加新的防御验证目标
            defense_targets = self._generate_defense_targets(defenses)

            # 在合适位置插入新目标（通常在帮助信息之后）
            help_section_end = content.find("\n# -------")
            if help_section_end != -1:
                insert_pos = content.find("\n\n", help_section_end)
                if insert_pos != -1:
                    new_content = (
                        content[:insert_pos]
                        + "\n"
                        + defense_targets
                        + content[insert_pos:]
                    )
                else:
                    new_content = content + "\n" + defense_targets
            else:
                new_content = content + "\n" + defense_targets

            # 备份原文件
            backup_path = self.makefile_path.with_suffix(".bak")
            shutil.copy2(self.makefile_path, backup_path)

            # 写入更新后的内容
            with open(self.makefile_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            click.echo("✅ Makefile已更新，添加了防御验证目标")
            return True

        except Exception as e:
            click.echo(f"❌ 更新Makefile失败: {e}")
            return False

    def _generate_defense_targets(self, defenses: Dict[str, List[str]]) -> str:
        """生成防御机制相关的Makefile目标"""
        targets = f"""
# -------------------------------
# 🛡️ CI防御机制验证
# 自动生成时间: {datetime.now().isoformat()}
# -------------------------------

.PHONY: validate-defenses
validate-defenses: ## 验证所有防御机制
	@echo "$(BLUE)>>> 验证防御机制...$(RESET)"
	@if $(ACTIVATE) && python scripts/ci_guardian.py --validate; then \\
		echo "$(GREEN)✅ 防御机制验证通过$(RESET)"; \\
	else \\
		echo "$(RED)❌ 防御机制验证失败$(RESET)"; \\
		exit 1; \\
	fi

.PHONY: run-validation-tests
run-validation-tests: ## 运行增强验证测试
	@echo "$(BLUE)>>> 运行验证测试...$(RESET)"
	$(ACTIVATE) && pytest tests/test_*_validation.py -v

.PHONY: check-defense-coverage
check-defense-coverage: ## 检查防御覆盖率
	@echo "$(BLUE)>>> 检查防御覆盖率...$(RESET)"
	@if $(ACTIVATE) && python scripts/ci_issue_analyzer.py -s; then \\
		echo "$(GREEN)✅ 防御覆盖率检查完成$(RESET)"; \\
	else \\
		echo "$(RED)❌ 防御覆盖率检查失败$(RESET)"; \\
		exit 1; \\
	fi

.PHONY: update-defenses
update-defenses: ## 更新防御机制
	@echo "$(BLUE)>>> 更新防御机制...$(RESET)"
	$(ACTIVATE) && python scripts/defense_generator.py -i logs/ci_issues.json -s

.PHONY: ci-guardian
ci-guardian: ## 运行完整CI守护检查
	@echo "$(BLUE)>>> 运行CI守护检查...$(RESET)"
	$(ACTIVATE) && python scripts/ci_guardian.py -c "make quality" -s
"""

        # 如果有测试文件，添加特定的测试目标
        if defenses.get("test_files"):
            targets += """
.PHONY: test-imports
test-imports: ## 运行导入验证测试
	$(ACTIVATE) && pytest tests/test_import_validation.py -v

.PHONY: test-types
test-types: ## 运行类型验证测试
	$(ACTIVATE) && pytest tests/test_type_validation.py -v

.PHONY: test-security
test-security: ## 运行安全验证测试
	$(ACTIVATE) && pytest tests/test_security_validation.py -v
"""

        return targets


class GitHubActionsUpdater:
    """GitHub Actions工作流更新器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"

    def integrate_defense_checks(self, defenses: Dict[str, List[str]]) -> bool:
        """将防御检查集成到现有CI工作流"""
        ci_workflow_path = self.workflows_dir / "ci.yml"

        if not ci_workflow_path.exists():
            click.echo("⚠️ CI工作流文件不存在，创建新的工作流")
            return self._create_new_workflow(defenses)

        try:
            with open(ci_workflow_path, "r", encoding="utf-8") as f:
                workflow = yaml.safe_load(f)

            # 检查是否已经有防御检查
            for job in workflow.get("jobs", {}).values():
                for step in job.get("steps", []):
                    if "Defense validation" in step.get("name", ""):
                        click.echo("ℹ️ CI工作流已包含防御验证步骤")
                        return True

            # 添加防御验证步骤到quality-check作业
            if "quality-check" in workflow.get("jobs", {}):
                quality_job = workflow["jobs"]["quality-check"]

                # 添加防御验证步骤
                defense_steps = self._generate_defense_steps(defenses)
                quality_job["steps"].extend(defense_steps)

                # 备份原文件
                backup_path = ci_workflow_path.with_suffix(".bak")
                shutil.copy2(ci_workflow_path, backup_path)

                # 写入更新后的工作流
                with open(ci_workflow_path, "w", encoding="utf-8") as f:
                    yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

                click.echo("✅ GitHub Actions工作流已更新")
                return True
            else:
                click.echo("⚠️ 未找到quality-check作业，创建新的防御作业")
                return self._add_defense_job(workflow, ci_workflow_path, defenses)

        except Exception as e:
            click.echo(f"❌ 更新GitHub Actions工作流失败: {e}")
            return False

    def _generate_defense_steps(self, defenses: Dict[str, List[str]]) -> List[Dict]:
        """生成防御验证步骤"""
        steps = []

        # 基础防御验证步骤
        steps.append(
            {
                "name": "Defense validation",
                "run": "python scripts/ci_guardian.py --validate",
            }
        )

        # 如果有验证测试，添加测试步骤
        if defenses.get("test_files"):
            steps.append(
                {
                    "name": "Run validation tests",
                    "run": "pytest tests/test_*_validation.py -v --tb=short",
                }
            )

        # 如果有pre-commit钩子，验证钩子配置
        if defenses.get("pre_commit_hooks"):
            steps.append(
                {
                    "name": "Validate pre-commit hooks",
                    "run": "pre-commit run --all-files",
                }
            )

        # 防御覆盖率检查
        steps.append(
            {
                "name": "Defense coverage check",
                "run": "python scripts/ci_issue_analyzer.py -s",
            }
        )

        return steps

    def _add_defense_job(
        self, workflow: Dict, workflow_path: Path, defenses: Dict[str, List[str]]
    ) -> bool:
        """添加新的防御作业"""
        defense_job = {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"name": "Checkout代码", "uses": "actions/checkout@v4"},
                {
                    "name": "设置Python环境",
                    "uses": "actions/setup-python@v4",
                    "with": {"python-version": "3.11"},
                },
                {
                    "name": "安装依赖",
                    "run": "pip install -r requirements.txt -r requirements-dev.txt",
                },
            ],
        }

        # 添加防御验证步骤
        defense_steps = self._generate_defense_steps(defenses)
        defense_job["steps"].extend(defense_steps)

        # 添加新作业
        workflow["jobs"]["defense-validation"] = defense_job

        try:
            with open(workflow_path, "w", encoding="utf-8") as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

            click.echo("✅ 已添加防御验证作业到CI工作流")
            return True
        except Exception as e:
            click.echo(f"❌ 添加防御作业失败: {e}")
            return False

    def _create_new_workflow(self, defenses: Dict[str, List[str]]) -> bool:
        """创建新的防御验证工作流"""
        workflow_path = self.workflows_dir / "defense-validation.yml"

        workflow = {
            "name": "Defense Validation",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main", "develop"]},
                "schedule": [{"cron": "0 2 * * *"}],  # 每天凌晨2点运行
            },
            "jobs": {
                "validate-defenses": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout代码", "uses": "actions/checkout@v4"},
                        {
                            "name": "设置Python环境",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.11"},
                        },
                        {
                            "name": "安装依赖",
                            "run": "pip install -r requirements.txt -r requirements-dev.txt",
                        },
                    ],
                }
            },
        }

        # 添加防御验证步骤
        defense_steps = self._generate_defense_steps(defenses)
        workflow["jobs"]["validate-defenses"]["steps"].extend(defense_steps)

        try:
            self.workflows_dir.mkdir(parents=True, exist_ok=True)

            with open(workflow_path, "w", encoding="utf-8") as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

            click.echo("✅ 已创建新的防御验证工作流")
            return True
        except Exception as e:
            click.echo(f"❌ 创建防御验证工作流失败: {e}")
            return False


class RequirementsUpdater:
    """依赖需求更新器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.req_dev_path = project_root / "requirements-dev.txt"

    def update_dev_requirements(self, defenses: Dict[str, List[str]]) -> bool:
        """更新开发依赖文件"""
        if not self.req_dev_path.exists():
            click.echo("⚠️ requirements-dev.txt不存在，创建新文件")
            self._create_dev_requirements()

        try:
            with open(self.req_dev_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否需要添加新的依赖
            new_packages = []

            # 如果有pre-commit钩子，确保pre-commit包存在
            if defenses.get("pre_commit_hooks") and "pre-commit" not in content:
                new_packages.append("pre-commit>=3.0.0")

            # 如果有安全检查，确保bandit包存在
            if (
                any("security" in str(files) for files in defenses.values())
                and "bandit" not in content
            ):
                new_packages.append("bandit[toml]>=1.7.0")

            # 如果有增强配置，确保相关包存在
            yaml_packages = ["PyYAML>=6.0", "ruamel.yaml>=0.17.0"]
            for pkg in yaml_packages:
                pkg_name = pkg.split(">=")[0]
                if pkg_name not in content:
                    new_packages.append(pkg)

            if new_packages:
                # 添加注释说明
                comment = f"\n# CI Defense packages - auto-added {datetime.now().isoformat()[:10]}\n"
                new_content = content + comment + "\n".join(new_packages) + "\n"

                # 备份原文件
                backup_path = self.req_dev_path.with_suffix(".bak")
                shutil.copy2(self.req_dev_path, backup_path)

                # 写入更新后的内容
                with open(self.req_dev_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                click.echo(f"✅ requirements-dev.txt已更新，添加了{len(new_packages)}个包")
                return True
            else:
                click.echo("ℹ️ requirements-dev.txt无需更新")
                return True

        except Exception as e:
            click.echo(f"❌ 更新requirements-dev.txt失败: {e}")
            return False

    def _create_dev_requirements(self):
        """创建基础的开发依赖文件"""
        basic_content = """# Development dependencies
pytest>=7.0.0
coverage>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
ruff>=0.1.0
bandit[toml]>=1.7.0
pre-commit>=3.0.0
PyYAML>=6.0
click>=8.0.0
"""

        with open(self.req_dev_path, "w", encoding="utf-8") as f:
            f.write(basic_content)

        click.echo("✅ 已创建基础的requirements-dev.txt文件")


class ConfigurationUpdater:
    """项目配置更新器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def update_setup_cfg(self, defenses: Dict[str, List[str]]) -> bool:
        """更新setup.cfg配置"""
        setup_cfg_path = self.project_root / "setup.cfg"

        if not setup_cfg_path.exists():
            click.echo("ℹ️ setup.cfg不存在，跳过更新")
            return True

        try:
            with open(setup_cfg_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否需要添加新的配置段
            additions = []

            # 如果有测试文件，添加pytest配置
            if defenses.get("test_files") and "[tool:pytest]" not in content:
                additions.append(
                    """
# Enhanced pytest configuration - auto-added
[tool:pytest]
testpaths = tests
python_files = test_*.py test_*_validation.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    validation: marks tests as validation tests
"""
                )

            # 如果有覆盖率配置需求
            if defenses.get("test_files") and "[coverage:" not in content:
                additions.append(
                    """
# Enhanced coverage configuration - auto-added
[coverage:run]
source = src
omit = 
    */tests/*
    */test_*
    */venv/*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
show_missing = True
fail_under = 80
"""
                )

            if additions:
                new_content = content + "\n".join(additions)

                # 备份原文件
                backup_path = setup_cfg_path.with_suffix(".bak")
                shutil.copy2(setup_cfg_path, backup_path)

                # 写入更新后的内容
                with open(setup_cfg_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                click.echo("✅ setup.cfg已更新")
                return True
            else:
                click.echo("ℹ️ setup.cfg无需更新")
                return True

        except Exception as e:
            click.echo(f"❌ 更新setup.cfg失败: {e}")
            return False

    def update_gitignore(self, defenses: Dict[str, List[str]]) -> bool:
        """更新.gitignore文件"""
        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            click.echo("⚠️ .gitignore不存在，创建基础版本")
            self._create_basic_gitignore()

        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 需要添加的忽略规则
            ignore_rules = []

            # 测试和覆盖率相关
            if defenses.get("test_files"):
                test_ignores = [
                    "# Test artifacts",
                    ".pytest_cache/",
                    ".coverage",
                    "htmlcov/",
                    "coverage.xml",
                    "*.cover",
                ]
                ignore_rules.extend(
                    [rule for rule in test_ignores if rule not in content]
                )

            # 备份文件
            backup_ignores = ["# Backup files", "*.bak", "*.backup"]
            ignore_rules.extend(
                [rule for rule in backup_ignores if rule not in content]
            )

            # pre-commit相关
            if defenses.get("pre_commit_hooks"):
                precommit_ignores = ["# Pre-commit", ".pre-commit-cache/"]
                ignore_rules.extend(
                    [rule for rule in precommit_ignores if rule not in content]
                )

            if ignore_rules:
                new_content = content + "\n\n" + "\n".join(ignore_rules) + "\n"

                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                click.echo("✅ .gitignore已更新")
                return True
            else:
                click.echo("ℹ️ .gitignore无需更新")
                return True

        except Exception as e:
            click.echo(f"❌ 更新.gitignore失败: {e}")
            return False

    def _create_basic_gitignore(self):
        """创建基础的.gitignore文件"""
        basic_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
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

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

        with open(self.project_root / ".gitignore", "w", encoding="utf-8") as f:
            f.write(basic_content)

        click.echo("✅ 已创建基础的.gitignore文件")


class DocumentationUpdater:
    """文档更新器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def create_defense_documentation(self, defenses: Dict[str, List[str]]) -> bool:
        """创建防御机制说明文档"""
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(exist_ok=True)

        doc_path = docs_dir / "ci_defense_mechanisms.md"

        doc_content = f"""# CI防御机制说明

> 此文档由CI Guardian系统自动生成  
> 生成时间: {datetime.now().isoformat()}

## 概述

本项目已部署智能CI防御机制，能够自动检测CI问题并生成相应的防护措施，确保同类问题不再发生。

## 防御机制组件

### 1. 验证测试 ({len(defenses.get("test_files", []))} 个文件)

{self._generate_test_docs(defenses.get("test_files", []))}

### 2. Lint配置 ({len(defenses.get("lint_configs", []))} 个文件)

{self._generate_config_docs(defenses.get("lint_configs", []))}

### 3. Pre-commit钩子

{self._generate_precommit_docs(defenses.get("pre_commit_hooks", []))}

### 4. CI工作流增强

{self._generate_workflow_docs(defenses.get("ci_workflows", []))}

## 使用方法

### 本地验证
```bash
# 运行所有防御验证
make validate-defenses

# 运行特定类型的验证测试
make run-validation-tests

# 检查防御覆盖率
make check-defense-coverage
```

### CI集成

防御机制已自动集成到CI流程中，每次提交都会运行相应的验证。

### 手动更新防御机制
```bash
# 分析最新的CI问题
python scripts/ci_issue_analyzer.py -l logs/quality_check.json -s

# 生成新的防御机制
python scripts/defense_generator.py -i logs/ci_issues.json -s

# 运行CI守护者进行完整检查
python scripts/ci_guardian.py -c "make quality" -s
```

## 防御机制说明

### 导入验证测试
- **目的**: 防止模块导入错误
- **检查内容**: 核心模块导入、依赖可用性、循环导入检测
- **触发条件**: 检测到ImportError或ModuleNotFoundError

### 类型验证测试
- **目的**: 确保类型注解正确性
- **检查内容**: 函数类型注解、类方法注解、返回类型一致性
- **触发条件**: 检测到MyPy类型错误

### 断言验证测试
- **目的**: 防止测试断言失败
- **检查内容**: 基础断言、空值安全、边界条件
- **触发条件**: 检测到Pytest断言失败

### 代码风格验证测试
- **目的**: 确保代码风格一致性
- **检查内容**: Ruff格式检查、行长度、import排序
- **触发条件**: 检测到代码风格问题

### 安全验证测试
- **目的**: 防止安全漏洞
- **检查内容**: Bandit扫描、硬编码密钥检测、SQL注入防护
- **触发条件**: 检测到安全问题

## 维护指南

### 定期检查
- 每周运行 `make ci-guardian` 进行全面检查
- 关注CI失败日志，及时生成新的防御机制
- 定期更新防御规则以适应项目变化

### 问题排查
- 查看 `logs/ci_issues.json` 了解历史问题
- 查看 `logs/defenses_generated.json` 了解已生成的防御措施
- 运行 `python scripts/ci_issue_analyzer.py -s` 获取问题分析报告

### 自定义配置
- 编辑相应的配置文件调整检查规则
- 修改测试文件添加特定的验证逻辑
- 更新CI工作流添加新的检查步骤

---

*此防御机制由AI CI Guardian系统维护，确保项目代码质量和稳定性。*
"""

        try:
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(doc_content)

            click.echo("✅ 已创建防御机制说明文档")
            return True
        except Exception as e:
            click.echo(f"❌ 创建文档失败: {e}")
            return False

    def _generate_test_docs(self, test_files: List[str]) -> str:
        """生成测试文档部分"""
        if not test_files:
            return "暂无验证测试文件。"

        docs = []
        for test_file in test_files:
            test_type = test_file.replace("test_", "").replace("_validation.py", "")
            docs.append(f"- `{test_file}`: {test_type} 验证测试")

        return "\n".join(docs)

    def _generate_config_docs(self, config_files: List[str]) -> str:
        """生成配置文档部分"""
        if not config_files:
            return "暂无增强配置文件。"

        docs = []
        for config_file in config_files:
            if "pyproject.toml" in config_file:
                docs.append("- `pyproject.toml`: 增强的Ruff配置")
            elif "mypy.ini" in config_file:
                docs.append("- `mypy.ini`: 严格的MyPy类型检查配置")
            elif ".bandit" in config_file:
                docs.append("- `.bandit`: 安全扫描配置")
            else:
                docs.append(f"- `{config_file}`: 配置文件")

        return "\n".join(docs)

    def _generate_precommit_docs(self, precommit_files: List[str]) -> str:
        """生成pre-commit文档部分"""
        if not precommit_files:
            return "暂无pre-commit钩子配置。"

        return """已配置pre-commit钩子，包括：
- 代码格式检查和自动修复
- 类型检查
- 安全扫描
- 基础代码质量检查

安装方法：
```bash
pre-commit install
```"""

    def _generate_workflow_docs(self, workflow_files: List[str]) -> str:
        """生成工作流文档部分"""
        if not workflow_files:
            return "暂无CI工作流增强。"

        docs = []
        for workflow_file in workflow_files:
            docs.append(f"- `{workflow_file}`: 增强的CI检查工作流")

        return "\n".join(docs)


class AutoCIUpdater:
    """自动CI配置更新器主控制器"""

    def __init__(self, project_root: Path = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

        self.makefile_updater = MakefileUpdater(self.project_root)
        self.github_updater = GitHubActionsUpdater(self.project_root)
        self.requirements_updater = RequirementsUpdater(self.project_root)
        self.config_updater = ConfigurationUpdater(self.project_root)
        self.docs_updater = DocumentationUpdater(self.project_root)

        self.update_results = []

    def integrate_defenses(self, defenses: Dict[str, List[str]]) -> bool:
        """集成所有防御机制到项目配置中"""
        click.echo("🔧 开始集成防御机制到项目配置...")

        success_count = 0
        total_updates = 6

        # 1. 更新Makefile
        if self.makefile_updater.add_defense_targets(defenses):
            success_count += 1
            self.update_results.append("✅ Makefile")
        else:
            self.update_results.append("❌ Makefile")

        # 2. 更新GitHub Actions
        if self.github_updater.integrate_defense_checks(defenses):
            success_count += 1
            self.update_results.append("✅ GitHub Actions")
        else:
            self.update_results.append("❌ GitHub Actions")

        # 3. 更新依赖文件
        if self.requirements_updater.update_dev_requirements(defenses):
            success_count += 1
            self.update_results.append("✅ Requirements")
        else:
            self.update_results.append("❌ Requirements")

        # 4. 更新setup.cfg
        if self.config_updater.update_setup_cfg(defenses):
            success_count += 1
            self.update_results.append("✅ Setup.cfg")
        else:
            self.update_results.append("❌ Setup.cfg")

        # 5. 更新.gitignore
        if self.config_updater.update_gitignore(defenses):
            success_count += 1
            self.update_results.append("✅ Gitignore")
        else:
            self.update_results.append("❌ Gitignore")

        # 6. 创建文档
        if self.docs_updater.create_defense_documentation(defenses):
            success_count += 1
            self.update_results.append("✅ Documentation")
        else:
            self.update_results.append("❌ Documentation")

        success_rate = (success_count / total_updates) * 100
        click.echo(f"\n📊 集成结果: {success_count}/{total_updates} ({success_rate:.1f}%)")

        return success_count >= total_updates * 0.8  # 80%成功率认为集成成功

    def validate_integration(self) -> bool:
        """验证集成的有效性"""
        click.echo("🔍 验证防御机制集成...")

        validation_commands = [
            ("make validate-defenses", "Makefile目标验证"),
            ("python scripts/ci_guardian.py --validate", "CI守护者验证"),
            ("python scripts/ci_issue_analyzer.py -s", "问题分析器验证"),
        ]

        success_count = 0
        for cmd, description in validation_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=30,
                )

                if result.returncode == 0:
                    click.echo(f"✅ {description}")
                    success_count += 1
                else:
                    click.echo(f"❌ {description}: {result.stderr[:100]}")
            except subprocess.TimeoutExpired:
                click.echo(f"⏱️ {description}: 超时")
            except Exception as e:
                click.echo(f"❌ {description}: {e}")

        validation_rate = (success_count / len(validation_commands)) * 100
        click.echo(
            f"\n📊 验证结果: {success_count}/{len(validation_commands)} ({validation_rate:.1f}%)"
        )

        return success_count >= len(validation_commands) * 0.7  # 70%成功率认为验证通过

    def generate_integration_report(self, defenses: Dict[str, List[str]]) -> str:
        """生成集成报告"""
        report = f"""# CI防御机制集成报告

**生成时间**: {datetime.now().isoformat()}
**项目路径**: {self.project_root}

## 集成摘要

### 防御机制统计
- 测试文件: {len(defenses.get("test_files", []))} 个
- 配置文件: {len(defenses.get("lint_configs", []))} 个  
- Pre-commit钩子: {len(defenses.get("pre_commit_hooks", []))} 个
- CI工作流: {len(defenses.get("ci_workflows", []))} 个

### 更新结果
{chr(10).join(self.update_results)}

## 生成的文件

### 测试文件
{chr(10).join(f"- {f}" for f in defenses.get("test_files", []))}

### 配置文件  
{chr(10).join(f"- {f}" for f in defenses.get("lint_configs", []))}

### 工作流文件
{chr(10).join(f"- {f}" for f in defenses.get("ci_workflows", []))}

## 使用说明

### 验证防御机制
```bash
make validate-defenses
```

### 运行验证测试
```bash
make run-validation-tests
```

### 检查防御覆盖率
```bash
make check-defense-coverage
```

### 手动触发CI守护者
```bash
python scripts/ci_guardian.py -c "make quality" -s
```

---
*此报告由AI CI Guardian系统自动生成*
"""

        # 保存报告
        report_path = self.project_root / "logs" / "integration_report.md"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            click.echo(f"📄 集成报告已保存到: {report_path}")
        except Exception as e:
            click.echo(f"⚠️ 保存集成报告失败: {e}")

        return report


@click.command()
@click.option("--defenses-file", "-d", help="防御机制JSON文件路径")
@click.option("--project-root", "-p", help="项目根目录路径")
@click.option("--validate-only", "-v", is_flag=True, help="仅验证现有集成")
@click.option("--makefile-only", "-m", is_flag=True, help="仅更新Makefile")
@click.option("--github-only", "-g", is_flag=True, help="仅更新GitHub Actions")
@click.option("--docs-only", "-doc", is_flag=True, help="仅更新文档")
@click.option("--summary", "-s", is_flag=True, help="显示集成摘要")
def main(
    defenses_file,
    project_root,
    validate_only,
    makefile_only,
    github_only,
    docs_only,
    summary,
):
    """
    🔧 自动CI配置更新器

    将防御机制自动集成到CI流程和项目配置中。

    Examples:
        auto_ci_updater.py -d logs/defenses_generated.json
        auto_ci_updater.py -v  # 仅验证
        auto_ci_updater.py -m  # 仅更新Makefile
        auto_ci_updater.py -s  # 显示摘要
    """

    project_path = Path(project_root) if project_root else Path.cwd()
    updater = AutoCIUpdater(project_path)

    click.echo("🔧 自动CI配置更新器启动")

    if validate_only:
        # 仅验证现有集成
        if updater.validate_integration():
            click.echo("✅ 防御机制集成验证通过")
        else:
            click.echo("❌ 防御机制集成验证失败")
        return

    # 读取防御机制文件
    if not defenses_file:
        defenses_file = project_path / "logs" / "defenses_generated.json"

    defenses_path = Path(defenses_file)
    if not defenses_path.exists():
        click.echo(f"❌ 防御机制文件不存在: {defenses_file}")
        return

    try:
        with open(defenses_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            defenses = data.get("defenses", {})
    except Exception as e:
        click.echo(f"❌ 读取防御机制文件失败: {e}")
        return

    click.echo("📋 从文件中读取到防御机制配置")

    # 根据选项执行特定更新
    if makefile_only:
        updater.makefile_updater.add_defense_targets(defenses)
    elif github_only:
        updater.github_updater.integrate_defense_checks(defenses)
    elif docs_only:
        updater.docs_updater.create_defense_documentation(defenses)
    else:
        # 执行完整集成
        if updater.integrate_defenses(defenses):
            click.echo("✅ 防御机制集成成功")

            # 验证集成
            if updater.validate_integration():
                click.echo("✅ 集成验证通过")
            else:
                click.echo("⚠️ 集成验证部分失败，请检查配置")
        else:
            click.echo("❌ 防御机制集成失败")

    # 生成报告
    if summary:
        report = updater.generate_integration_report(defenses)
        click.echo("\n📊 集成摘要:")
        click.echo(report[:500] + "..." if len(report) > 500 else report)


if __name__ == "__main__":
    main()
