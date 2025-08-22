"""AICultureKit 核心功能模块

包含项目模板生成、质量工具配置和文化规范管理的核心功能。
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml
from git import Repo
from jinja2 import Environment, FileSystemLoader


class CultureConfig:
    """文化配置管理类

    负责加载、管理和提供项目的文化配置信息，包括开发原则、
    质量标准和AI协作规范等。

    Attributes:
        config_path (str): 配置文件路径
        config (Dict[str, Any]): 加载的配置数据

    """

    def __init__(self, config_path: str | None = None) -> None:
        """初始化文化配置管理器

        Args:
            config_path: 配置文件路径，默认为 "aiculture.yaml"

        """
        self.config_path = config_path or "aiculture.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """加载文化配置

        Returns:
            Dict[str, Any]: 配置字典，如果文件不存在则返回默认配置

        """
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """默认文化配置"""
        return {
            "culture": {
                "principles": [
                    "YAGNI - You Aren't Gonna Need It",
                    "KISS - Keep It Simple, Stupid",
                    "SOLID - 面向对象设计原则",
                    "优雅代码，避免过度设计",
                    "AI协作友好的代码风格",
                ],
                "code_style": {
                    "python": {
                        "line_length": 88,
                        "formatter": "black",
                        "linter": ["flake8", "mypy"],
                        "import_sorter": "isort",
                    },
                    "javascript": {"formatter": "prettier", "linter": "eslint"},
                },
                "git_flow": {
                    "main_branch": "main",
                    "feature_prefix": "feature/",
                    "hotfix_prefix": "hotfix/",
                    "commit_format": "conventional",
                },
                "ai_guidelines": {
                    "context_sharing": True,
                    "incremental_development": True,
                    "documentation_first": True,
                },
            },
        }

    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, default_flow_style=False, allow_unicode=True)

    def get_principle(self, key: str) -> Any:
        """获取指定的文化原则"""
        return self.config.get("culture", {}).get(key)


class QualityTools:
    """代码质量工具管理类

    提供代码质量检查工具的统一接口，包括flake8、mypy、pytest等
    工具的配置和执行。

    Attributes:
        project_path (Path): 项目根目录路径

    """

    def __init__(self, project_path: str = ".") -> None:
        """初始化质量工具管理器

        Args:
            project_path: 项目根目录路径，默认为当前目录

        """
        self.project_path = Path(project_path)
        self.templates_path = Path(__file__).parent / "templates"

    def setup_pre_commit(self) -> bool:
        """设置pre-commit配置"""
        try:
            # 复制pre-commit配置
            template_file = self.templates_path / "pre-commit-config.yaml"
            target_file = self.project_path / ".pre-commit-config.yaml"

            if template_file.exists():
                shutil.copy2(template_file, target_file)

                # 安装pre-commit hooks
                subprocess.run(
                    ["pre-commit", "install"],
                    cwd=self.project_path,
                    check=True,
                )
                return True
            return False
        except Exception as e:
            print(f"设置pre-commit失败: {e}")
            return False

    def setup_linting(self, language: str = "python") -> bool:
        """设置代码检查工具"""
        if language == "python":
            return self._setup_python_linting()
        if language == "javascript":
            return self._setup_js_linting()
        return False

    def _setup_python_linting(self) -> bool:
        """设置Python代码检查"""
        try:
            # 创建.flake8配置
            flake8_config = """[flake8]
max-line-length = 88
extend-ignore = E203, W503
max-complexity = 10
exclude =
    .git,
    __pycache__,
    .venv,
    .eggs,
    *.egg,
    build,
    dist
"""
            (self.project_path / ".flake8").write_text(flake8_config)

            # 创建mypy配置已在pyproject.toml中
            return True
        except Exception as e:
            print(f"设置Python linting失败: {e}")
            return False

    def _setup_js_linting(self) -> bool:
        """设置JavaScript代码检查"""
        # 这里可以扩展JavaScript相关配置
        return True

    def run_quality_check(self) -> dict[str, bool]:
        """运行质量检查"""
        results = {}

        try:
            # 运行black格式化检查
            result = subprocess.run(
                ["black", "--check", "."],
                check=False,
                cwd=self.project_path,
                capture_output=True,
            )
            results["black"] = result.returncode == 0
        except FileNotFoundError:
            results["black"] = False

        try:
            # 运行flake8检查
            result = subprocess.run(
                ["flake8", "."],
                check=False,
                cwd=self.project_path,
                capture_output=True,
            )
            results["flake8"] = result.returncode == 0
        except FileNotFoundError:
            results["flake8"] = False

        try:
            # 运行mypy检查
            result = subprocess.run(
                ["mypy", "."],
                check=False,
                cwd=self.project_path,
                capture_output=True,
            )
            results["mypy"] = result.returncode == 0
        except FileNotFoundError:
            results["mypy"] = False

        return results


class ProjectTemplate:
    """项目模板生成类

    负责生成符合AICultureKit标准的项目模板，包括目录结构、
    配置文件和示例代码等。

    Attributes:
        templates_path (Path): 模板文件目录路径

    """

    def __init__(self) -> None:
        """初始化项目模板生成器"""
        self.templates_path = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_path)))

    def create_project(
        self,
        project_name: str,
        target_path: str,
        template_type: str = "python",
    ) -> bool:
        """创建新项目"""
        try:
            target = Path(target_path) / project_name
            target.mkdir(parents=True, exist_ok=True)

            # 基础项目结构
            self._create_basic_structure(target, project_name, template_type)

            # GitHub Actions
            self._create_github_actions(target)

            # 代码质量配置
            quality_tools = QualityTools(str(target))
            quality_tools.setup_pre_commit()
            quality_tools.setup_linting(template_type)

            # 初始化git仓库
            self._init_git_repo(target)

            print(f"✅ 项目 {project_name} 创建成功！路径: {target}")
            return True

        except Exception as e:
            print(f"❌ 项目创建失败: {e}")
            return False

    def _create_basic_structure(
        self,
        target: Path,
        project_name: str,
        template_type: str,
    ) -> None:
        """创建基础项目结构"""
        if template_type == "python":
            self._create_python_structure(target, project_name)
        elif template_type == "javascript":
            self._create_js_structure(target, project_name)

    def _create_python_structure(self, target: Path, project_name: str) -> None:
        """创建Python项目结构"""
        # 创建目录结构
        (target / project_name.replace("-", "_")).mkdir(exist_ok=True)
        (target / "tests").mkdir(exist_ok=True)
        (target / "docs").mkdir(exist_ok=True)
        (target / "scripts").mkdir(exist_ok=True)

        # 创建__init__.py
        init_content = '''"""
{project_name} - AI Culture Kit生成的项目

这是一个遵循AI开发文化最佳实践的项目。
"""

__version__ = "0.1.0"
'''
        (target / project_name.replace("-", "_") / "__init__.py").write_text(
            init_content,
        )

        # 创建主模块文件
        main_content = '''"""
{project_name} 主模块
"""

def main() -> None:
    """主函数"""
    print("Hello from {project_name}!")


if __name__ == "__main__":
    main()
'''
        (target / project_name.replace("-", "_") / "main.py").write_text(main_content)

        # 创建测试文件
        test_content = '''"""
{project_name} 测试模块
"""

import pytest
from {project_name.replace("-", "_")}.main import main


def test_main():
    """测试主函数"""
    # 这里添加你的测试逻辑
    assert True  # 占位测试


def test_import():
    """测试模块导入"""
    import {project_name.replace("-", "_")}
    assert hasattr({project_name.replace("-", "_")}, "__version__")
'''
        (target / "tests" / "test_main.py").write_text(test_content)

        # 创建空的__init__.py用于测试
        (target / "tests" / "__init__.py").write_text("")

    def _create_js_structure(self, target: Path, project_name: str) -> None:
        """创建JavaScript项目结构"""
        # JavaScript项目结构
        (target / "src").mkdir(exist_ok=True)
        (target / "tests").mkdir(exist_ok=True)

        # package.json
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "description": f"{project_name} - AI Culture Kit生成的项目",
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "test": "jest",
                "lint": "eslint src/",
                "format": "prettier --write src/",
            },
        }

        import json

        (target / "package.json").write_text(json.dumps(package_json, indent=2))

    def _create_github_actions(self, target: Path) -> None:
        """创建GitHub Actions工作流"""
        workflows_path = target / ".github" / "workflows"
        workflows_path.mkdir(parents=True, exist_ok=True)

        # CI workflow
        ci_content = self._get_ci_workflow_content()
        (workflows_path / "ci.yml").write_text(ci_content)

        # CD workflow
        cd_content = self._get_cd_workflow_content()
        (workflows_path / "cd.yml").write_text(cd_content)

    def _get_ci_workflow_content(self) -> str:
        """获取CI工作流内容"""
        return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

    - name: Type check with mypy
      run: mypy .

    - name: Format check with black
      run: black --check .

    - name: Import sort check with isort
      run: isort --check-only .

    - name: Security check with bandit
      run: bandit -r . -f json -o bandit-report.json || true

    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""

    def _get_cd_workflow_content(self) -> str:
        """获取CD工作流内容"""
        return """name: CD

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      if: startsWith(github.ref, 'refs/tags/')
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Docker Build and Push
      if: github.ref == 'refs/heads/main'
      run: |
        echo "Docker部署逻辑在这里实现"
        # docker build -t myapp:latest .
        # docker push myapp:latest
"""

    def _init_git_repo(self, target: Path) -> None:
        """初始化git仓库"""
        try:
            repo = Repo.init(str(target))

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
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Coverage
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Secrets
.secrets.baseline
"""
            (target / ".gitignore").write_text(gitignore_content)

            # 添加所有文件并提交
            repo.index.add(["."])
            repo.index.commit("🎉 Initial commit from AICultureKit")

        except Exception as e:
            print(f"⚠️  Git初始化失败: {e}")
